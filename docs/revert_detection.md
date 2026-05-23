# Revert Detection

`patchnote-gen` can scan a commit range and surface every **revert commit** — commits whose [Conventional Commits](https://www.conventionalcommits.org/) type is `revert`.

## How it works

1. `collect_reverts(commits)` iterates the list and keeps commits where `commit_type == "revert"`.
2. For each match, `_extract_target_sha` tries to parse the SHA of the original commit from the message body (e.g. the standard *"This reverts commit `<sha>`"* footer).
3. Results are wrapped in a `RevertReport` with `.total`, `.since`, and `.until` fields.

## CLI usage

```bash
# Plain-text summary for the last release
patchnote-reverts --since v1.2.0 --until v1.3.0

# Machine-readable JSON
patchnote-reverts --since v1.2.0 --json

# Against a non-CWD repository
patchnote-reverts --repo /path/to/repo --since v2.0.0
```

### Example output

```
Reverts (2):
  revert abc1234: reverts def5678 — Revert "feat(auth): add SSO login"
  revert 9f3c210: reverts unknown — revert accidental dependency bump
```

## Python API

```python
from patchnote_gen.git_parser import get_commits
from patchnote_gen.revert import build_revert_report, format_revert_report

commits = get_commits(since="v1.0.0")
report = build_revert_report(commits, since="v1.0.0", until="HEAD")
print(format_revert_report(report))
# or access programmatically:
for entry in report.reverts:
    print(entry.reverting.hash, "→", entry.target_sha)
```

## Notes

- Only commits typed `revert` (per Conventional Commits) are detected; bare `Revert "..."` subject lines without a type prefix are **not** matched by the type parser.
- If the target SHA cannot be extracted the field is `None` and the formatter shows `unknown`.
