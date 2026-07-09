import pytest
from src.trending.domain.models import Repository, Issue


def make_repo(**kwargs):
    defaults = dict(
        name="owner/my-repo",
        description="A cool repo",
        stars=1000,
        language="Python",
        url="https://github.com/owner/my-repo",
    )
    defaults.update(kwargs)
    return Repository(**defaults)


def test_repository_display_name():
    repo = make_repo(name="octocat/hello-world")
    assert repo.display_name == "hello-world"


def test_repository_owner():
    repo = make_repo(name="octocat/hello-world")
    assert repo.owner == "octocat"


def test_repository_no_language():
    repo = make_repo(language=None)
    assert repo.language_display == "Unknown"


def test_repository_no_description():
    repo = make_repo(description="")
    assert repo.description_display == "No description provided"


def test_repository_has_no_issues_by_default():
    repo = make_repo()
    assert not repo.has_issues()


def test_repository_has_issues():
    issue = Issue(
        number=1,
        title="Fix bug",
        url="http://example.com",
        labels=["good first issue"]
    )
    repo = make_repo()
    repo.issues = [issue]
    assert repo.has_issues()


def test_issue_str_contains_number():
    issue = Issue(
        number=42,
        title="Add tests",
        url="http://example.com/issues/42",
        labels=["beginner"]
    )
    result = str(issue)
    assert "#42" in result


def test_issue_str_contains_title():
    issue = Issue(
        number=42,
        title="Add tests",
        url="http://example.com/issues/42",
        labels=["beginner"]
    )
    result = str(issue)
    assert "Add tests" in result


def test_repository_stars_display():
    repo = make_repo(stars=5000)
    assert repo.stars == 5000


def test_repository_url():
    repo = make_repo(url="https://github.com/owner/my-repo")
    assert repo.url == "https://github.com/owner/my-repo"