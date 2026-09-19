#!/bin/bash
set -euo pipefail

source_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
install_dir="${HOME}/.local/share/ex374-lab"
bin_dir="${HOME}/.local/bin"

mkdir -p "$install_dir" "$bin_dir"
rm -rf "$install_dir/labs"
cp -a "$source_dir/labs" "$install_dir/labs"
cp "$source_dir/labs.json" "$install_dir/labs.json"
install -m 0755 "$source_dir/exlab.py" "$bin_dir/exlab"

printf 'Installed EX374 practice labs.\n'
printf 'Run: %s list\n' "$bin_dir/exlab"
if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
    printf 'Add %s to PATH, or run it with the full path shown above.\n' "$bin_dir"
fi
