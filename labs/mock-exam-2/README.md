# AU374-inspired Mock Exam 2: Bluefin Web Platform

> **Red Hat lab adaptation:** managed hosts use `devops` on port `22`; the cached supported EE is RHEL 9. Use the values in this task rather than older values from external notes.

**Time:** 3 hours 30 minutes  
**Total:** 100 marks  
**Pass mark:** 70

This is a solution-free practical exercise integrating Chapters 1, 2, 5, 6, 7, and 8. Bluefin is moving a RHEL 9 web platform to a staged rolling deployment. Work only in `starter/`.

## Lab assumptions

- Run from `workstation` as the `student` user.
- Managed nodes are `servera.lab.example.com` through `serverd.lab.example.com` as `devops` over SSH port 22.
- Do not place passwords, tokens, vault secrets, or private keys in the project.
- The supported cached execution-environment image is `aap.lab.example.com/ee-supported-rhel9:latest`.
- Internet access is not required. Do not alter host SSH configuration.
- Preserve the supplied business data and logical host aliases.

## Candidate rules

- Complete every candidate `TODO` in `starter/`; supplied files without TODOs must not be rewritten.
- Use YAML playbooks and recommended Ansible practices, including FQCNs and meaningful task names.
- Your solution must be idempotent and safe to rerun.
- The grader performs static checks plus local execution of the supplied inventory script; it never connects to managed hosts.
- Run `python grade.py starter` at any time. A score of 70 or more exits 0.

## Question 1 — Project configuration (8 marks, 15 minutes)

Complete the project-local `ansible.cfg` so the mixed inventory directory is the default, roles and collections can be found locally, privilege escalation is not globally forced, host-key checking remains enabled, and the project uses five forks. Complete the minimal `ansible-navigator.yml` to use the cached image, playbook mode, and artifact output under `artifacts/`.

## Question 2 — Mixed inventory and variables (16 marks, 30 minutes)

The complete dynamic inventory script `inventory/platform_inventory.py` is supplied; do not rewrite it. Ensure it is executable, where the platform requires that, and configure/use the `inventory/` directory as the project's inventory source. Run the script with `--list` and `--host smoke_runner`, then use `ansible-inventory --graph` and `--list` to inspect the merged inventory.

Complete `inventory/hosts.yml`. Define the logical aliases `web_blue`, `web_green`, and `load_balancer`, mapping them respectively to servera, serverb, and serverc with `devops`, SSH/22. Build `webservers`, `loadbalancers`, and their parent `platform`. Also construct a `validation` parent group whose child is the script-provided `smoke` group; the merged inventory must therefore place `smoke_runner` under `validation` without duplicating it in static inventory.

Place shared connection variables, group package/service variables, and host-specific deployment metadata in the supplied `group_vars/` and `host_vars/` files. Keep aliases in play targeting and use inventory variables for real endpoints.

## Question 3 — Dependencies and data preparation (10 marks, 20 minutes)

Declare `ansible.posix`, `ansible.utils`, and `community.general` in `collections/requirements.yml`. In the deployment playbook, load `vars/releases.yml`, use `default` for a missing release channel, `default(omit)` for an optional module argument, `map` to derive artifact names, and `difference` to calculate packages still required. Parse the supplied YAML manifest with `from_yaml`, and use a `template` lookup to prepare smoke-test request data without writing an intermediate controller file.

## Question 4 — Baseline and orchestration structure (16 marks, 30 minutes)

Create a clearly named deployment play targeting the web tier. Put validation in `pre_tasks`, reporting in `post_tasks`, and service actions in handlers. Give multiple notifications a shared `listen` topic. Apply privilege escalation at play level for the web deployment, then override it for an appropriate unprivileged block. Add useful `validate`, `packages`, `deploy`, and `smoke` tags. Install the optimized package list in one package transaction rather than looping over a package task.

## Question 5 — Templates and filters (12 marks, 25 minutes)

Complete `templates/web.conf.j2` and `templates/smoke-request.yml.j2`. The deployed web configuration must use facts and inventory data, render backend IPv4 addresses with an appropriate network filter from `ansible.utils`, and avoid embedding lab credentials. Ensure configuration changes notify the shared handler topic.

## Question 6 — Delegated load-balancer workflow (14 marks, 30 minutes)

For each web host, delegate load-balancer disable and re-enable operations to the logical `load_balancer` alias. Delegate the smoke check to `smoke_runner`. Ensure delegated operations use the current web host's endpoint and do not accidentally use the delegate's variables. Re-enable a node even when deployment or smoke validation fails, while still exposing the failure.

## Question 7 — Staged rolling deployment (18 marks, 35 minutes)

Implement a staged rolling update with `serial` batches that canary one host before continuing. Configure `max_fail_percentage` so one failed host in the two-node web tier stops unsafe continuation, while preserving the intended canary behavior. Set project forks independently from batch size. For every batch, enforce this order:

1. disable the current node in the load balancer;
2. deploy and flush required handlers;
3. smoke-test the current node;
4. re-enable the node.

Use blocks and error handling so the traffic state is recovered reliably.

## Question 8 — Quality and verification (6 marks, 25 minutes)

Ensure all candidate-authored module calls use FQCNs, tasks and plays are named, file modes are quoted, command-like tasks accurately report changes, and no secrets are present. Verify inventory sources and syntax using the cached execution environment. Do not run the deployment unless the lab is disposable.

## Grading

From this directory run:

```bash
python grade.py starter
```

The grader tolerates missing or malformed candidate files, awards partial credit, prints a section breakdown, and makes no Ansible or network calls. It only executes the supplied inventory script locally.
