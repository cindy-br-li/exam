#!/usr/bin/python3
"""Supplied dynamic inventory source for the Bluefin smoke-test host."""

import argparse
import json


HOSTVARS = {
    "smoke_runner": {
        "ansible_host": "serverd.lab.example.com",
        "ansible_user": "devops",
        "ansible_port": 22,
    }
}


def main():
    """Support the dynamic inventory --list and --host protocols."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--host")
    args = parser.parse_args()

    if args.host:
        result = HOSTVARS.get(args.host, {})
    else:
        result = {
            "_meta": {"hostvars": HOSTVARS},
            "smoke": {"hosts": ["smoke_runner"]},
        }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
