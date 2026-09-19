"""Custom filters for the mock exam."""

from ansible.errors import AnsibleFilterError


def to_envvar(value):
    """TODO: convert a string into an environment variable name."""
    raise AnsibleFilterError("not implemented")


class FilterModule:
    def filters(self):
        return {"to_envvar": to_envvar}
