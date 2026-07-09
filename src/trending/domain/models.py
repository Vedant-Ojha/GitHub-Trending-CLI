from dataclasses import dataclass, field
from typing import List


@dataclass
class Issue:
    """
    Represents a single GitHub issue.
    Used for 'good first issue' display when --contribute flag is set.
    """
    number: int
    title: str
    url: str
    labels: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        label_str = ", ".join(self.labels) if self.labels else "No labels"
        return (
            f"  #{self.number}: {self.title}\n"
            f"    Labels: {label_str}\n"
            f"    URL: {self.url}"
        )


@dataclass
class Repository:
    """
    Represents a GitHub repository with optional list of good first issues.
    Core domain entity passed through all layers.
    """
    name: str           # e.g. "owner/repo-name"
    description: str    # Repo description (may be empty string)
    stars: int          # stargazers_count from API
    language: str       # Primary programming language (may be None)
    url: str            # html_url from API
    issues: List[Issue] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        """Short display name without owner prefix."""
        parts = self.name.split("/")
        return parts[1] if len(parts) == 2 else self.name

    @property
    def owner(self) -> str:
        """Repository owner (user or org name)."""
        parts = self.name.split("/")
        return parts[0] if len(parts) == 2 else ""

    @property
    def language_display(self) -> str:
        """Safe language string — never None in display."""
        return self.language or "Unknown"

    @property
    def description_display(self) -> str:
        """Safe description — never empty in display."""
        return self.description or "No description provided"

    def has_issues(self) -> bool:
        """Check if this repo has any good first issues loaded."""
        return len(self.issues) > 0

    def __str__(self) -> str:
        return (
            f"Repository: {self.name}\n"
            f"  Stars: {self.stars:,}\n"
            f"  Language: {self.language_display}\n"
            f"  Description: {self.description_display}\n"
            f"  URL: {self.url}"
        )