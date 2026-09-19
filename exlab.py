#!/usr/bin/env python3
"""Local EX374 practice lab runner for Red Hat training workstations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys


ROOT = Path(os.environ.get("EXLAB_ROOT", Path.home() / ".local/share/ex374-lab"))
STATE_HOME = Path(os.environ.get("EXLAB_STATE_HOME", Path.home() / ".local/state/ex374-lab"))
WORK_HOME = Path(os.environ.get("EXLAB_WORK_HOME", Path.home() / "ex374-work"))
STATE_FILE = STATE_HOME / "state.json"


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def labs() -> dict[str, dict]:
    entries = load_json(ROOT / "labs.json", [])
    return {entry["id"]: entry for entry in entries}


def state() -> dict:
    return load_json(STATE_FILE, {"active": None, "completed": {}, "assessments": {}})


def title(entry: dict) -> str:
    brief = ROOT / "labs" / entry["id"] / "README.md"
    try:
        first = brief.read_text(encoding="utf-8-sig").splitlines()[0]
        return first.lstrip("# ").strip()
    except (FileNotFoundError, IndexError):
        return entry["id"]


def resolve(entry_id: str | None) -> tuple[dict, Path]:
    all_labs = labs()
    current = state().get("active")
    selected = entry_id or (current or {}).get("id")
    if not selected:
        raise SystemExit("No active exercise. Run: exlab start <exercise>")
    if selected not in all_labs:
        raise SystemExit(f"Unknown exercise: {selected}. Run: exlab list")
    work = Path((current or {}).get("workdir", "")) if (current or {}).get("id") == selected else WORK_HOME / selected
    return all_labs[selected], work


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".exlab" not in path.parts and path.name != "TASK.md"
    }


def preflight(entry: dict) -> list[str]:
    warnings = []
    for command in entry.get("commands", []):
        if shutil.which(command) is None:
            warnings.append(f"required command not found: {command}")
    for host in entry.get("dns", []):
        try:
            socket.getaddrinfo(host, None)
        except socket.gaierror:
            warnings.append(f"required host does not resolve: {host}")
    for host in entry.get("optional_dns", []):
        try:
            socket.getaddrinfo(host, None)
        except socket.gaierror:
            warnings.append(f"optional service unavailable; controller portion cannot run: {host}")
    if shutil.which("podman"):
        for image in entry.get("images", []):
            found = subprocess.run(
                ["podman", "image", "exists", image], check=False, capture_output=True
            ).returncode == 0
            if not found:
                warnings.append(f"required container image is not cached: {image}")
    return warnings


def cmd_list(_: argparse.Namespace) -> int:
    current_state = state()
    completed = current_state.get("completed", {})
    assessments = current_state.get("assessments", {})
    print(f"{'EXERCISE':43} {'GRADE':9} STATUS")
    for entry in labs().values():
        status = completed.get(entry["id"], assessments.get(entry["id"], "-"))
        print(f"{entry['id']:43} {entry['grade']:9} {status}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    entry, work = resolve(args.exercise)
    current = state().get("active")
    if current and current.get("id") != entry["id"]:
        raise SystemExit(f"Finish the active exercise first: {current['id']}")
    if work.exists() and any(work.iterdir()) and not args.reset:
        raise SystemExit(f"Work directory already exists: {work}\nUse --reset only if you intend to delete it.")
    if work.exists() and args.reset:
        shutil.rmtree(work)
    work.mkdir(parents=True)
    source = ROOT / "labs" / entry["id"]
    starter = source / "starter"
    if starter.is_dir():
        shutil.copytree(starter, work, dirs_exist_ok=True)
    shutil.copy2(source / "README.md", work / "TASK.md")
    metadata = work / ".exlab"
    metadata.mkdir()
    save_json(metadata / "starter.json", snapshot(work))
    current_state = state()
    current_state["active"] = {"id": entry["id"], "workdir": str(work)}
    save_json(STATE_FILE, current_state)
    print(f"Started: {entry['id']} — {title(entry)}")
    print(f"Work in: {work}")
    print(f"Brief:   {work / 'TASK.md'}")
    warnings = preflight(entry)
    if warnings:
        print("\nEnvironment warnings:")
        for warning in warnings:
            print(f"- {warning}")
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    entry, work = resolve(args.exercise)
    current = state().get("active")
    if current and current.get("id") != entry["id"]:
        raise SystemExit(f"Finish the active exercise first: {current['id']}")
    if work.exists() and not args.yes:
        answer = input(f"Delete all work in {work} and restore the starter files? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Reset cancelled.")
            return 1
    return cmd_start(argparse.Namespace(exercise=entry["id"], reset=True))


def changed_files(work: Path) -> list[str]:
    before = load_json(work / ".exlab/starter.json", {})
    after = snapshot(work)
    return sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))


def yaml_check(work: Path) -> list[str]:
    failures = []
    try:
        import yaml
    except ImportError:
        return ["PyYAML unavailable; YAML parse check skipped"]
    for path in work.rglob("*"):
        if path.suffix not in {".yml", ".yaml"} or ".exlab" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if text.startswith("$ANSIBLE_VAULT;"):
            continue
        try:
            list(yaml.safe_load_all(text))
        except yaml.YAMLError as error:
            failures.append(f"{path.relative_to(work)}: {str(error).splitlines()[0]}")
    return failures


def basic_grade(work: Path) -> int:
    changed = changed_files(work)
    todo_files = []
    for path in work.rglob("*"):
        if not path.is_file() or ".exlab" in path.parts or path.name == "TASK.md":
            continue
        if "TODO" in path.read_text(encoding="utf-8", errors="ignore"):
            todo_files.append(path.relative_to(work).as_posix())
    yaml_failures = yaml_check(work)
    print(f"Changed files: {len(changed)}")
    for path in changed:
        print(f"  {path}")
    if todo_files:
        print("FAIL: unresolved TODO markers:")
        for path in todo_files:
            print(f"  {path}")
    if yaml_failures:
        print("FAIL: YAML validation:")
        for failure in yaml_failures:
            print(f"  {failure}")
    if not changed:
        print("FAIL: no work differs from the starter files")
    passed = bool(changed) and not todo_files and not yaml_failures
    print("BASIC PASS" if passed else "BASIC FAIL")
    print("Note: basic grading checks completion and YAML only; also run the acceptance tests in TASK.md.")
    return 0 if passed else 1


def cmd_grade(args: argparse.Namespace) -> int:
    entry, work = resolve(args.exercise)
    if not work.is_dir():
        raise SystemExit(f"Missing work directory: {work}")
    source = ROOT / "labs" / entry["id"]
    if entry["grade"] == "automatic" and (source / "grade.py").is_file():
        return subprocess.run([sys.executable, str(source / "grade.py"), str(work)], check=False).returncode
    if entry["grade"] == "manual":
        print("Manual exercise: run 'exlab mark' for criterion-by-criterion scoring.")
        return 0
    result = basic_grade(work)
    if (source / "CHECKLIST.md").is_file():
        print("For criterion scoring run: exlab mark")
    return result


def checklist_items(path: Path) -> list[str]:
    items = []
    current = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- [ ] "):
            if current:
                items.append(" ".join(current))
            current = [line[6:].strip()]
        elif current and (line.startswith("  ") or line.startswith("      ")):
            current.append(line.strip())
    if current:
        items.append(" ".join(current))
    return items


def cmd_mark(args: argparse.Namespace) -> int:
    entry, _ = resolve(args.exercise)
    checklist = ROOT / "labs" / entry["id"] / "CHECKLIST.md"
    if not checklist.is_file():
        raise SystemExit("No separate marking checklist is available; use TASK.md.")
    items = checklist_items(checklist)
    if not items:
        raise SystemExit("The marking checklist has no checkbox criteria.")
    score = 0
    print(f"Self-marking: {entry['id']} ({len(items)} criteria)")
    for number, item in enumerate(items, 1):
        answer = input(f"\n{number}. {item}\nMet? [y/N] ").strip().lower()
        if answer in {"y", "yes"}:
            score += 1
    percent = round(score * 100 / len(items))
    assessment = f"score {score}/{len(items)} ({percent}%)"
    current_state = state()
    current_state.setdefault("assessments", {})[entry["id"]] = assessment
    save_json(STATE_FILE, current_state)
    print(f"\n{assessment}")
    return 0 if score == len(items) else 1


def cmd_status(_: argparse.Namespace) -> int:
    current = state().get("active")
    if not current:
        print("No active exercise.")
        return 0
    entry, work = resolve(current["id"])
    print(f"Active:  {entry['id']} — {title(entry)}")
    print(f"Workdir: {work}")
    print(f"Changed: {len(changed_files(work)) if work.is_dir() else 'workdir missing'}")
    for warning in preflight(entry):
        print(f"WARNING: {warning}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    _, work = resolve(args.exercise)
    brief = work / "TASK.md"
    if not brief.is_file():
        raise SystemExit(f"Missing brief: {brief}")
    print(brief.read_text(encoding="utf-8-sig"))
    return 0


def cmd_finish(args: argparse.Namespace) -> int:
    entry, work = resolve(args.exercise)
    result = cmd_grade(argparse.Namespace(exercise=entry["id"]))
    if result and not args.force:
        print("Not finished because grading failed. Use --force only for a deliberately self-assessed exercise.")
        return result
    current_state = state()
    current_state.setdefault("completed", {})[entry["id"]] = "passed" if result == 0 else "self-assessed"
    if (current_state.get("active") or {}).get("id") == entry["id"]:
        current_state["active"] = None
    save_json(STATE_FILE, current_state)
    print(f"Finished: {entry['id']}")
    print(f"Work retained at: {work}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="exlab", description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("list").set_defaults(func=cmd_list)
    start = commands.add_parser("start")
    start.add_argument("exercise")
    start.add_argument("--reset", action="store_true", help="delete and recreate existing exercise work")
    start.set_defaults(func=cmd_start)
    reset = commands.add_parser("reset", help="delete all exercise work and restore its starter files")
    reset.add_argument("exercise", nargs="?")
    reset.add_argument("--yes", action="store_true", help="reset without an interactive confirmation")
    reset.set_defaults(func=cmd_reset)
    for name, function in (("grade", cmd_grade), ("show", cmd_show)):
        command = commands.add_parser(name)
        command.add_argument("exercise", nargs="?")
        command.set_defaults(func=function)
    mark = commands.add_parser("mark", help="score the exercise against its marking checklist")
    mark.add_argument("exercise", nargs="?")
    mark.set_defaults(func=cmd_mark)
    finish = commands.add_parser("finish")
    finish.add_argument("exercise", nargs="?")
    finish.add_argument("--force", action="store_true")
    finish.set_defaults(func=cmd_finish)
    commands.add_parser("status").set_defaults(func=cmd_status)
    return result


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(arguments.func(arguments))
