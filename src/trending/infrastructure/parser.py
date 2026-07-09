from typing import List, Dict, Any
from ..domain.models import Repository, Issue
from ..utils.errors import ParseError
from ..utils.logger import get_logger

logger = get_logger(__name__)


def parse_repositories(data: Dict[str, Any]) -> List[Repository]:
    """
    Parse GitHub Search API response into Repository objects.

    Args:
        data: Raw JSON dict from GitHub /search/repositories

    Returns:
        List of Repository domain objects

    Raises:
        ParseError: If response format is unexpected
    """
    if not isinstance(data, dict):
        raise ParseError(
            f"Expected dict from API, got {type(data).__name__}"
        )

    items = data.get("items")

    if items is None:
        raise ParseError("API response missing 'items' key")

    if not isinstance(items, list):
        raise ParseError(
            f"Expected 'items' to be a list, got {type(items).__name__}"
        )

    repos = []

    for item in items:
        try:
            repo = Repository(
                name=item["full_name"],
                description=item.get("description") or "",
                stars=item.get("stargazers_count", 0),
                language=item.get("language"),
                url=item.get("html_url", ""),
            )
            repos.append(repo)

        except KeyError as e:
            # Skip malformed items but log a warning
            logger.warning(f"Skipping repo due to missing field: {e}")
            continue

    logger.debug(f"Parsed {len(repos)} repositories from API response")
    return repos


def parse_issues(data: List[Dict[str, Any]]) -> List[Issue]:
    """
    Parse GitHub Issues API response into Issue objects.

    Args:
        data: Raw JSON list from GitHub /repos/{owner}/{repo}/issues

    Returns:
        List of Issue domain objects

    Raises:
        ParseError: If response format is unexpected
    """
    if not isinstance(data, list):
        raise ParseError(
            f"Expected list from Issues API, got {type(data).__name__}"
        )

    issues = []

    for item in data:
        try:
            labels = [
                label.get("name", "")
                for label in item.get("labels", [])
                if isinstance(label, dict)
            ]

            issue = Issue(
                number=item["number"],
                title=item.get("title", "No title"),
                url=item.get("html_url", ""),
                labels=labels,
            )
            issues.append(issue)

        except KeyError as e:
            logger.warning(f"Skipping issue due to missing field: {e}")
            continue

    logger.debug(f"Parsed {len(issues)} issues from API response")
    return issues