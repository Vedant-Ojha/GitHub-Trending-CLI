from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class Config:
    """
    Central configuration for the application.
    All values are constants — no environment variables needed
    for unauthenticated usage.
    """
    # GitHub API base URL
    GITHUB_API_BASE: str = "https://api.github.com"

    # Request timeout in seconds
    REQUEST_TIMEOUT: int = 15

    # Max repos per API request (GitHub max is 100)
    MAX_PER_PAGE: int = 100

    # Max issues to fetch per repository
    MAX_ISSUES_PER_REPO: int = 3

    # Valid duration choices for --duration flag
    VALID_DURATIONS: Tuple[str, ...] = ("day", "week", "month", "year")

    # Default values matching CLI defaults
    DEFAULT_DURATION: str = "week"
    DEFAULT_LIMIT: int = 10

    # Min/Max allowed values for --limit flag
    MIN_LIMIT: int = 1
    MAX_LIMIT: int = 100

    # HTTP headers sent with every request
    HEADERS: dict = field(default_factory=lambda: {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "github-trending-cli/1.0.0"
    })


# Singleton instance — import this everywhere
config = Config()