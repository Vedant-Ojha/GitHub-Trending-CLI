from typing import List

from ..domain.models import Repository
from ..domain.sorter import filter_and_rank
from ..infrastructure.github_client import RepoClient, IssuesClient
from ..application.validator import validate_duration, validate_limit
from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TrendingService:
    """
    Orchestrates all operations in the correct order:
    1. Validate inputs
    2. Fetch repositories from GitHub API
    3. Sort and limit results
    4. Optionally fetch good first issues for each repo
    """

    def __init__(self):
        self.repo_client = RepoClient()
        self.issues_client = IssuesClient()

    def get_trending(
        self,
        duration: str,
        limit: int,
        include_issues: bool = False,
    ) -> List[Repository]:
        """
        Main entry point for the application layer.

        Args:
            duration: Time window — 'day', 'week', 'month', 'year'
            limit: How many repositories to return
            include_issues: If True, fetch good first issues per repo

        Returns:
            List of Repository objects sorted by stars
            with optional issues attached

        Raises:
            ValidationError: On invalid inputs
            APIError: On GitHub API failures
            NetworkError: On connection failures
        """
        # --- Step 1: Validate inputs ---
        duration = validate_duration(duration)
        limit = validate_limit(limit)

        logger.debug(
            f"Service called: duration={duration}, "
            f"limit={limit}, "
            f"include_issues={include_issues}"
        )

        # --- Step 2: Fetch repositories ---
        repos = self.repo_client.fetch(duration=duration, limit=limit)

        # --- Step 3: Sort by stars and apply limit ---
        repos = filter_and_rank(repos, limit)

        # --- Step 4: Fetch issues if requested ---
        if include_issues:
            repos = self._attach_issues(repos)

        return repos

    def _attach_issues(self, repos: List[Repository]) -> List[Repository]:
        """
        For each repository, fetch up to MAX_ISSUES_PER_REPO
        good first issues.

        Failed issue fetches are silently skipped
        so one bad repo does not crash the whole output.

        Args:
            repos: List of Repository objects

        Returns:
            Same list with .issues field populated on each repo
        """
        for repo in repos:
            logger.debug(f"Fetching issues for {repo.name}")

            issues = self.issues_client.fetch(
                repo_full_name=repo.name,
                max_issues=config.MAX_ISSUES_PER_REPO,
            )

            repo.issues = issues

            logger.debug(f"Found {len(issues)} issues for {repo.name}")

        return repos
