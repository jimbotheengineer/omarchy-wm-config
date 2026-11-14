#!/usr/bin/env python3
"""Local, mutually exclusive vLLM/NInfer controls for the Noctalia bar."""
import argparse
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

HOME = (Path.home() / 'llm/control')
STATE = HOME / 'selection.json'
LOCK = HOME / 'operation.lock'
PI_MODELS = (Path.home() / '.pi/agent/models.json')
NINFER = (Path.home() / 'ninfer')
NINFER_ALL = (Path.home() / 'ninfer-all')
SHARP = (Path.home() / 'llm/vllm/models/nvidia/Qwen3.8-27B-NVFP4/chat_template.jinja')
SERVICES = {'vllm': 'vllm-local.service', 'ninfer': 'ninfer-local.service'}
CONTEXT_MIN = 4096
CONTEXT_MAX = 1048576
CONTEXT_STEP = 256
NINFER_TEMPLATES = {
    'sharp': {'label': 'Sharp v22.5.0', 'path': str(SHARP)},
    'native': {'label': 'NInfer built-in', 'path': None},
}
NINFER_MODELS = {
    'qwen38-nvfp4': {
        'label': 'Qwen3.8 27B NVFP4 • NInfer', 'root': NINFER,
        'file': 'qwen3_8_27b_nvfp4.ninfer', 'verified': True,
        # Approximate MTP weight residency from NInfer's 27B performance profile.
        'vram': {'weights_gib': {'off': 19.7}, 'kv_bytes_per_token': 33024,
                 'mtp_kv_ratio': 1.063, 'other_gib': {'off': 2.0}},
    },
    'qwen38-gsq-iq3s': {
        'label': 'Qwen3.8 27B GSQ-RCO IQ3_S • NInfer-all', 'root': NINFER_ALL,
        'file': 'Qwen3.8-27B-GSQ-RCO-IQ3_S-ninfer-v3.ninfer',
        'size': 15017456896, 'verified': True,
        # Calibrated to this machine's startup logs at 115,200 tokens.
        'vram': {'weights_gib': {'off': 11.6, 'on': 11.9},
                 'kv_bytes_per_token': 26112, 'mtp_kv_ratio': 1.063,
                 'other_gib': {'off': 1.94, 'on': 2.54}},
    },
}
DEFAULT = {'engine': 'vllm', 'ninfer_model': 'qwen38-nvfp4',
           'ninfer_template': 'sharp', 'ninfer_vision': 'off',
           'ninfer_context': 115200}
spec = importlib.util.spec_from_file_location('vllm_selection', str(Path.home() / 'llm/vllm/model-selection.py'))
vllm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vllm)


def load():
    value = json.loads(STATE.read_text()) if STATE.exists() else DEFAULT.copy()
    if (isinstance(value, dict) and {'engine', 'ninfer_template'} <= set(value)
            and set(value) <= set(DEFAULT)):
        value = {**DEFAULT, **value}
    if (not isinstance(value, dict) or set(value) != set(DEFAULT)
            or value['engine'] not in SERVICES or value['ninfer_model'] not in NINFER_MODELS
            or value['ninfer_template'] not in NINFER_TEMPLATES
            or value['ninfer_vision'] not in ('on', 'off')
            or type(value['ninfer_context']) is not int
            or not CONTEXT_MIN <= value['ninfer_context'] <= CONTEXT_MAX
            or value['ninfer_context'] % CONTEXT_STEP != 0
            or (value['ninfer_model'] != 'qwen38-gsq-iq3s' and value['ninfer_vision'] == 'on')):
        raise ValueError('Invalid inference-server selection')
    return value


def save(value):
    HOME.mkdir(parents=True, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix='.selection-', dir=HOME)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(path, STATE)
    finally:
        if os.path.exists(path): os.unlink(path)


def pi_model_update(choice):
    """Prepare Pi's local-llm entry for the server that will be started."""
    if not PI_MODELS.is_file(): return None
    data = json.loads(PI_MODELS.read_text())
    models = data['providers']['vllm']['models']
    model = next(item for item in models if item.get('id') == 'local-llm')
    if choice['engine'] == 'ninfer':
        model['contextWindow'] = choice['context']
        model['input'] = ['text', 'image'] if choice['vision'] == 'on' else ['text']
    else:
        model['contextWindow'] = 32768 if choice['model'] == 'qwen-gguf' else 115200
        model['input'] = ['text'] if choice['model'] == 'qwen-gguf' else ['text', 'image']
    return data


