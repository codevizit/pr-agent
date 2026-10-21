import pytest

from agent.clients.github import GitHubClient


def clear(monkeypatch):
    for k in ("GITHUB_REPO", "GITHUB_REPOSITORY", "GITHUB_TOKEN"):
        monkeypatch.delenv(k, raising=False)


def test_uses_github_repository_when_github_repo_missing(monkeypatch):
    clear(monkeypatch)
    monkeypatch.setenv("GITHUB_REPOSITORY", "octo/hello")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    assert GitHubClient().repo == "octo/hello"


def test_github_repo_wins_when_both_set(monkeypatch):
    clear(monkeypatch)
    monkeypatch.setenv("GITHUB_REPO", "me/mine")
    monkeypatch.setenv("GITHUB_REPOSITORY", "octo/hello")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    assert GitHubClient().repo == "me/mine"


def test_missing_token_raises(monkeypatch):
    clear(monkeypatch)
    monkeypatch.setenv("GITHUB_REPOSITORY", "octo/hello")
    with pytest.raises(RuntimeError):
        GitHubClient()