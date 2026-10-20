import agent.nodes.post_comments as pc
from agent.poster import fingerprint

PATCH = "@@ -0,0 +1,2 @@\n+a = 1\n+password = 'x'"
STATE = {
    "pr_number": 1,
    "kept_files": [{"path": "a.py", "status": "added", "patch": PATCH}],
    "skipped_files": [],
    "notes": [],
    "findings": [{"path": "a.py", "line": 2, "severity": "high", "category": "security",
                  "title": "T", "explanation": "e", "suggestion": None}],
}


class FakeGH:
    def __init__(self, existing=()):
        self.existing = list(existing)
        self.created = []

    def list_review_comments(self, n):
        return [{"body": b} for b in self.existing]

    def get_pr(self, n):
        return {"head": {"sha": "abc"}}

    def create_review(self, n, payload):
        self.created.append((n, payload))


def run(monkeypatch, fake, flag):
    monkeypatch.setattr(pc, "GitHubClient", lambda: fake)
    if flag is None:
        monkeypatch.delenv("PR_AGENT_POST", raising=False)
    else:
        monkeypatch.setenv("PR_AGENT_POST", flag)
    return pc.post_comments(STATE)


def test_dry_run_by_default(monkeypatch):
    fake = FakeGH()
    out = run(monkeypatch, fake, None)
    assert fake.created == [] and out["post_stats"]["submitted"] is False
    assert out["review_payload"]["commit_id"] == "abc"


def test_live_posts_once(monkeypatch):
    fake = FakeGH()
    out = run(monkeypatch, fake, "1")
    assert len(fake.created) == 1 and out["post_stats"]["submitted"] is True
    assert fake.created[0][0] == 1


def test_only_exact_1_enables_posting(monkeypatch):
    fake = FakeGH()
    run(monkeypatch, fake, "true")
    assert fake.created == []


def test_live_with_nothing_new_posts_nothing(monkeypatch):
    fp = fingerprint("a.py", "security", "password = 'x'")
    fake = FakeGH(existing=[f"old <!-- pr-agent:fp={fp} -->"])
    out = run(monkeypatch, fake, "1")
    assert fake.created == [] and out["review_payload"] is None
    assert out["post_stats"]["duplicates"] == 1