def save_pi_model(data):
    if data is None: return
    fd, path = tempfile.mkstemp(prefix='.models-', dir=PI_MODELS.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.chmod(path, PI_MODELS.stat().st_mode & 0o777)
        os.replace(path, PI_MODELS)
    finally:
        if os.path.exists(path): os.unlink(path)


def profiles():
    old = vllm.available()
    models = [{'id': key, 'label': model['label'], 'verified': model['verified'],
        'templates': [{'id': key, 'label': template['label']} for key, template in model['templates'].items()
                      if Path(template['path']).is_file()]} for key, model in old.items()]
    ninfer_models = []
    for key, item in NINFER_MODELS.items():
        root = item['root']
        artifact = root/'models'/item['file']
        if (not (root/'build/apps/ninfer-serve').is_file() or not artifact.is_file()
                or ('size' in item and artifact.stat().st_size != item['size'])):
            continue
        templates = ('native', 'sharp') if key == 'qwen38-gsq-iq3s' else ('sharp', 'native')
        ninfer_models.append({'id': key, 'label': item['label'], 'verified': item['verified'],
            'vision': key == 'qwen38-gsq-iq3s',
            'vram': item.get('vram'),
            'templates': [{'id': name, 'label': template['label'] +
                          (' (untested)' if key == 'qwen38-gsq-iq3s' and name == 'sharp' else '')}
                          for name in templates for template in [NINFER_TEMPLATES[name]]
                          if template['path'] is None or Path(template['path']).is_file()]})
    return {'vllm': models, 'ninfer': ninfer_models}


def selected(engine=None):
    value = load(); engine = engine or value['engine']
    choice = vllm.load() if engine == 'vllm' else {
        'model':value['ninfer_model'],'template':value['ninfer_template'],
        'vision':value['ninfer_vision'],'context':value['ninfer_context']}
    return {'engine':engine, **choice}


def choose(engine, model, template, vision='off', context=None):
    if engine not in SERVICES: raise ValueError('Unknown engine')
    profile = next((p for p in profiles()[engine] if p['id']==model), None)
    if (profile is None or template not in {t['id'] for t in profile['templates']}
            or vision not in ('on', 'off') or (vision == 'on' and not profile.get('vision'))):
        raise ValueError('Unavailable model/template selection')
    value = load()
    if engine == 'vllm': vllm.save({'model':model,'template':template})
    else:
        if context is None: context = value['ninfer_context']
        if (type(context) is not int or not CONTEXT_MIN <= context <= CONTEXT_MAX
                or context % CONTEXT_STEP != 0):
            raise ValueError(f'Context must be {CONTEXT_MIN}–{CONTEXT_MAX} tokens in {CONTEXT_STEP}-token steps')
        value['ninfer_model'] = model
        value['ninfer_template'] = template
        value['ninfer_vision'] = vision
        value['ninfer_context'] = context
    value['engine'] = engine
    save(value)
    return selected()


def systemctl(*args):
    return subprocess.run(['systemctl','--user',*args],check=True,text=True,capture_output=True,timeout=120).stdout


def service_status(engine):
    values = systemctl('show',SERVICES[engine],'-p','ActiveState','-p','SubState','-p','MainPID')
    info = dict(line.split('=',1) for line in values.splitlines() if '=' in line)
    active = info.get('ActiveState','inactive'); args=[]
    pid = info.get('MainPID','0')
    if pid.isdigit() and int(pid)>0:
        try: args=[v.decode() for v in Path('/proc',pid,'cmdline').read_bytes().split(b'\0') if v]
        except (FileNotFoundError,ProcessLookupError): pass
    state = {'inactive':'off','failed':'failed','activating':'loading','deactivating':'stopping'}.get(active,'off')
    if active == 'active':
        state = 'loading'
        try:
            # Check identity too: a healthy endpoint from the other engine is not readiness.
            with urllib.request.urlopen('http://127.0.0.1:8000/metrics',timeout=1) as r:
                text=r.read().decode()
            signature='ninfer_engine_ready 1' if engine=='ninfer' else 'vllm:num_requests_running'
            if signature in text: state='ready'
            elif engine=='ninfer' and 'ninfer_engine_ready 0' in text:
                # An engine-wide failure keeps HTTP/metrics alive but /health
                # returns 503. Show retryable failure, not endless startup.
                state='failed'
            elif engine=='ninfer':
                # NInfer-all exposes llama.cpp-style metrics. Its health response
                # identifies the engine and distinguishes ready from still loading.
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=1) as r:
                        if r.headers.get('X-NInfer-Version') and json.load(r).get('status') == 'ok':
                            state='ready'
                except urllib.error.HTTPError as exc:
                    if exc.code == 503: state='failed'
        except (OSError,urllib.error.URLError): pass
    return {'engine':engine,'state':state,'args':args}


