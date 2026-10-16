#!/usr/bin/env python3
"""Portable local commands for the Codex job-search workspace."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def runtime(root=ROOT):
    file = root / '.runtime/runtime.local.json'
    value = json.loads(file.read_text(encoding='utf-8-sig')) if file.exists() else {}
    if not isinstance(value, dict):
        raise ValueError('runtime.local.json debe ser un objeto JSON')
    return value


def executable(name, config, root=ROOT):
    configured = config.get(name)
    if isinstance(configured, str) and Path(configured).is_file():
        return str(Path(configured).resolve())
    local = root / '.runtime/bun/bun-windows-x64/bun.exe'
    if name == 'bun' and local.is_file():
        return str(local)
    return sys.executable if name == 'python' else shutil.which(name)


def environment(config, root=ROOT):
    env = os.environ.copy()
    bins = [str(Path(p).parent) for n in ('python', 'bun', 'node', 'codex') if (p := executable(n, config, root))]
    env['PATH'] = os.pathsep.join(dict.fromkeys(bins + [env.get('PATH', '')]))
    env['PYTHONPATH'] = os.pathsep.join(filter(None, [str(root / '.runtime/python-packages'), env.get('PYTHONPATH')]))
    env['PYTHONUTF8'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    return env


def search_args(query, mode, limit, root=ROOT):
    if not query.strip() or mode not in ('all', 'remote', 'hybrid', 'onsite') or not 1 <= limit <= 20:
        raise ValueError('Consulta, modalidad o límite inválidos')
    args = ['run', str(root / '.agents/skills/freehire-search/cli/src/cli.ts'), 'search', '--query', query,
            '--country', 'AR', '--jobage', '14', '--limit', str(limit), '--format', 'json', '--no-description']
    return args + (['--remote', mode] if mode != 'all' else [])


def portal_enabled(name, root=ROOT):
    packages = str(root / '.runtime/python-packages')
    if Path(packages).is_dir() and packages not in sys.path:
        sys.path.insert(0, packages)
    try:
        import yaml
    except ImportError as exc:
        raise ValueError('Falta PyYAML; instalá requirements.txt antes de consultar el portal') from exc
    text = (root / '.agents/skills' / name / 'SKILL.md').read_text(encoding='utf-8')
    if not text.startswith('---\n') or '\n---' not in text[4:]:
        raise ValueError(f'Metadatos del portal inválidos: {name}')
    data = yaml.safe_load(text[4:].split('\n---', 1)[0])
    if not isinstance(data, dict) or not isinstance(data.get('metadata', {}), dict):
        raise ValueError(f'Metadatos del portal inválidos: {name}')
    value = data.get('metadata', {}).get('enabled', True)
    if isinstance(value, str) and value.lower() in ('true', 'false'):
        value = value.lower() == 'true'
    if not isinstance(value, bool):
        raise ValueError(f'metadata.enabled debe indicar true o false: {name}')
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    subs.add_parser('doctor')
    subs.add_parser('portals')
    search = subs.add_parser('search', help='Fuente tecnológica freehire para Argentina')
    search.add_argument('--query', required=True)
    search.add_argument('--mode', choices=('all', 'remote', 'hybrid', 'onsite'), default='remote')
    search.add_argument('--limit', type=int, choices=range(1, 21), default=10)
    for name in ('python', 'bun'):
        subs.add_parser(name).add_argument('arguments', nargs=argparse.REMAINDER)
    start = subs.add_parser('start')
    start.add_argument('--prompt', default='Leé AGENTS.md y usá argentina-job-search. Ayudame con mi búsqueda laboral. Leé el perfil existente y preguntá solo lo necesario para continuar. Conversá en español.')
    args = parser.parse_args(argv)
    try:
        config = runtime()
        env = environment(config)
        if args.action == 'portals':
            print((ROOT / 'config/portales-argentina.json').read_text(encoding='utf-8'))
            return 0
        if args.action == 'doctor':
            command = [executable('python', config), str(ROOT / 'tools/doctor.py')]
        elif args.action == 'search':
            bun = executable('bun', config)
            if not bun:
                print('Bun no está disponible. Usá Codex para búsqueda web guiada; la consulta automática no se ejecutó.', file=sys.stderr)
                return 2
            if not portal_enabled('freehire-search'):
                print('freehire-search está deshabilitado en metadata.enabled; la consulta no se ejecutó.', file=sys.stderr)
                return 2
            print('Fuente: freehire (tecnología). Verificar aviso, vigencia y elegibilidad; no se asigna afinidad sin perfil.', file=sys.stderr)
            command = [bun] + search_args(args.query, args.mode, args.limit)
        elif args.action == 'start':
            codex = executable('codex', config)
            if not codex:
                print('Codex CLI no está en PATH. Abrí esta carpeta en la aplicación Codex y seguí AGENTS.md.', file=sys.stderr)
                return 2
            command = [codex, '--cd', str(ROOT), '--search', args.prompt]
        else:
            tool = executable(args.action, config)
            if not tool:
                print(f'{args.action} no está disponible.', file=sys.stderr)
                return 2
            command = [tool] + (args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments)
        return subprocess.run(command, cwd=ROOT, env=env).returncode
    except (OSError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())
