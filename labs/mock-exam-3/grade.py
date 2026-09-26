#!/usr/bin/env python3
"""Offline, non-destructive structural grader for Mock Exam 3."""
from __future__ import annotations
import configparser
import re
import sys
from pathlib import Path

S = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent / "starter"
try:
    import yaml
except Exception:
    yaml = None

def text(path):
    try: return (S / path).read_text(encoding="utf-8")
    except (OSError, UnicodeError): return ""
def yml(path):
    try: return yaml.safe_load(text(path)) if yaml else None
    except Exception: return None
results = []
def section(name, maximum, checks):
    earned = sum(p for p, ok, _ in checks if ok)
    results.append((name, earned, maximum, [label for _, ok, label in checks if not ok]))

cfg_text = text("ansible.cfg"); cfg = configparser.ConfigParser(interpolation=None)
try: cfg.read_string(cfg_text); cfg_ok = True
except configparser.Error: cfg_ok = False
servers = cfg.get("galaxy", "server_list", fallback="") if cfg_ok else ""
section("Hub configuration", 8, [(2, cfg_ok and len(servers.split(",")) >= 2, "server priority"), (2, "galaxy_server.private_hub" in cfg_text and "galaxy_server.galaxy" in cfg_text, "server sections"), (2, bool(re.search(r"token\s*=\s*(\$|env)", cfg_text, re.I)), "indirect token"), (2, bool(re.search(r"validate_certs\s*=\s*(true|yes)", cfg_text, re.I)), "TLS validation")])

req = yml("collections/requirements.yml"); items = req.get("collections", []) if isinstance(req, dict) else []
def pinned(name): return any(isinstance(x, dict) and x.get("name") == name and re.search(r"\d", str(x.get("version", ""))) for x in items)
section("Collection requirements", 6, [(2, pinned("ansible.posix"), "pinned ansible.posix"), (2, pinned("community.general"), "pinned community.general"), (2, len(items) >= 3 and any(isinstance(x, dict) and x.get("source") for x in items) and "token" not in text("collections/requirements.yml").lower(), "private source without token")])

defaults = yml("northstar/content_supply/roles/content_publisher/defaults/main.yml"); spec = yml("northstar/content_supply/roles/content_publisher/meta/argument_specs.yml")
tasks = text("northstar/content_supply/roles/content_publisher/tasks/main.yml"); template = text("northstar/content_supply/roles/content_publisher/templates/release-summary.j2")
options = (((spec or {}).get("argument_specs") or {}).get("main") or {}).get("options", {}) if isinstance(spec, dict) else {}
section("Supplied role migration", 20, [(4, isinstance(defaults, dict) and len(defaults) >= 6, "role defaults migrated"), (4, isinstance(options, dict) and len(options) >= 6, "argument specification migrated"), (4, "ansible.builtin.copy:" in tasks and "ansible.builtin.template:" in tasks, "FQCN tasks"), (4, "force: false" in tasks.lower() and "release-summary.j2" in tasks, "idempotent supplied behavior"), (4, "{{" in template and "TODO" not in template and ("for " in template or "join" in template), "template migrated")])

galaxy = yml("northstar/content_supply/galaxy.yml"); runtime = yml("northstar/content_supply/meta/runtime.yml"); galaxy = galaxy if isinstance(galaxy, dict) else {}; deps = galaxy.get("dependencies", {})
section("Collection metadata", 12, [(3, galaxy.get("namespace") == "northstar" and galaxy.get("name") == "content_supply" and str(galaxy.get("version")) == "1.0.0", "identity/version"), (3, all(galaxy.get(k) for k in ("readme", "authors", "description", "license", "tags")), "complete metadata"), (3, isinstance(deps, dict) and any(re.search(r"[<>=~]\s*\d", str(v)) for v in deps.values()), "versioned dependency"), (3, isinstance(runtime, dict) and bool(re.search(r">=\s*2\.(1[5-9]|[2-9]\d)", str(runtime.get("requires_ansible", "")))), "runtime requirement")])

script = text("build_install.sh"); consumer = text("consumer.yml"); consumer_data = yml("consumer.yml")
section("Build, install, consume", 14, [(2, "set -euo pipefail" in script, "strict mode"), (3, "ansible-galaxy collection build" in script and "artifacts" in script, "build artifact"), (3, "ansible-galaxy collection install" in script and "installed_collections" in script, "local install"), (3, "--syntax-check" in script and "ANSIBLE_COLLECTIONS_PATH" in script, "syntax check installed content"), (3, isinstance(consumer_data, list) and "hosts: localhost" in consumer and "northstar.content_supply.content_publisher" in consumer, "FQCN localhost consumer")])

ee = yml("execution-environment.yml"); ee = ee if isinstance(ee, dict) else {}; ee_text = text("execution-environment.yml"); dependencies = ee.get("dependencies", {})
ee_req = text("ee/requirements.yml")
section("Execution environment", 25, [(3, ee.get("version") == 3, "schema v3"), (4, "rhel9" in ee_text.lower() or "ubi9" in ee_text.lower(), "RHEL 9 base"), (4, isinstance(dependencies, dict) and all(k in dependencies for k in ("galaxy", "python", "system")), "all dependency inputs"), (3, "northstar.content_supply" in ee_req, "packaged collection dependency"), (3, all(text(p).strip() and "TODO" not in text(p) for p in ("ee/requirements.yml", "ee/requirements.txt", "ee/bindep.txt")), "populated inputs"), (3, isinstance(ee.get("options"), dict) and ee["options"].get("package_manager_path") == "/usr/bin/dnf", "dnf option"), (2, "corporate-ca.crt.example" in ee_text, "CA build file"), (3, "update-ca-trust" in ee_text and "/etc/pki/ca-trust/source/anchors" in ee_text, "CA trust step")])

evidence = text("ee-evidence.md"); low = evidence.lower()
section("Builder context and image inspection", 15, [(3, "ansible-builder create" in evidence and "--output-filename" in evidence, "create context command"), (3, "ansible-builder build" in evidence and bool(re.search(r"(?:-t|--tag).*:[\w.-]+", evidence)) and ":latest" not in evidence, "tagged build command"), (3, "containerfile" in low and "_build/requirements.yml" in low and "bindep" in low, "context inspection facts"), (3, "podman image inspect" in evidence and all(x in low for x in ("digest", "architecture", "labels", "created")), "image inspection facts"), (3, "/etc/redhat-release" in evidence and "ansible-galaxy collection list" in evidence and "ansible-doc -t role" in evidence and "cpu" not in low and "memory" not in low and "disk" not in low, "runtime validation without resource plan")])

total = sum(x[1] for x in results); maximum = sum(x[2] for x in results)
print("Mock Exam 3 structural grade")
for name, earned, possible, notes in results:
    print(f"{name}: {earned}/{possible}")
    if notes: print("  Missing: " + "; ".join(notes))
print(f"TOTAL: {total}/{maximum}  PASS MARK: 70")
print("PASS" if total >= 70 else "NOT YET PASSING")
sys.exit(0 if total >= 70 else 1)
