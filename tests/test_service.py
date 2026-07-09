import pytest
from unittest.mock import MagicMock
from src.trending.application.service import TrendingService
from src.trending.domain.models import Repository, Issue
from src.trending.utils.errors import ValidationError


def make_repo(name="owner/repo", stars=500):
    return Repository(
        name=name,
        description="Test repo",
        stars=stars,
        language="Python",
        url=f"https://github.com/{name}",
    )


@pytest.fixture
def service():
    return TrendingService()


def test_invalid_duration_raises_error(service):
    with pytest.raises(ValidationError):
        service.get_trending(duration="invalid", limit=10)


def test_invalid_limit_raises_error(service):
    with pytest.raises(ValidationError):
        service.get_trending(duration="week", limit=0)


def test_get_trending_returns_repos(service):
    repos = [make_repo("o/r1", 1000), make_repo("o/r2", 500)]
    service.repo_client.fetch = MagicMock(return_value=repos)

    result = service.get_trending(duration="week", limit=5, include_issues=False)

    assert len(result) == 2


def test_get_trending_sorted_by_stars(service):
    repos = [make_repo("o/r1", 100), make_repo("o/r2", 9999), make_repo("o/r3", 500)]
    service.repo_client.fetch = MagicMock(return_value=repos)

    result = service.get_trending(duration="month", limit=10, include_issues=False)

    assert result[0].stars == 9999
    assert result[1].stars == 500
    assert result[2].stars == 100


def test_get_trending_with_issues(service):
    repos = [make_repo("o/r1", 1000)]
    issues = [Issue(number=1, title="Easy fix", url="http://example.com", labels=[])]

    service.repo_client.fetch = MagicMock(return_value=repos)
    service.issues_client.fetch = MagicMock(return_value=issues)

    result = service.get_trending(duration="week", limit=5, include_issues=True)

    assert result[0].issues == issues


def test_get_trending_calls_issues_client(service):
    repos = [make_repo("o/r1", 1000)]

    service.repo_client.fetch = MagicMock(return_value=repos)
    service.issues_client.fetch = MagicMock(return_value=[])

    service.get_trending(duration="week", limit=5, include_issues=True)

    service.issues_client.fetch.assert_called_once_with(repo_full_name="o/r1", max_issues=3)


def test_get_trending_no_issues_client_when_flag_false(service):
    repos = [make_repo("o/r1", 1000)]

    service.repo_client.fetch = MagicMock(return_value=repos)
    service.issues_client.fetch = MagicMock(return_value=[])

    service.get_trending(duration="week", limit=5, include_issues=False)

    service.issues_client.fetch.assert_not_called()
