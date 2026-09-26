# EX374 Mock Exam 1 — Core Automation

> **Red Hat lab adaptation:** managed hosts use `devops` on port `22`; the cached supported EE is RHEL 9. Use the values in this task rather than older values from external notes.

**Time limit:** 2 hours 30 minutes · **Pass mark:** 70/100 · **No internet**

Work only inside the directory created by `exlab start mock-exam-1`. Use
`ansible-doc` and locally installed documentation. Use FQCNs for modules.

## Environment

| Logical host | Connection target | Group |
|---|---|---|
| `web1` | `servera.lab.example.com` | `webservers` |
| `web2` | `serverb.lab.example.com` | `webservers` |
| `db1` | `serverc.lab.example.com` | `databases` |
| `backup1` | `serverd.lab.example.com` | `backup` |

All managed hosts use SSH user `devops`, port `22`, and passwordless sudo.

## Q1 — Inventory and variables (20 marks)

Complete `inventory/hosts.yml` with the four logical hosts and connection
targets above. Create parent group `production` containing `webservers` and
`databases`. Keep `backup` under `development`.

Complete these variable files:

- `group_vars/all/connection.yml`: `ansible_user: devops`, `ansible_port: 22`
- `group_vars/webservers/packages.yml`: `web_packages: [httpd, mod_ssl]`
- `host_vars/web1/app.yml`: `app_name: portal`, `http_port: 8080`
- `host_vars/web2/app.yml`: `app_name: portal`, `http_port: 8081`

Validation:

```bash
ansible-inventory --graph
ansible-inventory --host web1
ansible-inventory --host web2
```

## Q2 — Tagged deployment playbook (20 marks)

Complete `site.yml` targeting `webservers` with play-level `become: true`:

1. Install `web_packages` with `ansible.builtin.dnf`, tag `packages`.
2. Deploy `templates/index.html.j2` to `/var/www/html/index.html` with
   `ansible.builtin.template`, tag `deploy`.
3. Ensure `httpd` is enabled and started with `ansible.builtin.service`, tag
   `service`.
4. Add an `always`-tagged debug task showing `inventory_hostname`.

The template must include `app_name`, `inventory_hostname`, and `http_port`.

Validate safely before applying:

```bash
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml --list-tags
ansible-playbook site.yml --check --tags packages,deploy
```

## Q3 — Data transformation (20 marks)

Complete `data_transform.yml`, using `vars/employees.yml`, to write
`artifacts/transform-results.yml` with exactly these keys and values:

```yaml
names: [Alice, Bob, Charlie, Diana]
engineering_names: [Alice, Charlie]
total_salary: 375000
python_users: [Alice, Charlie, Diana]
environment: prod
renamed_server: webserver-prod-eu-west-01.example.com
backup_path: /tmp/backup
```

Use the requested filters in the playbook: `map`, `selectattr`, `sum`,
`regex_search`, `regex_replace`, and `default`. Run it before grading:

```bash
ansible-playbook data_transform.yml
```

## Q4 — Delegation (15 marks)

Complete `delegation.yml` targeting `webservers`. It must gather facts and:

1. Delegate creation of `/tmp/mock-exam-reports` to `localhost` once.
2. Delegate one report per host to `localhost` at
   `/tmp/mock-exam-reports/<inventory_hostname>.txt` containing the inventory
   hostname, default IPv4 address, and distribution.
3. Use `run_once: true` with `delegate_to: localhost` to create
   `/tmp/mock-exam-reports/summary.txt` listing all webservers.

Run the playbook before grading.

## Q5 — Package a supplied role in a collection (15 marks)

The complete role `supplied_roles/system_report` is provided. Copy it to
`ansible_collections/exam/utilities/roles/system_report` without rewriting its
tasks. Complete the collection metadata with version `1.0.0` and
`requires_ansible: ">=2.15.0"`.

Complete `collection_test.yml` as a localhost play that uses the role by its
FQCN, `exam.utilities.system_report`. Run the playbook and verify that it
creates `/tmp/ex374-system-report.txt`, then build the collection:

```bash
ansible-playbook collection_test.yml
ansible-galaxy collection build ansible_collections/exam/utilities \
  --output-path artifacts
```

## Q6 — Execution environment definition (10 marks)

Complete the files under `custom-ee/`:

- schema `version: 3`;
- base image `aap.lab.example.com/ee-supported-rhel9:latest`;
- collection dependency `exam.utilities`;
- Python dependency `netaddr`;
- system dependency `jq [platform:rpm]`;
- `options.package_manager_path: /usr/bin/dnf`.

Validate without requiring an online build:

```bash
ansible-builder create -f custom-ee/execution-environment.yml
```

## Marking

```bash
exlab grade
```

The grader awards partial credit and prints each failed criterion. A score of
70 or above passes. Controller and private Hub work are intentionally excluded
because those services are not available in the current lab session.
