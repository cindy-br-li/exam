# EE build context and image validation

- Image tag: `aap.lab.example.com/system/northstar-content-ee:1.0.0`

## Create and build

```bash
ansible-builder create -f execution-environment.yml --output-filename Containerfile --context build-context
ansible-builder build -f execution-environment.yml --context build-context \
  -t aap.lab.example.com/system/northstar-content-ee:1.0.0
```

In `build-context`, inspect `Containerfile` for the selected base image and build stages. Inspect `_build/requirements.yml` for `northstar.content_supply`, `_build/requirements.txt` for the pinned Python package, and `_build/bindep.txt` for the RPM dependency.

## Image inspection and runtime validation

```bash
podman image inspect aap.lab.example.com/system/northstar-content-ee:1.0.0 \
  --format 'ID={{.Id}} Digest={{.Digest}} Architecture={{.Architecture}} OS={{.Os}} Created={{.Created}} Labels={{json .Labels}}'
podman run --rm aap.lab.example.com/system/northstar-content-ee:1.0.0 cat /etc/redhat-release
podman run --rm aap.lab.example.com/system/northstar-content-ee:1.0.0 ansible-galaxy collection list
podman run --rm aap.lab.example.com/system/northstar-content-ee:1.0.0 \
  ansible-doc -t role northstar.content_supply.content_publisher
```

`NOT RUN - offline`: context generation and image build/inspection commands are documented for execution when the classroom registry and container engine are available.
