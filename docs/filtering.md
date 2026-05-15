# Commit Filtering

The `patchnote_gen.filter` module provides utilities to narrow down commit lists before rendering changelogs.

## Usage

```python
from patchnote_gen.filter import filter_commits
from patchnote_gen.git_parser import get_commits

commits = get_commits(since="v1.0.0")

# Only include features and fixes
filtered = filter_commits(commits, include_types=["feat", "fix"])

# Exclude chores and CI commits
filtered = filter_commits(commits, exclude_types=["chore", "ci"])

# Only commits touching the 'auth' scope
filtered = filter_commits(commits, scope="auth")

# Only breaking changes
filtered = filter_commits(commits, breaking_only=True)

# Combine filters
filtered = filter_commits(
    commits,
    include_types=["feat", "fix"],
    exclude_types=["chore"],
    scope="api",
)
```

## Parameters

| Parameter | Type | Description |
|---|---|---|
| `include_types` | `list[str] \| None` | Whitelist of commit types to keep |
| `exclude_types` | `list[str] \| None` | Blacklist of commit types to drop |
| `scope` | `str \| None` | Only keep commits with this scope (case-insensitive) |
| `breaking_only` | `bool` | Only keep breaking change commits |

## Breaking Change Detection

A commit is considered a breaking change if its body contains `BREAKING CHANGE` or if the subject line uses the `!` convention (e.g. `feat!: remove endpoint`).
