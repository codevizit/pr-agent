import os

from agent.clients.github import GitHubClient
from agent.config import load_config
from agent.poster import plan_review


def post_comments(state: dict) -> dict:
    """Plan the review. Post it only when PR_AGENT_POST is exactly "1"."""
    cfg = load_config()
    gh = GitHubClient()
    pr = state["pr_number"]
    existing = [c.get("body") or "" for c in gh.list_review_comments(pr)]
    plan = plan_review(state, existing, cfg)
    payload, submitted = plan["payload"], False
    if payload:
        payload["commit_id"] = gh.get_pr(pr)["head"]["sha"]
        if os.getenv("PR_AGENT_POST") == "1":
            gh.create_review(pr, payload)
            submitted = True
    return {"review_payload": payload, "post_stats": {**plan["stats"], "submitted": submitted}}