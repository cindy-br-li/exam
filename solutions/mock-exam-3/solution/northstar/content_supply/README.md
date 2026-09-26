# Northstar Content Supply

> **Red Hat lab adaptation:** managed hosts use `devops` on port `22`; the cached supported EE is RHEL 9. Use the values in this task rather than older values from external notes.

The `northstar.content_supply` collection packages the supplied `content_publisher` role for installation and FQCN-based use. It targets Ansible Core 2.15 or later and depends on `ansible.posix` 2.x or later.

```yaml
roles:
  - role: northstar.content_supply.content_publisher
```
