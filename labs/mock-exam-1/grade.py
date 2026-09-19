#!/usr/bin/env python3
"""Score EX374 Mock Exam 1 out of 100 without changing the environment."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import yaml


ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
score = 0
results: list[tuple[bool, int, str]] = []


def read(relative: str) -> str:
    try:
        return (ROOT / relative).read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


def load(relative: str):
    try:
        return yaml.safe_load(read(relative)) or {}
    except yaml.YAMLError:
        return {}


def award(label: str, points: int, passed: bool) -> None:
    global score
    results.append((passed, points, label))
    if passed:
        score += points


inventory = load("inventory/hosts.yml")
children = inventory.get("all", {}).get("children", {}) if isinstance(inventory, dict) else {}
expected_hosts = {
    "webservers": {"web1": "servera.lab.example.com", "web2": "serverb.lab.example.com"},
    "databases": {"db1": "serverc.lab.example.com"},
    "backup": {"backup1": "serverd.lab.example.com"},
}
hosts_ok = True
for group, hosts in expected_hosts.items():
    actual = children.get(group, {}).get("hosts", {})
    hosts_ok &= all(actual.get(name, {}).get("ansible_host") == target for name, target in hosts.items())
parents_ok = (
    set(children.get("production", {}).get("children", {})) == {"webservers", "databases"}
    and set(children.get("development", {}).get("children", {})) == {"backup"}
)
award("Q1 inventory aliases and parent groups", 8, hosts_ok and parents_ok)

connection = load("group_vars/all/connection.yml")
award("Q1 common SSH variables", 4, connection.get("ansible_user") == "devops" and connection.get("ansible_port") == 22)
packages = load("group_vars/webservers/packages.yml")
award("Q1 web package variables", 4, packages.get("web_packages") == ["httpd", "mod_ssl"])
web1 = load("host_vars/web1/app.yml")
web2 = load("host_vars/web2/app.yml")
award(
    "Q1 per-host application variables",
    4,
    web1.get("app_name") == web2.get("app_name") == "portal"
    and web1.get("http_port") == 8080
    and web2.get("http_port") == 8081,
)

site = load("site.yml")
play = site[0] if isinstance(site, list) and site and isinstance(site[0], dict) else {}
tasks = play.get("tasks", []) if isinstance(play.get("tasks"), list) else []
award("Q2 webservers play with play-level become", 4, play.get("hosts") == "webservers" and play.get("become") is True)
task_keys = {key for task in tasks if isinstance(task, dict) for key in task}
award(
    "Q2 required FQCN modules",
    6,
    {"ansible.builtin.dnf", "ansible.builtin.template", "ansible.builtin.service", "ansible.builtin.debug"}.issubset(task_keys),
)
tags = set()
for task in tasks:
    value = task.get("tags", []) if isinstance(task, dict) else []
    tags.update([value] if isinstance(value, str) else value)
award("Q2 packages/deploy/service/always tags", 6, {"packages", "deploy", "service", "always"}.issubset(tags))
template = read("templates/index.html.j2")
award("Q2 template uses all required variables", 4, all(name in template for name in ("app_name", "inventory_hostname", "http_port")))

expected_transform = {
    "names": ["Alice", "Bob", "Charlie", "Diana"],
    "engineering_names": ["Alice", "Charlie"],
    "total_salary": 375000,
    "python_users": ["Alice", "Charlie", "Diana"],
    "environment": "prod",
    "renamed_server": "webserver-prod-eu-west-01.example.com",
    "backup_path": "/tmp/backup",
}
award("Q3 generated transformation results", 12, load("artifacts/transform-results.yml") == expected_transform)
transform_source = read("data_transform.yml")
award(
    "Q3 required data transformation filters",
    8,
    all(token in transform_source for token in ("map(", "selectattr(", "sum", "regex_search", "regex_replace", "default(")),
)

delegation_source = read("delegation.yml")
award(
    "Q4 delegation and run-once semantics",
    8,
    delegation_source.count("delegate_to: localhost") >= 3
    and "run_once: true" in delegation_source,
)
report_dir = Path("/tmp/mock-exam-reports")
reports_ok = all((report_dir / name).is_file() for name in ("web1.txt", "web2.txt", "summary.txt"))
if reports_ok:
    reports_ok = "web1" in (report_dir / "web1.txt").read_text(errors="ignore") and "web2" in (report_dir / "web2.txt").read_text(errors="ignore")
award("Q4 delegated reports exist on workstation", 7, reports_ok)

filter_path = ROOT / "ansible_collections/exam/utilities/plugins/filter/format_utils.py"
filter_ok = False
registration_ok = False
try:
    spec = importlib.util.spec_from_file_location("mock_format_utils", filter_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    filter_ok = module.to_envvar("app.db host-1") == "APP_DB_HOST_1" and module.to_envvar("3tier") == "_3TIER"
    try:
        module.to_envvar(123)
    except Exception as error:  # The exact class is checked by its name to avoid coupling the grader.
        filter_ok &= error.__class__.__name__ == "AnsibleFilterError"
    else:
        filter_ok = False
    registration_ok = module.FilterModule().filters().get("to_envvar") is module.to_envvar
except Exception:
    pass
award("Q5 to_envvar filter behavior", 8, filter_ok)
galaxy = load("ansible_collections/exam/utilities/galaxy.yml")
runtime = load("ansible_collections/exam/utilities/meta/runtime.yml")
award(
    "Q5 filter registration and collection metadata",
    7,
    registration_ok
    and galaxy.get("namespace") == "exam"
    and galaxy.get("name") == "utilities"
    and str(galaxy.get("version")) == "1.0.0"
    and runtime.get("requires_ansible") == ">=2.15.0",
)

ee = load("custom-ee/execution-environment.yml")
award(
    "Q6 execution environment v3 definition",
    6,
    ee.get("version") == 3
    and ee.get("images", {}).get("base_image", {}).get("name") == "aap.lab.example.com/ee-supported-rhel9:latest"
    and ee.get("options", {}).get("package_manager_path") == "/usr/bin/dnf",
)
requirements = load("custom-ee/requirements.yml").get("collections", [])
collection_names = {item.get("name") if isinstance(item, dict) else item for item in requirements}
award(
    "Q6 collection, Python, and RPM dependencies",
    4,
    "exam.utilities" in collection_names
    and "netaddr" in read("custom-ee/requirements.txt").split()
    and "jq [platform:rpm]" in read("custom-ee/bindep.txt"),
)

for passed, points, label in results:
    print(f"{'PASS' if passed else 'FAIL'} [{points:2d}] {label}")
print(f"\nSCORE: {score}/100 — {'PASS' if score >= 70 else 'NOT YET PASSING'}")
raise SystemExit(0 if score >= 70 else 1)
