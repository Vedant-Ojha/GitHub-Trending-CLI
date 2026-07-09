from datetime import datetime, timedelta
from typing import List

import requests

from ..domain.models import Repository, Issue
from ..infrastructure.parser import parse_repositories, parse_issues
from ..utils.config import config
from ..utils.errors import APIError, RateLimitError, NetworkError, ParseError
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Maps user-facing duration strings to timedelta objects
DURATION_MAP = {
    "day": timedelta(days=1),
    "week": timedelta(weeks=1),
    "month": timedelta(days=30),
    "year": timedelta(days=365),
}


def _build_date_filter(duration: str) -> str:
    """
    Build GitHub search date filter string.

    Args:
        duration: One of 'day', 'week', 'month', 'year'

    Returns:
        Date string like '>2024-01-01'
    """
    delta = DURATION_MAP[duration]
    since_date = datetime.utcnow() - delta
    return since_date.strftime(">%Y-%m-%d")


def _make_request(url: str, params: dict = None) -> any:
    """
    Internal helper — makes a GET request with full error handling.

    Args:
        url: Full request URL
        params: Query parameters dict

    Returns:
        Parsed JSON response (dict or list)

    Raises:
        RateLimitError: On 403 with rate limit headers
        APIError: On any non-200 HTTP status
        NetworkError: On connection/timeout failures
        ParseError: If response is not valid JSON
    """
    logger.debug(f"GET {url} | params={params}")

    try:
        response = requests.get(
            url,
            headers=config.HEADERS,
            params=params,
            timeout=config.REQUEST_TIMEOUT,
        )

    except requests.exceptions.Timeout:
        raise NetworkError(
            f"Request timed out after {config.REQUEST_TIMEOUT}s. " "Check your internet connection."
        )

    except requests.exceptions.ConnectionError as e:
        raise NetworkError(f"Connection failed: {e}")

    # Handle rate limiting (403 or 429)
    if response.status_code in (403, 429):
        reset_time = response.headers.get("X-RateLimit-Reset")
        if reset_time:
            reset_dt = datetime.utcfromtimestamp(int(reset_time))
            reset_str = reset_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            reset_str = None
        raise RateLimitError(reset_time=reset_str)

    # Handle all other HTTP errors
    if not response.ok:
        raise APIError(
            f"GitHub API returned {response.status_code}: " f"{response.text[:200]}",
            status_code=response.status_code,
        )

    try:
        return response.json()

    except ValueError as e:
        raise ParseError(f"Failed to parse API response as JSON: {e}")


class RepoClient:
    """
    Fetches trending repositories from GitHub Search API.
    Endpoint: GET /search/repositories
    """

    def fetch(self, duration: str, limit: int) -> List[Repository]:
        """
        Fetch trending repositories created within the given duration.

        Args:
            duration: One of 'day', 'week', 'month', 'year'
            limit: Number of repositories to return (max 100)

        Returns:
            List of Repository objects sorted by stars (desc)
        """
        date_filter = _build_date_filter(duration)
        query = f"created:{date_filter}"

        # GitHub API allows max 100 per page
        per_page = min(limit, config.MAX_PER_PAGE)

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": 1,
        }

        url = f"{config.GITHUB_API_BASE}/search/repositories"

        logger.debug(f"Fetching repos: duration={duration}, limit={limit}")

        raw_data = _make_request(url, params=params)
        repos = parse_repositories(raw_data)

        logger.debug(f"Fetched {len(repos)} repos from API")
        return repos


class IssuesClient:
    """
    Fetches 'good first issue' issues for a given repository.
    Endpoint: GET /repos/{owner}/{repo}/issues
    """

    def fetch(self, repo_full_name: str, max_issues: int = 3) -> List[Issue]:
        """
        Fetch good first issues for a repository.

        Args:
            repo_full_name: Repository full name (e.g., "owner/repo")
            max_issues: Maximum number of issues to return

        Returns:
            List of Issue objects — empty list if none found or error
        """
        url = f"{config.GITHUB_API_BASE}/repos/" f"{repo_full_name}/issues"

        params = {
            "labels": "good first issue",
            "state": "open",
            "per_page": max_issues,
            "sort": "created",
            "direction": "desc",
        }

        logger.debug(f"Fetching good first issues for: {repo_full_name}")

        try:
            raw_data = _make_request(url, params=params)
            issues = parse_issues(raw_data)
            return issues[:max_issues]

        except (APIError, NetworkError, ParseError) as e:
            # Graceful fallback — issues fetch failure
            # should NOT crash the whole app
            logger.warning(f"Could not fetch issues for {repo_full_name}: {e}")
            return []
