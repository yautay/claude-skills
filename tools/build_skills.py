#!/usr/bin/env python3
"""Package standalone provider skills from shared sources; --check detects drift."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    failures = []
    packages = [
        ('git-clean', 'shared/git-clean', ('claude', 'codex')),
        ('repo-safe-data-audit', 'shared/repo-safe-data-audit', ('claude', 'codex')),
    ]
    built = 0
    for skill, source_dir, providers in packages:
        sources = [p for p in sorted((ROOT / source_dir).rglob('*'))
                   if p.is_file() and p.suffix in ('.sh', '.ps1', '.py', '.md', '.yaml')
                   and '__pycache__' not in p.parts]
        targets = [ROOT / provider / 'skills' / skill for provider in providers
                   if (ROOT / provider / 'skills' / skill / 'SKILL.md').is_file()]
        for target in targets:
            for source in sources:
                destination = target / source.relative_to(ROOT / source_dir)
                if args.check:
                    if not destination.exists() or destination.read_bytes() != source.read_bytes():
                        failures.append(str(destination.relative_to(ROOT)))
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())
            built += 1
    if failures:
        print('Outdated packages: ' + ', '.join(failures))
        return 1
    print(('Checked' if args.check else 'Built') + f' {built} skill packages.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
