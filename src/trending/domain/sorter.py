from typing import List
from .models import Repository


def sort_by_stars(repos: List[Repository], descending: bool = True) -> List[Repository]:
    """
    Sort repositories by star count.

    Args:
        repos: List of Repository objects
        descending: If True (default), highest stars first

    Returns:
        New sorted list (original list is not mutated)
    """
    return sorted(repos, key=lambda r: r.stars, reverse=descending)


def apply_limit(repos: List[Repository], limit: int) -> List[Repository]:
    """
    Trim repository list to the requested limit.

    Args:
        repos: List of Repository objects
        limit: Maximum number to return

    Returns:
        Sliced list with at most `limit` items
    """
    return repos[:limit]


def filter_and_rank(repos: List[Repository], limit: int) -> List[Repository]:
    """
    Convenience function: sort by stars then apply limit.
    Called by the service layer after fetching repos.

    Args:
        repos: List of Repository objects
        limit: Maximum number to return

    Returns:
        Sorted and limited list of Repository objects
    """
    sorted_repos = sort_by_stars(repos)
    return apply_limit(sorted_repos, limit)
