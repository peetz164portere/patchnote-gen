"""Parse git commit history into structured commit objects."""

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Commit:
    hash: str
    short_hash: str
    author: str
    email: str
    date: datetime
    subject: str
    body: str = ""
    tags: List[str] = field(default_factory=list)

    @property
    def commit_type(self) -> Optional[str]:
        """Extract conventional commit type (feat, fix, chore, etc.)."""
        if ":" in self.subject:
            prefix = self.subject.split(":")[0].strip()
            # handle scoped commits like feat(auth)
            base = prefix.split("(")[0].strip()
            return base if base.isalpha() else None
        return None

    @property
    def scope(self) -> Optional[str]:
        """Extract conventional commit scope."""
        if ":" in self.subject:
            prefix = self.subject.split(":")[0].strip()
            if "(" in prefix and ")" in prefix:
                return prefix[prefix.index("(") + 1 : prefix.index(")")]
        return None

    @property
    def message(self) -> str:
        """Return subject without the conventional commit prefix."""
        if ":" in self.subject and self.commit_type:
            return self.subject.split(":", 1)[1].strip()
        return self.subject


def get_commits(repo_path: str = ".", since_tag: Optional[str] = None) -> List[Commit]:
    """Fetch commits from a git repository."""
    separator = "||COMMIT_SEP||"
    fmt = f"%H{separator}%h{separator}%an{separator}%ae{separator}%aI{separator}%s{separator}%b{separator}END"

    cmd = ["git", "-C", repo_path, "log", f"--format={fmt}"]
    if since_tag:
        cmd.append(f"{since_tag}..HEAD")

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    raw = result.stdout.strip()

    if not raw:
        return []

    commits = []
    for entry in raw.split("END"):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(separator)
        if len(parts) < 7:
            continue
        commits.append(
            Commit(
                hash=parts[0].strip(),
                short_hash=parts[1].strip(),
                author=parts[2].strip(),
                email=parts[3].strip(),
                date=datetime.fromisoformat(parts[4].strip()),
                subject=parts[5].strip(),
                body=parts[6].strip(),
            )
        )
    return commits
