#!/usr/bin/env python3
"""
Repo에 포함된 Codex skills를 CODEX_HOME/skills 또는 ~/.codex/skills에 설치한다.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"


def get_codex_skills_dir(env: dict[str, str] | None = None) -> Path:
    env = env or os.environ
    codex_home = env.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "skills"
    return Path.home() / ".codex" / "skills"


def discover_skills(skills_root: Path = SKILLS_ROOT) -> list[Path]:
    if not skills_root.exists():
        return []
    return sorted(
        path for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    )


def _remove_target(target: Path):
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.exists():
        shutil.rmtree(target)


def install_skill(source: Path, target_root: Path, *, mode: str = "symlink", force: bool = False) -> str:
    target_root.mkdir(parents=True, exist_ok=True)
    target = target_root / source.name

    if target.exists() or target.is_symlink():
        same_symlink = target.is_symlink() and target.resolve() == source.resolve()
        if same_symlink:
            return "unchanged"
        if not force:
            return "skipped"
        _remove_target(target)

    if mode == "copy":
        shutil.copytree(source, target)
    else:
        target.symlink_to(source.resolve(), target_is_directory=True)

    return "installed"


def install_all_skills(*, skills_root: Path = SKILLS_ROOT, target_root: Path | None = None,
                       mode: str = "symlink", force: bool = False) -> list[tuple[str, str]]:
    target_root = target_root or get_codex_skills_dir()
    results = []
    for skill in discover_skills(skills_root):
        status = install_skill(skill, target_root, mode=mode, force=force)
        results.append((skill.name, status))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install repo Codex skills")
    parser.add_argument("--mode", choices=["symlink", "copy"], default="symlink")
    parser.add_argument("--force", action="store_true", help="기존 skill이 있으면 덮어쓴다")
    parser.add_argument("--target-dir", type=Path, help="설치 대상 skills 디렉토리")
    parser.add_argument("--list", action="store_true", help="설치 대상 skill 목록만 출력한다")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    skills = discover_skills()

    if args.list:
        for skill in skills:
            print(skill.name)
        return 0

    if not skills:
        print("설치할 skill이 없습니다.", file=sys.stderr)
        return 1

    target_root = args.target_dir or get_codex_skills_dir()
    results = install_all_skills(
        target_root=target_root,
        mode=args.mode,
        force=args.force,
    )

    print(f"대상 디렉토리: {target_root}")
    for name, status in results:
        print(f"- {name}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
