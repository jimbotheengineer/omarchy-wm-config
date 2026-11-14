#!/usr/bin/env python3
"""Check, install or restore the portable WM profile without restarting the session."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent

def run(args, env=None):
    result = subprocess.run(args, text=True, capture_output=True, env=env)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed:\n{result.stdout}\n{result.stderr}')
    return result.stdout + result.stderr

def remove(path):
    if path.is_dir() and not path.is_symlink(): shutil.rmtree(path)
    elif path.exists() or path.is_symlink(): path.unlink()

def restore(backup):
    records = json.loads((backup / 'manifest.json').read_text())
    for record in reversed(records):
        target = Path(record['target'])
        saved = backup / record['saved']
        # A missing backup for a formerly existing target is never grounds to delete it.
        if record['existed'] and not saved.exists() and not saved.is_symlink():
            raise RuntimeError(f'Missing saved item: {saved}')
        remove(target)
        if record['existed']:
            target.parent.mkdir(parents=True, exist_ok=True)
            if saved.is_symlink(): target.symlink_to(os.readlink(saved))
            elif saved.is_dir(): shutil.copytree(saved, target, symlinks=True)
            else: shutil.copy2(saved, target)
    print('Restored saved configuration. Log out and back in; no session was restarted.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true', help='validate and print plan (default)')
    modes.add_argument('--install', action='store_true', help='back up targets and install; no restart')
    modes.add_argument('--restore', type=Path, metavar='BACKUP_DIR')
    parser.add_argument('--home', type=Path, default=Path.home(), help='recipient home; also useful for isolated checks')
    args = parser.parse_args()
    if os.geteuid() == 0: parser.error('Run as the desktop user, without sudo.')
    if args.restore:
        restore(args.restore.resolve())
        return
    home = args.home.expanduser().resolve()
    if not home.is_dir(): parser.error('--home must be an existing directory')
    for command, minimum in [('Hyprland', (0,57,2)), ('noctalia', (5,5,0))]:
        if not shutil.which(command): raise RuntimeError(f'Install {command} first; see AGENTS.md')
        version = re.search(r'(\d+)\.(\d+)\.(\d+)', run([command, '--version']))
        if not version or tuple(map(int, version.groups())) < minimum:
            raise RuntimeError(f'{command} must be at least {".".join(map(str,minimum))}')
    wallpaper = home / '.local/share/wm-profile/wallpapers/dragon.png'
    config_home = home / '.config'
    state_home = home / '.local/state'
    if home == Path.home().resolve():
        config_home = Path(os.environ.get('XDG_CONFIG_HOME', str(config_home))).resolve()
        state_home = Path(os.environ.get('XDG_STATE_HOME', str(state_home))).resolve()
        wallpaper = Path(os.environ.get('XDG_DATA_HOME', str(home/'.local/share'))) / 'wm-profile/wallpapers/dragon.png'
    with tempfile.TemporaryDirectory(prefix='wm-profile-stage-') as temp:
        stage = Path(temp)
        shutil.copytree(ROOT/'config', stage/'config')
        cfg = stage/'config/noctalia/config.toml'
        text = cfg.read_text().replace('"__WALLPAPER__"', json.dumps(str(wallpaper)))
        cfg.write_text(text)
        # Use only the recipient's output names; never ship source-machine identifiers.
        outputs = []
        if shutil.which('hyprctl') and home == Path.home().resolve():
            result = subprocess.run(['hyprctl','-j','monitors','all'], capture_output=True, text=True)
            if result.returncode == 0:
                try:
                    outputs = [m['name'] for m in json.loads(result.stdout) if re.fullmatch(r'[A-Za-z0-9_.:-]+',m['name'])]
                except (ValueError,KeyError,TypeError): pass
        outputs = (outputs or ['0'])[:3]
        variables = stage/'config/hypr/config/variables.lua'
        text = variables.read_text()
        for i in range(1,4):
            name = outputs[i-1] if len(outputs) >= i else outputs[0]
            text = re.sub(f'MONITOR{i} = "[^"]*"', f'MONITOR{i} = {json.dumps(name)}',text)
        variables.write_text(text)
        runtime = stage/'runtime'
        runtime.mkdir(mode=0o700)
        env = os.environ.copy()
        env.update(XDG_CONFIG_HOME=str(stage/'config'), XDG_RUNTIME_DIR=str(runtime))
        env.pop('HYPRLAND_INSTANCE_SIGNATURE', None)
        result = run(['Hyprland','--verify-config','-c',str(stage/'config/hypr/hyprland.lua')], env)
        if 'config ok' not in result.lower(): raise RuntimeError('Hyprland did not confirm config validity')
        run(['noctalia','config','validate',str(cfg)], env)
        print('Hyprland and Noctalia configuration validation passed.')
        targets = [(stage/'config/hypr',config_home/'hypr'),
                   (stage/'config/noctalia',config_home/'noctalia'),
                   (stage/'config/kitty',config_home/'kitty'),
                   (None,state_home/'noctalia/settings.toml'),
                   (ROOT/'wallpapers/dragon.png',wallpaper)]
        print('Targets (existing items will be backed up):')
        for _,target in targets: print(f'  {target}')
        apps = ['kitty','dolphin','brave','gnome-text-editor','gnome-calculator','btop','hyprpicker','uwsm','dbus-update-activation-environment']
        missing = [c for c in apps if not shutil.which(c)]
        if missing: print('Missing launcher commands; install or edit variables/binds: '+', '.join(missing))
        if not args.install:
            print('Check only. Read AGENTS.md, then use --install when ready.')
            return
        if missing: raise RuntimeError('Resolve missing launcher commands before installing.')
        # All validation finishes before any live configuration is replaced.
        backup = state_home/'wm-profile/backups'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        backup.mkdir(parents=True, mode=0o700)
        records=[]
        for i,(_,target) in enumerate(targets):
            exists = target.exists() or target.is_symlink()
            saved = backup/str(i)
            if exists:
                if target.is_symlink(): saved.symlink_to(os.readlink(target))
                elif target.is_dir(): shutil.copytree(target,saved,symlinks=True)
                else: shutil.copy2(target,saved)
            records.append({'target':str(target),'saved':str(i),'existed':exists})
        (backup/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
        try:
            for source,target in targets:
                remove(target)
                target.parent.mkdir(parents=True,exist_ok=True)
                if source is None: target.write_text('config_version = 20\n')
                elif source.is_dir(): shutil.copytree(source,target)
                else: shutil.copy2(source,target)
        except Exception:
            restore(backup)
            raise
        print(f'Installed. Backup: {backup}')
        print('No session processes or services were changed. Follow AGENTS.md before logging in again.')

if __name__ == '__main__':
    try: main()
    except (RuntimeError,OSError) as exc: raise SystemExit(str(exc))
