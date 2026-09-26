#!/usr/bin/env bash
set -euo pipefail

rm -rf artifacts installed_collections
mkdir -p artifacts installed_collections

ansible-galaxy collection build northstar/content_supply --output-path artifacts
artifact=$(find artifacts -maxdepth 1 -type f -name 'northstar-content_supply-*.tar.gz' -print -quit)
test -n "$artifact"
ansible-galaxy collection install "$artifact" --collections-path installed_collections
ANSIBLE_COLLECTIONS_PATH=installed_collections ansible-playbook --syntax-check consumer.yml