def applied(info):
    choice=selected(info['engine']);args=info['args']
    if not args: return False
    if info['engine']=='vllm':
        model,template=vllm.validate({'model':choice['model'],'template':choice['template']})
        return model['path'] in args and str(template) in args
    path=NINFER_TEMPLATES[choice['template']]['path']
    model = NINFER_MODELS[choice['model']]
    return (str(model['root']/'models'/model['file']) in args
            and (('--vision' in args) == (choice['vision'] == 'on'))
            and '--max-context' in args and args[args.index('--max-context')+1] == str(choice['context'])
            and '--kv-capacity' in args and args[args.index('--kv-capacity')+1] == str(choice['context'])
            and ((path in args) if path else '--chat-template' not in args))


def benchmark_busy():
    # The comparison harness owns GPU transitions until it has restored vLLM.
    for p in Path('/proc').iterdir():
        if not p.name.isdigit(): continue
        try: args=(p/'cmdline').read_bytes().split(b'\0')
        except (OSError,ProcessLookupError): continue
        if any(a.startswith(str(Path.home() / 'ninfer/bench-results').encode() + b'/') and a.endswith(b'/benchmark.py') for a in args):
            return True
    return False


def operation_busy():
    HOME.mkdir(parents=True,exist_ok=True)
    with LOCK.open('a') as f:
        try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: return True
    return False


def status():
    services={engine:service_status(engine) for engine in SERVICES}
    active=[e for e,info in services.items() if info['state'] in ('ready','loading','stopping')]
    engine=active[0] if active else load()['engine']
    if len(active)>1: raise RuntimeError('Both inference services are active; stop one')
    info=services[engine]
    active_model = None
    if active and engine == 'ninfer':
        for key, profile in NINFER_MODELS.items():
            if str(profile['root']/'models'/profile['file']) in info['args']:
                active_model = profile['label']
                break
    return {'selected':selected(),'active_engine':active[0] if active else None,
        'active_model':active_model,
        'active_vision':('on' if '--vision' in info['args'] else 'off') if active_model else None,
        'active_context':(int(info['args'][info['args'].index('--max-context')+1])
            if active_model and '--max-context' in info['args'] else None),
        'engine':engine,'state':info['state'],
        'running':bool(active),'applied':applied(info),
        'pending':bool(active) and (active[0]!=load()['engine'] or not applied(info)),
        'busy':operation_busy() or benchmark_busy(),
        'services':{e:{'state':i['state']} for e,i in services.items()}}


def unload_ollama():
    try:
        with urllib.request.urlopen('http://127.0.0.1:11434/api/ps',timeout=3) as r:
            models=json.load(r).get('models',[])
    except (OSError,urllib.error.URLError): return
    for item in models:
        name=item.get('name') or item.get('model')
        if not name: continue
        request=urllib.request.Request('http://127.0.0.1:11434/api/generate',
            data=json.dumps({'model':name,'keep_alive':0}).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request,timeout=30) as r: r.read()


