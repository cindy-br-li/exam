# AU374 Mock Exam Coverage

The mock exams recombine the AU374 v2.5 lab behaviours into new scenarios.
They do not copy the course exercises or claim to reproduce live exam tasks.

| AU374 practical area | Mock coverage |
|---|---|
| Navigator execution, stdout mode and EE selection | Mock 1, 2 and 4 |
| Git branching, commits, ignored logs/artifacts and persisted projects | Mock 4 |
| Recommended project structure, FQCNs, native modules, naming and lint-ready YAML | All mocks |
| Role defaults, metadata and argument specifications | Mock 3 |
| Private Hub server priority and collection requirements | Mock 3 |
| Selecting content-capable EEs and documenting local validation | Mock 2 and 3 |
| `ansible.cfg` precedence, forks and scoped privilege escalation | Mock 2 and 4 |
| Minimal `ansible-navigator.yml`, artifact settings and avoiding captured effective settings | Mock 2 and 4 |
| Static YAML inventory and logical `ansible_host` aliases | Mock 1 and 2 |
| Mixed inventory directory using a supplied executable dynamic inventory script | Mock 2 |
| Host/group variable files and parent/child groups | Mock 1 and 2 |
| `pre_tasks`, `post_tasks`, handlers and shared `listen` topics | Mock 2 |
| Tags, selective execution and unprivileged task/block overrides | Mock 1 and 2 |
| Execution profiling concepts and optimized package-list transactions | Mock 2 |
| `default`, `default(omit)`, `map`, `difference`, lookups and `from_yaml` | Mock 1 and 2 |
| External group/user data with file and lines lookups | Mock 4 |
| Password lookup/hash, `subelements`, groups, users and authorized keys | Mock 4 |
| IPv4/network transformations | Mock 2 |
| Delegated control-node reports and `run_once` | Mock 1 |
| Delegated load-balancer operations and smoke tests | Mock 2 |
| Forks, staged `serial` batches and `max_fail_percentage` | Mock 2 |
| Recovery-safe rolling updates using blocks and delegated traffic control | Mock 2 |
| Collection metadata, runtime requirements and collection dependencies | Mock 1 and 3 |
| Migrating supplied roles into collections and consuming them by FQCN | Mock 1 and 3 |
| Collection role, template, defaults and argument specification | Mock 3 |
| Collection build, local install and FQCN consumer playbook | Mock 3 |
| Builder v3 Galaxy/Python/system dependencies and package manager | Mock 1 and 3 |
| CA trust through additional build files/steps | Mock 3 |
| Explicit EE tags, inspection, validation and honest offline evidence | Mock 3 |
| Comprehensive inventory/optimization/rolling-update review | Mock 2 |
| Git, configuration, inventories, lookups and remote user management | Mock 4 |

## Exam sequence

1. **Mock 1 — Core Automation:** inventory, tagged deployment, transformations,
   delegation, supplied-role collection packaging and an EE definition.
2. **Mock 2 — Bluefin Web Platform:** supplied dynamic inventory, configuration,
   filters, handlers, performance and recovery-safe rolling updates.
3. **Mock 3 — Content Supply Chain:** private content configuration, collection
   role packaging, collection build/install and custom EE design.
4. **Mock 4 — Branch Office Access:** Git/configuration, inventory, lookups,
   remote users/groups, membership and authorized keys.

Private Hub publication and Controller UI work require services that are absent
from this Red Hat lab and are therefore not simulated with unsupported
config-as-code tasks. Candidates should still perform live validation whenever
the relevant official course environment provides those services.
