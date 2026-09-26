# Mock Exam 4 — Branch Office Access

> **Red Hat lab adaptation:** managed hosts use `devops` on port `22`; the cached supported EE is RHEL 9. Use the values in this task rather than older values from external notes.

**Time:** 3 hours · **Total:** 100 marks · **Pass:** 70 marks

Work only in `starter/`. This exam tests Git, Ansible configuration,
inventories, lookups, loops, and idempotent Linux account management. It does
not require Vault creation, Controller config-as-code, or Python development.

## Rules

- Do not store passwords, tokens, private keys, or other usable credentials.
- Use FQCNs, idempotent modules, meaningful task names, and quoted file modes.
- Do not edit `grade.py` or this README.
- Run `python grade.py` from the mock-exam directory for partial-credit marking.

## Tasks

### 1. Git workflow — 10 marks

Initialize `starter/` as a Git repository. Configure your Git identity, create
a descriptive feature branch, and make at least two meaningful commits.
Complete `.gitignore` for Navigator logs, playbook artifacts, retry files, and
common local secret/environment files.

### 2. Ansible configuration — 10 marks

Complete `ansible.cfg` with the local inventory, local role and collection
paths, remote user `devops`, host-key checking enabled, retry files disabled,
and at least 10 forks. Configure sudo privilege escalation defaults but do not
enable become globally.

### 3. Navigator configuration — 5 marks

Complete a minimal `ansible-navigator.yml` using stdout mode, disabled playbook
artifacts, and `aap.lab.example.com/ee-supported-rhel9:latest` with pull policy
`missing`. Do not paste generated effective settings.

### 4. Inventory — 10 marks

Complete `inventory.ini` with `branch01` and `branch02` in `managed`, a parent
group named `branch_offices`, and group connection variables `ansible_user`
`devops` and `ansible_port` `22`. Preserve the supplied host addresses.

### 5. External account data — 10 marks

Complete `vars/groups.yml` with at least two groups and three users, including
group membership lists. Complete `files/users.txt` with the same three unique
user names and comments in `name|comment` format. Do not include passwords.
Public-key inputs are supplied under `files/authorized_keys/`.

### 6. Groups and users — 30 marks

Complete `playbooks/manage_users.yml` for `managed`. Load the external YAML,
read user records with the `lines` lookup, and create groups and users with
`ansible.builtin.group` and `ansible.builtin.user`. Generate password hashes
with the password lookup and `password_hash`; protect that task with
`no_log: true`. Apply become only to tasks that need it.

### 7. Membership and authorized keys — 15 marks

Use `subelements` to apply group memberships from `managed_users`. Use the
`file` lookup and `ansible.posix.authorized_key` to install each supplied public
key. Keep both operations idempotent.

### 8. Execution controls — 10 marks

Tag group, user, membership, and key tasks with useful `groups`, `users`, and
`keys` tags. Verify the playbook without changing hosts:

```bash
ansible-playbook playbooks/manage_users.yml --syntax-check
ansible-playbook playbooks/manage_users.yml --list-tasks
ansible-playbook playbooks/manage_users.yml --list-tags
```

## Marking

```bash
python grade.py
```
