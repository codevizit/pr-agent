import os

import httpx

API = "https://api.github.com"


class GitHubClient:
    def __init__(self, repo: str | None = None, token: str | None = None):
        self.repo = repo or os.environ.get("GITHUB_REPO", "")
        token = token or os.environ.get("GITHUB_TOKEN", "")
        if not token or "/" not in self.repo:
            raise RuntimeError("Set GITHUB_TOKEN and GITHUB_REPO (owner/repo) in .env")
        self.http = httpx.Client(
            base_url=API,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30,
        )

    def _get_all(self, url: str) -> list[dict]:
        items, page = [], 1
        while True:
            r = self.http.get(url, params={"per_page": 100, "page": page})
            r.raise_for_status()
            batch = r.json()
            items += batch
            if len(batch) < 100:
                return items
            page += 1

    def list_pr_files(self, pr_number: int) -> list[dict]:
        return self._get_all(f"/repos/{self.repo}/pulls/{pr_number}/files")

    def list_review_comments(self, pr_number: int) -> list[dict]:
        return self._get_all(f"/repos/{self.repo}/pulls/{pr_number}/comments")

    def get_pr(self, pr_number: int) -> dict:
        r = self.http.get(f"/repos/{self.repo}/pulls/{pr_number}")
        r.raise_for_status()
        return r.json()

    def create_review(self, pr_number: int, payload: dict) -> dict:
        r = self.http.post(f"/repos/{self.repo}/pulls/{pr_number}/reviews", json=payload)
        if r.status_code >= 400:
            raise RuntimeError(f"GitHub rejected the review ({r.status_code}): {r.text[:500]}")
        return r.json()