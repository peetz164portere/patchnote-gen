# Diff Statistics

`patchnote-gen` can collect and display per-commit diff statistics alongside
your changelog, giving you a quick sense of the *size* of a release.

## Module: `patchnote_gen.diff_stats`

### `DiffStat`

A dataclass holding statistics for a single commit:

| Field | Type | Description |
|---|---|---|
| `sha` | `str` | Full commit SHA |
| `files_changed` | `int` | Number of files touched |
| `insertions` | `int` | Lines added |
| `deletions` | `int` | Lines removed |
| `files` | `list[str]` | Paths of changed files |
| `net_lines` | `int` *(property)* | `insertions - deletions` |

### `get_diff_stat(sha, repo_path=".")`

Runs `git show --stat` for a single SHA and returns a `DiffStat`, or `None`
if the command fails.

### `get_diff_stats(shas, repo_path=".")`

Convenience wrapper that calls `get_diff_stat` for each SHA in the list and
returns only the successful results.

### `summarise_stats(stats)`

Aggregates a list of `DiffStat` objects into a summary dictionary:

```python
{
    "total_commits": 4,
    "total_files_changed": 11,
    "total_insertions": 87,
    "total_deletions": 23,
    "net_lines": 64,
}
```

## CLI: `patchnote-diff`

```
usage: patchnote-diff [--since REF] [--until REF] [--summary] [--repo PATH]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--since` | *(none)* | Start ref or tag |
| `--until` | `HEAD` | End ref or tag |
| `--summary` | off | Print only the aggregated totals |
| `--repo` | `.` | Path to the git repository |

### Example

```bash
# Show per-commit stats between two tags
patchnote-diff --since v1.2.0 --until v1.3.0

# Show only the summary
patchnote-diff --since v1.2.0 --summary
```

Sample output:

```
abc1234  2 file(s) changed, +11 -6
def5678  1 file(s) changed, +3 -0

Total: 2 commit(s), 3 file(s) changed, +14 -6 (net +8)
```
