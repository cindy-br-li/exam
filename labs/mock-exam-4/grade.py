#!/usr/bin/env python3
"""Offline partial-credit grader for Mock Exam 4."""
from __future__ import annotations

import configparser
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
S = ROOT / "starter"
awards: list[tuple[str, int, int, str]] = []


def read(relative: str) -> str:
    try:
        return (S / relative).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def load(relative: str):
    try:
        return yaml.safe_load(read(relative))
    except yaml.YAMLError:
        return None


def give(name: str, points: int, maximum: int, note: str = "") -> None:
    awards.append((name, min(max(points, 0), maximum), maximum, note))


def git(*arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(S), *arguments],
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


# Git workflow (10)
branch = git("branch", "--show-current")
commits = git("log", "-n", "10", "--pretty=%s").splitlines()
ignore = read(".gitignore").lower()
points = 2 if branch and branch not in {"main", "master", "develop"} else 0
points += 4 if len(commits) >= 2 and len(set(commits[:2])) == 2 else 2 if commits else 0
points += 4 if all(term in ignore for term in ("navigator", "artifact", "*.retry", ".env")) else 0
give("Git workflow", points, 10, branch or "no feature branch")

# Ansible configuration (10)
config = configparser.ConfigParser(interpolation=None)
try:
    config.read_string(read("ansible.cfg"))
except configparser.Error:
    config = configparser.ConfigParser(interpolation=None)


def setting(section: str, key: str) -> str:
    return config.get(section, key, fallback="").strip().lower()


points = 0
points += 2 if setting("defaults", "inventory") == "inventory.ini" else 0
points += 2 if setting("defaults", "remote_user") == "devops" else 0
points += 2 if setting("defaults", "roles_path") and setting("defaults", "collections_path") else 0
try:
    points += 2 if int(setting("defaults", "forks")) >= 10 else 0
except ValueError:
    pass
points += 1 if setting("defaults", "host_key_checking") in {"true", "yes", "1"} else 0
points += 1 if setting("privilege_escalation", "become") in {"false", "no", "0"} else 0
give("Ansible configuration", points, 10)

# Navigator (5)
navigator = read("ansible-navigator.yml").lower()
navigator_data = load("ansible-navigator.yml")
points = 2 if isinstance(navigator_data, dict) and "ansible-navigator" in navigator_data else 0
points += 1 if re.search(r"mode\s*:\s*stdout", navigator) else 0
points += 1 if "playbook-artifact" in navigator and re.search(r"enable\s*:\s*false", navigator) else 0
points += 1 if "ee-supported-rhel9:latest" in navigator and re.search(r"policy\s*:\s*missing", navigator) else 0
give("Navigator configuration", points, 5)

# Inventory (10)
inventory = read("inventory.ini").lower()
points = 4 if all(term in inventory for term in ("[managed]", "branch01", "branch02", "192.0.2.41", "192.0.2.42")) else 0
points += 3 if "[branch_offices:children]" in inventory and re.search(r"(?m)^managed\s*$", inventory) else 0
points += 3 if "[managed:vars]" in inventory and "ansible_user=devops" in inventory and "ansible_port=22" in inventory else 0
give("Inventory", points, 10)

# External data (10)
variables = load("vars/groups.yml")
groups = variables.get("managed_groups", []) if isinstance(variables, dict) else []
users = variables.get("managed_users", []) if isinstance(variables, dict) else []
records = [line for line in read("files/users.txt").splitlines() if line.strip() and not line.lstrip().startswith("#")]
points = 3 if isinstance(groups, list) and len(groups) >= 2 else 0
points += 4 if isinstance(users, list) and len(users) >= 3 and all(isinstance(user, dict) and user.get("name") and isinstance(user.get("groups"), list) for user in users) else 0
record_names = [line.split("|", 1)[0].strip() for line in records if "|" in line]
points += 3 if len(record_names) >= 3 and len(record_names) == len(set(record_names)) and "password" not in read("files/users.txt").lower() else 0
give("External account data", points, 10)

# Groups and users (30)
playbook = read("playbooks/manage_users.yml")
playbook_data = load("playbooks/manage_users.yml")
points = 3 if isinstance(playbook_data, list) else 0
points += 4 if "../vars/groups.yml" in playbook else 0
points += 5 if re.search(r"(?:query|lookup)\s*\([^\n]*['\"]ansible\.builtin\.lines['\"]", playbook) else 0
points += 6 if "ansible.builtin.group:" in playbook and "managed_groups" in playbook else 0
points += 6 if "ansible.builtin.user:" in playbook else 0
points += 6 if "ansible.builtin.password" in playbook and "password_hash" in playbook and "no_log: true" in playbook.lower() else 0
give("Groups and users", points, 30)

# Membership and keys (15)
points = 6 if "subelements" in playbook and "append: true" in playbook.lower() else 0
points += 5 if "ansible.posix.authorized_key:" in playbook else 0
points += 4 if re.search(r"lookup\s*\([^\n]*['\"]ansible\.builtin\.file['\"]", playbook) else 0
give("Membership and authorized keys", points, 15)

# Execution controls (10)
points = 3 if playbook.lower().count("become: true") >= 3 else 0
points += 4 if all(tag in playbook for tag in ("groups", "users", "keys")) else 0
points += 3 if all(module in playbook for module in ("ansible.builtin.group:", "ansible.builtin.user:", "ansible.posix.authorized_key:")) else 0
give("Execution controls", points, 10)

total = sum(points for _, points, _, _ in awards)
maximum = sum(maximum for _, _, maximum, _ in awards)
for name, points, top, note in awards:
    print(f"{name:.<34} {points:>2}/{top:<2} {note}")
print("-" * 54)
print(f"TOTAL {total}/{maximum} — {'PASS' if total >= 70 else 'NOT YET PASSING'}")
assert maximum == 100
raise SystemExit(0 if total >= 70 else 1)