def control(action):
    HOME.mkdir(parents=True,exist_ok=True)
    with LOCK.open('a') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise RuntimeError('Another server-control operation is in progress')
        if benchmark_busy(): raise RuntimeError('Benchmark in progress; wait until vLLM is restored')
        info=status()
        if action=='toggle': action='stop' if info['running'] else 'start'
        if action=='stop':
            # A second click while loading must not kill model startup.
            if info['state'] in ('loading','stopping'): raise RuntimeError('Server is still transitioning; please wait')
            for service in SERVICES.values(): systemctl('stop',service)
            return {'action':'stop'}
        if action not in ('start','restart'): raise ValueError('Unknown action')
        if info['state'] in ('loading','stopping'): raise RuntimeError('Server is still transitioning; please wait')
        choice=selected(); engine=choice['engine']
        if engine=='vllm': vllm.validate({'model':choice['model'],'template':choice['template']})
        else: ninfer_command()  # Validate assets before stopping the existing server.
        if action=='start' and info['active_engine']==engine and info['applied']: return {'action':'already-running','engine':engine}
        pi_data=pi_model_update(choice)
        unload_ollama()
        for other,service in SERVICES.items():
            if other!=engine: systemctl('stop',service)
        # Inactive units may be garbage-collected; reset-failed on an unloaded
        # unit errors even when its unit file exists. Only reset actual failures.
        if info.get('services',{}).get(engine,{}).get('state') == 'failed':
            systemctl('reset-failed',SERVICES[engine])
        systemctl('restart',SERVICES[engine])
        save_pi_model(pi_data)
        return {'action':'start','engine':engine,'state':'loading'}


def ninfer_command():
    choice=selected('ninfer'); template=NINFER_TEMPLATES[choice['template']]['path']
    profile=NINFER_MODELS[choice['model']]
    exe=profile['root']/'build/apps/ninfer-serve'; model=profile['root']/'models'/profile['file']
    for path in (exe,model,Path(template) if template else None):
        if path and not path.is_file(): raise ValueError(f'Missing NInfer prerequisite: {path}')
    if 'size' in profile and model.stat().st_size != profile['size']:
        raise ValueError(f'Incomplete NInfer artifact: {model}')
    args=[str(exe),str(model),'--host','127.0.0.1','--port','8000','--model-id','local-llm',
        '--max-context',str(choice['context']),'--kv-capacity',str(choice['context']),'--max-concurrency','4']
    if choice['model'] == 'qwen38-gsq-iq3s':
        args += ['--kv-dtype','rk8v4','--gdn-state-fp16','--host-cache-mib','2048',
                 '--spec','mtp','--draft-tokens','3']
        if choice['vision'] == 'on': args += ['--vision']
    else:
        args += ['--kv-dtype','fp8','--device-state-slots','0','--host-context-mib','2048',
                 '--spec','mtp','--draft-tokens','4','--lm-head-draft']
    args += ['--preserve-thinking']
    if template: args+=['--chat-template',template]
    return args


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['list','status','select','start','stop','restart','toggle','launch-ninfer'])
    parser.add_argument('values',nargs='*');args=parser.parse_args()
    if args.command=='list':
        print(json.dumps({'selected':selected(),'defaults':{e:selected(e) for e in SERVICES},
            'context':{'min':CONTEXT_MIN,'max':CONTEXT_MAX,'step':CONTEXT_STEP},
            'engines':[{'id':'vllm','label':'vLLM'},{'id':'ninfer','label':'NInfer'}],'models':profiles()}))
    elif args.command=='status': print(json.dumps(status()))
    elif args.command=='select':
        if len(args.values) not in (3,4,5): raise ValueError('select ENGINE MODEL TEMPLATE [VISION] [CONTEXT]')
        if benchmark_busy(): raise RuntimeError('Benchmark in progress; selections are locked until restoration')
        with LOCK.open('a') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise RuntimeError('Control operation in progress')
            values = args.values[:4]
            if len(args.values) == 5:
                values.append(int(args.values[4]))
            print(json.dumps(choose(*values)))
    elif args.command=='launch-ninfer':
        if args.values: raise ValueError('Unexpected arguments')
        command=ninfer_command();os.execv(command[0],command)
    else:
        if args.values: raise ValueError('Unexpected arguments')
        print(json.dumps(control(args.command)))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as exc:
        print(str(exc),file=sys.stderr);sys.exit(1)
