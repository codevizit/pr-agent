import agent.nodes.review_chunks as rc

CHUNK = {
    "index": 1,
    "files": ["a.py"],
    "chars": 100,
    "text": "### FILE: a.py (added)\n@@ -0,0 +1,2 @@\n+x = 1\n+password = 'admin'",
}
GOOD = {"path": "a.py", "line": 2, "severity": "high", "category": "security",
        "title": "Hardcoded password", "explanation": "e", "suggestion": None}
BAD = {"findings": [{"path": "a.py"}]}


def fake_factory(replies, seen):
    it = iter(replies)

    def fake(system, user):
        seen.append(user)
        return {"data": next(it), "latency_s": 0.1, "tokens": 100}

    return fake


def test_valid_finding_kept_and_bad_line_dropped(monkeypatch):
    seen = []
    monkeypatch.setattr(rc, "ask_json",
                        fake_factory([{"findings": [GOOD, {**GOOD, "line": 9}]}], seen))
    out = rc.review_chunks({"chunks": [CHUNK]})
    assert [f["line"] for f in out["findings"]] == [2]
    assert out["dropped_findings"][0]["line"] == 9
    assert "line" in out["dropped_findings"][0]["reason"]
    assert out["usage"]["calls"] == 1 and out["notes"] == []


def test_retry_once_then_succeed(monkeypatch):
    seen = []
    monkeypatch.setattr(rc, "ask_json", fake_factory([BAD, {"findings": [GOOD]}], seen))
    out = rc.review_chunks({"chunks": [CHUNK]})
    assert len(out["findings"]) == 1 and out["usage"]["calls"] == 2
    assert "previous reply was invalid" in seen[1]
    assert "previous reply" not in seen[0]


def test_skip_chunk_after_two_invalid_replies(monkeypatch):
    seen = []
    monkeypatch.setattr(rc, "ask_json", fake_factory([BAD, BAD], seen))
    out = rc.review_chunks({"chunks": [CHUNK]})
    assert out["findings"] == [] and out["usage"]["calls"] == 2
    assert len(out["notes"]) == 1 and "skipped" in out["notes"][0]


def test_empty_findings_ok(monkeypatch):
    seen = []
    monkeypatch.setattr(rc, "ask_json", fake_factory([{"findings": []}], seen))
    out = rc.review_chunks({"chunks": [CHUNK]})
    assert out["findings"] == [] and out["notes"] == []