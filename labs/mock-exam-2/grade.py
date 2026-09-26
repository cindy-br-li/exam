#!/usr/bin/env python3
"""Safe partial-credit grader for Mock Exam 2 (no Ansible or network calls)."""

from __future__ import annotations

import configparser
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required (python3 -m pip install pyyaml).")
    raise SystemExit(2)


ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "starter").resolve()
SECTIONS = {
    "Project configuration": 8,
    "Inventory and variables": 16,
    "Dependencies and data": 10,
    "Orchestration structure": 16,
    "Templates and filters": 12,
    "Delegation workflow": 14,
    "Rolling deployment": 18,
    "Quality": 6,
}
scores = {name: 0 for name in SECTIONS}
notes: list[str] = []


def text(relative: str) -> str:
    try:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size > 1_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def data(relative: str):
    raw = text(relative)
    if not raw:
        return None
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        notes.append(f"{relative}: malformed YAML ({str(exc).splitlines()[0]})")
        return None


def award(section: str, points: int, condition: bool, label: str) -> None:
    if condition:
        scores[section] += points
    else:
        notes.append(f"{section}: missing {label} ({points} mark{'s' if points != 1 else ''})")


def contains(raw: str, *patterns: str) -> bool:
    return all(re.search(pattern, raw, re.I | re.M | re.S) for pattern in patterns)


# 1: project configuration (8)
cfg_raw = text("ansible.cfg")
cfg = configparser.ConfigParser(interpolation=None)
try:
    cfg.read_string(cfg_raw)
except configparser.Error as exc:
    notes.append(f"ansible.cfg: malformed INI ({exc})")

defaults = cfg["defaults"] if cfg.has_section("defaults") else {}
award("Project configuration", 2, str(defaults.get("inventory", "")).rstrip("/\\").endswith("inventory"), "default inventory directory")
award("Project configuration", 1, "roles" in str(defaults.get("roles_path", "")), "local roles path")
award("Project configuration", 1, "collections" in str(defaults.get("collections_path", defaults.get("collections_paths", ""))), "local collections path")
award("Project configuration", 1, str(defaults.get("forks", "")) == "5", "five forks")
safe_host_keys = str(defaults.get("host_key_checking", "true")).lower() not in {"false", "no", "0"}
global_become = contains(cfg_raw, r"(?m)^\s*become\s*=\s*(true|yes|1)\s*$")
award("Project configuration", 1, safe_host_keys and not global_become, "safe SSH and scoped privilege settings")
nav = text("ansible-navigator.yml")
award("Project configuration", 2, contains(nav, r"aap\.lab\.example\.com/ee-supported-rhel9:latest", r"mode\s*:\s*(playbook|stdout)", r"artifact.*artifacts"), "navigator image, mode, and artifact settings")

