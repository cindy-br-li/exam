# Mock Exam 3: Collections and Execution Environments

> **Red Hat lab adaptation:** managed hosts use `devops` on port `22`; the cached supported EE is RHEL 9. Use the values in this task rather than older values from external notes.

**Time:** 4 hours  
**Total:** 100 marks  
**Pass:** 70 marks

Package supplied Northstar role content as an Ansible collection and define a custom execution environment in `starter/`. Hub and registries may be unavailable, so the work must remain structurally gradeable offline.

## Rules

- Work only in `starter/`; do not modify `grade.py`.
- Do not add credentials or real certificates.
- YAML must parse. Use FQCNs in playbooks and role tasks.
- Developing modules, plug-ins, and filters is outside scope. Do not add or test custom Python content.
- Run `python3 grade.py` from this directory. The grader does not build an image.

## Tasks and marking

### 1. Private automation hub configuration (8 marks)

Complete `ansible.cfg` with public Galaxy and private Hub servers, server priority, an indirectly sourced token, and TLS validation.

### 2. Collection dependencies (6 marks)

Complete `collections/requirements.yml` with pinned `ansible.posix` and `community.general` versions plus a private collection from Hub, without embedded authentication.

### 3. Package the supplied role as a collection (20 marks)

Migrate `supplied_roles/content_publisher` into `northstar/content_supply/roles/content_publisher`. Preserve its defaults, argument specification, tasks, and template. Ensure tasks use FQCNs and repeated execution is idempotent. Do not modify or replace the role with custom Python content.

### 4. Collection metadata (12 marks)

Complete `galaxy.yml`, `README.md`, and `meta/runtime.yml`. Use namespace `northstar`, name `content_supply`, version `1.0.0`, complete descriptive metadata, a versioned collection dependency, and a suitable `requires_ansible` constraint.

### 5. Build, install, and consume (14 marks)

Complete `build_install.sh` with strict shell mode. Build the collection into `artifacts/`, install its artifact into `installed_collections/`, then syntax-check `consumer.yml` with that collection path. Complete the localhost consumer so it invokes the role as `northstar.content_supply.content_publisher`. Do not publish.

### 6. Custom execution environment definition (25 marks)

Complete `execution-environment.yml` using schema version 3 and a supported RHEL 9 EE base image. Reference the supplied Galaxy, Python, and system dependency files; populate those files; set the package manager to `/usr/bin/dnf`; and copy the placeholder corporate CA with `additional_build_files` before running `update-ca-trust`. Also include the packaged collection in the EE collection requirements. The CA file must remain a placeholder.

### 7. Create/build context and image inspection (15 marks)

Complete `ee-evidence.md` with:

- an explicit non-`latest` image tag;
- exact `ansible-builder create` and `ansible-builder build` commands;
- facts to inspect in the generated context (`Containerfile`, `_build/requirements.yml`, Python and bindep inputs);
- `podman image inspect` facts for image ID/digest, architecture, OS, labels, and creation time;
- runtime commands that validate the RHEL release, installed collections, and the role with `ansible-doc`.

Record `NOT RUN - offline` when commands cannot be run. CPU, memory, disk planning and evidence-retention deliverables are not required.

## Suggested verification

```bash
python3 grade.py
ansible-galaxy collection build starter/northstar/content_supply --output-path /tmp/mock3-artifacts
```

The grader awards partial credit and preserves a total of 100 marks.
