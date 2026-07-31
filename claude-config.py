#!/usr/bin/env python3
"""Sync portable Claude Code config between this repo and ~/.claude.

Only the names in TRACKED ever move. Private material — .credentials.json,
projects/, sessions/, history.jsonl — stays in ~/.claude and is never copied
here, so this repo cannot leak it even if .gitignore is wrong.
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

TRACKED = ("CLAUDE.md", "settings.json")
MUST_PARSE_AS_JSON = frozenset({"settings.json"})

REPO = Path(__file__).resolve().parent
TARGET = Path.home() / ".claude"


class ConfigError(Exception):
    pass


def json_failure(path):
    if path.name not in MUST_PARSE_AS_JSON:
        return None
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return f"{path} is not valid JSON: {exc}"
    return None


def validate(source_dir):
    """Fail before any copy, so a bad source never half-overwrites a target."""
    absent = [name for name in TRACKED if not (source_dir / name).is_file()]
    if absent:
        raise ConfigError(f"missing in {source_dir}: {', '.join(absent)}")

    for name in TRACKED:
        failure = json_failure(source_dir / name)
        if failure:
            raise ConfigError(failure)


def back_up(path):
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = path.with_name(f"{path.name}.bak-{stamp}")
    shutil.copy2(path, destination)
    return destination


def copy_tracked(source_dir, destination_dir, back_up_existing):
    for name in TRACKED:
        destination = destination_dir / name
        saved = back_up(destination) if back_up_existing else None
        shutil.copy2(source_dir / name, destination)
        note = f"   (previous saved as {saved.name})" if saved else ""
        print(f"  {name}{note}")


def describe_difference(in_repo, in_target):
    if not in_repo.is_file():
        return "missing in repo"
    if not in_target.is_file():
        return "missing in ~/.claude"
    if in_repo.read_bytes() == in_target.read_bytes():
        return "identical"
    return "differs"


def apply():
    if not TARGET.is_dir():
        raise ConfigError(f"{TARGET} does not exist - run Claude Code once first")
    validate(REPO)
    print(f"apply: {REPO} -> {TARGET}")
    copy_tracked(REPO, TARGET, back_up_existing=True)
    print("done - restart Claude Code, or it will pick settings up on its own")


def capture():
    validate(TARGET)
    print(f"capture: {TARGET} -> {REPO}")
    copy_tracked(TARGET, REPO, back_up_existing=False)
    print("done - review with 'git diff', then commit")


def check():
    differing = 0
    print(f"repo   {REPO}\ntarget {TARGET}\n")
    for name in TRACKED:
        status = describe_difference(REPO / name, TARGET / name)
        print(f"  {name:<16} {status}")
        if status != "identical":
            differing += 1

    if not differing:
        print("\nin sync")
        return 0
    print(f"\n{differing} file(s) out of sync - 'capture' updates the repo, 'apply' updates ~/.claude")
    return 1


COMMANDS = {"apply": apply, "capture": capture, "check": check}


def main(argv):
    if len(argv) != 1 or argv[0] not in COMMANDS:
        print(f"usage: {Path(__file__).name} {{{'|'.join(COMMANDS)}}}", file=sys.stderr)
        return 2

    try:
        result = COMMANDS[argv[0]]()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if result is None:
        return 0
    return result


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