# 2: inventory and variables (16)
inv_raw = text("inventory/hosts.yml")
inv = data("inventory/hosts.yml")
aliases = all(name in inv_raw for name in ("web_blue", "web_green", "load_balancer"))
endpoints = all(name in inv_raw for name in ("servera.lab.example.com", "serverb.lab.example.com", "serverc.lab.example.com"))
award("Inventory and variables", 4, isinstance(inv, dict) and aliases and endpoints, "three logical aliases and static endpoints")
award("Inventory and variables", 3, all(name in inv_raw for name in ("webservers", "loadbalancers", "platform")), "static group hierarchy")
award("Inventory and variables", 2, contains(inv_raw, r"ansible_user\s*:\s*devops", r"ansible_port\s*:\s*22"), "devops SSH/22 variables")
script = ROOT / "inventory/platform_inventory.py"
script_results = []
script_is_executable = os.name == "nt" or (script.is_file() and os.access(script, os.X_OK))
if script_is_executable:
    command = [sys.executable, str(script)] if os.name == "nt" else [str(script)]
    try:
        for arguments in (["--list"], ["--host", "smoke_runner"]):
            completed = subprocess.run(
                command + arguments,
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            script_results.append(json.loads(completed.stdout))
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        notes.append(f"inventory/platform_inventory.py: execution failed ({exc})")
list_result = script_results[0] if len(script_results) == 2 else {}
host_result = script_results[1] if len(script_results) == 2 else {}
valid_script = (
    list_result.get("smoke", {}).get("hosts") == ["smoke_runner"]
    and list_result.get("_meta", {}).get("hostvars", {}).get("smoke_runner", {}).get("ansible_host")
    == "serverd.lab.example.com"
    and host_result.get("ansible_host") == "serverd.lab.example.com"
)
award("Inventory and variables", 2, script_is_executable and valid_script, "executable supplied inventory script and valid --list/--host output")
try:
    children = inv["all"]["children"]
    validation_children = children["validation"]["children"]
except (KeyError, TypeError):
    children = {}
    validation_children = {}
merged_group = "smoke" in validation_children and "smoke_runner" not in inv_raw
award("Inventory and variables", 2, merged_group, "validation parent of the script-provided smoke group without a duplicate static host")
vars_raw = "\n".join(text(p) for p in ("group_vars/all.yml", "group_vars/webservers.yml", "host_vars/web_blue.yml", "host_vars/web_green.yml"))
award("Inventory and variables", 3, all(token in vars_raw for token in ("web_required_packages", "deployment_slot", "web_listen_address")) and "TODO" not in text("group_vars/all.yml"), "group and host variable organization")

# 3: dependencies and transformations (10)
req = text("collections/requirements.yml")
play = text("deploy.yml")
award(
    "Dependencies and data",
    2,
    all(collection in req for collection in ("ansible.posix", "ansible.utils", "community.general")),
    "required collection dependencies",
)
award("Dependencies and data", 2, contains(play, r"default\s*\(", r"default\s*\(\s*omit\s*\)"), "default and default(omit)")
award("Dependencies and data", 2, contains(play, r"\|\s*map\s*(\(|\b)", r"\|\s*difference\s*\("), "map and difference filters")
award("Dependencies and data", 2, contains(play, r"from_yaml", r"vars/releases\.yml|vars_files\s*:.*releases"), "from_yaml and release data loading")
award("Dependencies and data", 2, contains(play, r"lookup\s*\(\s*['\"]template['\"]|query\s*\(\s*['\"]template['\"]", r"smoke-request\.yml\.j2"), "template lookup for smoke data")

# 4: orchestration (16)
award("Orchestration structure", 4, all(re.search(rf"(?m)^\s*{key}\s*:", play) for key in ("pre_tasks", "post_tasks", "handlers")), "pre_tasks, post_tasks, and handlers")
award("Orchestration structure", 3, contains(play, r"listen\s*:", r"notify\s*:") and len(re.findall(r"listen\s*:", play)) >= 2, "shared handler listen topic")
award("Orchestration structure", 3, contains(play, r"hosts\s*:\s*webservers", r"become\s*:\s*true", r"block\s*:.*become\s*:\s*false"), "play privilege and unprivileged block override")
award("Orchestration structure", 3, all(re.search(rf"\b{tag}\b", play) for tag in ("validate", "packages", "deploy", "smoke")), "required tags")
package_task = re.search(r"ansible\.builtin\.(?:dnf|package)\s*:(.*?)(?=\n\s*-\s+name:|\Z)", play, re.S)
award("Orchestration structure", 3, bool(package_task and "name:" in package_task.group(1) and "loop:" not in package_task.group(1)), "single optimized package transaction")

# 5: templates and network filters (12)
web_tpl = text("templates/web.conf.j2")
smoke_tpl = text("templates/smoke-request.yml.j2")
award("Templates and filters", 4, "TODO" not in web_tpl and contains(web_tpl, r"ansible_facts|hostvars|groups", r"web_listen_address|ansible_host"), "fact/inventory-driven web template")
award("Templates and filters", 3, contains(web_tpl, r"ansible\.utils\.(?:ipaddr|ipv4|ipwrap)"), "ansible.utils network filter")
award("Templates and filters", 2, "TODO" not in smoke_tpl and contains(smoke_tpl, r"health|url|path", r"expected|status"), "structured smoke request template")
award("Templates and filters", 3, contains(play, r"ansible\.builtin\.template", r"notify\s*:") and "web.conf.j2" in play, "template deployment notifying handlers")

# 6: delegation and recovery (14)
award("Delegation workflow", 4, len(re.findall(r"delegate_to\s*:\s*['\"]?load_balancer", play)) >= 2, "delegated disable and re-enable")
award("Delegation workflow", 3, contains(play, r"delegate_to\s*:\s*['\"]?smoke_runner"), "delegated smoke check")
award("Delegation workflow", 3, contains(play, r"hostvars\s*\[\s*inventory_hostname\s*\]|ansible_delegated_vars", r"web_listen_address|ansible_host"), "original-host endpoint under delegation")
award("Delegation workflow", 4, contains(play, r"block\s*:", r"rescue\s*:", r"always\s*:") and contains(play, r"always\s*:.*(?:enable|load.?balanc)"), "re-enable recovery while exposing failure")

# 7: rolling deployment (18)
award("Rolling deployment", 5, contains(play, r"serial\s*:\s*(?:\n\s*-\s*1|\[?\s*1\s*,)"), "one-host canary serial strategy")
mfp = re.search(r"max_fail_percentage\s*:\s*(\d+)", play)
award("Rolling deployment", 4, bool(mfp and int(mfp.group(1)) < 50), "failure threshold below 50 percent")
award("Rolling deployment", 3, "ansible.builtin.meta:" in play and "flush_handlers" in play, "explicit handler flush")
positions = [play.lower().find(word) for word in ("disable", "flush_handlers", "smoke", "enable")]
award("Rolling deployment", 4, all(pos >= 0 for pos in positions) and positions == sorted(positions), "disable/deploy-flush/smoke/re-enable ordering")
award("Rolling deployment", 2, contains(play, r"block\s*:.*rescue\s*:.*always\s*:"), "batch error-handling structure")

# 8: quality (6)
award("Quality", 2, "TODO" not in "\n".join((play, inv_raw, web_tpl, smoke_tpl)), "all candidate TODOs completed")
short_modules = re.findall(r"(?m)^\s{4,}-\s+(?!name:|block:|rescue:|always:)([a-z_][\w_]*)\s*:", play)
award("Quality", 2, not short_modules and "ansible.builtin." in play, "FQCN module usage")
secret_pattern = r"(?i)(password|token|private_key|secret)\s*:\s*(?!['\"]?(?:omit|prompt|vault|\{\{|$))\S+"
all_candidate = "\n".join(text(str(p.relative_to(ROOT))) for p in ROOT.rglob("*") if p.is_file() and p.stat().st_size < 1_000_000)
award("Quality", 1, not re.search(secret_pattern, all_candidate), "no apparent embedded credentials")
award("Quality", 1, bool(re.search(r"(?m)^\s*-\s+name\s*:\s*\S+", play)) and not re.search(r"mode\s*:\s*0[0-7]{3}\b", play), "named tasks and quoted file modes")

total = sum(scores.values())
print(f"Assessment: {ROOT}")
for section, maximum in SECTIONS.items():
    print(f"  {section:<27} {scores[section]:>2}/{maximum}")
print(f"TOTAL: {total}/100 — {'PASS' if total >= 70 else 'NOT YET PASSING'}")
if notes:
    print("\nUnawarded checks:")
    for note in notes:
        print(f"- {note}")
raise SystemExit(0 if total >= 70 else 1)
