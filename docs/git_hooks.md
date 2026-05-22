# Git Hook Integration

`patchnote-gen` can automatically update your changelog on every commit by
installing a git hook into your repository.

## Supported Hook Types

| Hook | When it runs |
|------|--------------|
| `post-commit` | After each commit is recorded (default) |
| `commit-msg` | When the commit message is being finalised |

## Installing a Hook

```bash
# Install the default post-commit hook
patchnote-hook install

# Install a commit-msg hook instead
patchnote-hook install --type commit-msg

# Install into a specific repo
patchnote-hook install --repo /path/to/repo
```

The command writes a small shell script to `.git/hooks/<hook-type>` and marks
it executable. If a hook file already exists, patchnote-gen appends its lines
rather than overwriting the file.

## Checking Hook Status

```bash
patchnote-hook status
# post-commit: installed
```

Exits with code `0` if installed, `1` if not.

## Uninstalling a Hook

```bash
patchnote-hook uninstall
```

Only the lines added by patchnote-gen are removed. Any pre-existing hook
content is preserved. If the file becomes empty after removal it is deleted.

## What the Hook Does

The installed script runs:

```sh
patchnote-gen --since HEAD~1 --output CHANGELOG.md --prepend
```

This generates a changelog entry for the latest commit and prepends it to
`CHANGELOG.md`. Adjust the command by editing `.git/hooks/post-commit`
directly after installation.

## Programmatic Usage

```python
from patchnote_gen.hook import install_hook, uninstall_hook, hook_status

install_hook("post-commit")          # install
hook_status("post-commit")           # True / False
uninstall_hook("post-commit")        # remove
```
