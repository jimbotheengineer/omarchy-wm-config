#!/usr/bin/env python3
"""Curated local vLLM profiles for the Noctalia control panel and launcher.

Only list models with local configuration/tokenizer assets. GGUF is a candidate,
not a promise of successful startup; it is never selected automatically.
"""
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile

HOME = (Path.home() / 'llm/vllm')
STATE = HOME / 'selection.json'
NATIVE = HOME / 'models/nvidia/Qwen3.8-27B-NVFP4'
TOKENIZER = HOME / 'models/tokenizers/local-llm'
GGUF = HOME / 'models/gguf/qwen3.8-27b/Qwen3.8-27B-Q4_K_M.gguf'
MODELS = {
    'nvfp4': {'label': 'Qwen3.8 27B NVFP4 (current)', 'path': str(NATIVE), 'required': [NATIVE/'config.json', NATIVE/'model.safetensors.index.json', NATIVE/'tokenizer.json'], 'templates': {
        'sharp': {'label': 'Sharp (current)', 'path': str(NATIVE/'chat_template.jinja')},
        'nvidia': {'label': 'NVIDIA original', 'path': str(NATIVE/'chat_template.nvidia.jinja')},
    }, 'verified': True},
    'qwen-gguf': {'label': 'Qwen3.8 27B Q4_K_M GGUF (untested)', 'path': str(GGUF), 'required': [GGUF, TOKENIZER/'config.json', TOKENIZER/'tokenizer.json'], 'templates': {
        'embedded': {'label': 'GGUF original', 'path': str(TOKENIZER/'chat_template.jinja')},
        'sharp': {'label': 'Sharp (experimental)', 'path': str(NATIVE/'chat_template.jinja')},
    }, 'verified': False},
}
DEFAULT = {'model': 'nvfp4', 'template': 'sharp'}


def available():
    return {key: model for key, model in MODELS.items() if all(p.is_file() for p in model['required'])}


def load():
    if not STATE.exists():
        return DEFAULT.copy()
    value = json.loads(STATE.read_text())
    if not isinstance(value, dict) or set(value) != {'model', 'template'}:
        raise ValueError('Invalid selection file')
    validate(value)
    return value


def validate(value):
    models = available()
    model = models.get(value['model'])
    if model is None or value['template'] not in model['templates']:
        raise ValueError('Selected model or template is unavailable')
    template = Path(model['templates'][value['template']]['path'])
    if not template.is_file():
        raise ValueError(f'Template not found: {template}')
    return model, template


def save(value):
    validate(value)
    fd, tmp = tempfile.mkstemp(prefix='.selection-', dir=STATE.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, STATE)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if command == 'list':
        current = load()
        models = available()
        print(json.dumps({'selected': current, 'models': [
            {'id': key, 'label': model['label'], 'verified': model['verified'],
             'templates': [{'id': template, 'label': item['label']} for template, item in model['templates'].items() if Path(item['path']).is_file()]}
            for key, model in models.items()] }))
    elif command == 'status' and len(sys.argv) == 2:
        value = load()
        model, template = validate(value)
        pid = subprocess.check_output(['systemctl', '--user', 'show', 'vllm-local.service', '-p', 'MainPID', '--value'], text=True).strip()
        args = []
        if pid.isdigit() and int(pid) > 0:
            try:
                args = [a.decode() for a in Path('/proc', pid, 'cmdline').read_bytes().split(b'\0') if a]
            except (FileNotFoundError, ProcessLookupError):
                pass
        print(json.dumps({'running': bool(args), 'applied': bool(args) and model['path'] in args and str(template) in args}))
    elif command == 'select' and len(sys.argv) == 4:
        value = {'model': sys.argv[2], 'template': sys.argv[3]}
        save(value)
        print(json.dumps(value))
    elif command == 'launch' and len(sys.argv) == 2:
        value = load()
        model, template = validate(value)
        # Shell-safe argument array; launcher uses mapfile, not eval/source.
        for item in (value['model'], model['path'], str(template)):
            sys.stdout.buffer.write(item.encode() + b'\0')
    else:
        raise ValueError('Usage: model-selection.py list | status | select MODEL TEMPLATE | launch')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
