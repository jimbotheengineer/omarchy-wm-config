#!/usr/bin/env python3
"""Install only the anonymous Noctalia plugin; backend setup is separate."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--helper',type=Path,required=True,help='absolute path to the prepared server-control.py backend')
    parser.add_argument('--install',action='store_true',help='copy plugin after validation; default is check only')
    args=parser.parse_args()
    if os.geteuid()==0: parser.error('Run as the desktop user, without sudo.')
    helper=args.helper.expanduser().resolve()
    if not helper.is_file(): parser.error('--helper must be an existing Python backend file')
    root=Path(__file__).resolve().parent
    data=Path(os.environ.get('XDG_DATA_HOME',str(Path.home()/'.local/share')))
    target=data/'noctalia/plugins/llm-control'
    with tempfile.TemporaryDirectory(prefix='llm-plugin-stage-') as temp:
        stage=Path(temp)/'llm-control'
        shutil.copytree(root/'plugin',stage)
        for filename in ['widget.luau','panel.luau']:
            p=stage/filename
            p.write_text(p.read_text().replace('"__LLM_CONTROL_HELPER__"',json.dumps(str(helper))))
        subprocess.run(['noctalia','plugins','lint',str(stage)],check=True)
        print(f'Plugin target: {target}')
        if not args.install:
            print('Check only. Backend and plugin have not been started.')
            return
        if target.exists():
            backup=target.with_name('llm-control.backup-'+datetime.datetime.now().strftime('%Y%m%dT%H%M%S%f'))
            shutil.move(target,backup)
            print(f'Previous plugin: {backup}')
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(stage,target)
        print('Installed local/llm-control. Enable it and add its widget as described in AGENTS.md.')

if __name__=='__main__': main()
