# Version Tagging

`patchnote-gen` can automatically suggest the next semantic version based on
your git commit history.

## How it works

The version bump logic follows [Semantic Versioning 2.0](https://semver.org/):

| Commit types present | Suggested bump |
|----------------------|----------------|
| `breaking` / `BREAKING CHANGE` | **major** |
| `feat` (and no breaking) | **minor** |
| anything else (`fix`, `chore`, …) | **patch** |

## CLI usage

```bash
# Show the suggested next version (reads latest git tag automatically)
patchnote-gen bump

# Override the current version
patchnote-gen bump --current 1.4.2

# Limit the commit range
patchnote-gen bump --since v1.4.2 --until HEAD
```

## Python API

```python
from patchnote_gen.bump import compute_next_version

result = compute_next_version(since="v1.4.2")
if result:
    current, next_ver = result
    print(f"Current: {current}  →  Next: {next_ver}")
else:
    print("Could not determine current version — no git tags found.")
```

## Version format

Tags are expected to follow `MAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH`
(with an optional pre-release suffix like `-beta.1`).

Examples of valid tags: `1.0.0`, `v2.3.1`, `0.1.0-alpha.2`
