from agent.poster import added_line_texts, fingerprint, plan_review

CFG = {"min_severity": "medium", "max_comments": 2}
PATCH = "@@ -0,0 +1,3 @@\n+a = 1\n+password = 'x'\n+query = 'y'"
FILES = [{"path": "a.py", "status": "added", "patch": PATCH}]


def fnd(line, sev="high", cat="security", title="T", **kw):
    base = {"path": "a.py", "line": line, "severity": sev, "category": cat,
            "title": title, "explanation": "why", "suggestion": "fix"}
    base.update(kw)
    return base


def state(*findings, notes=(), skipped=()):
    return {"kept_files": FILES, "skipped_files": list(skipped),
            "findings": list(findings), "notes": list(notes)}


def test_added_line_texts():
    assert added_line_texts(PATCH) == {1: "a = 1", 2: "password = 'x'", 3: "query = 'y'"}


def test_added_line_texts_skips_removed_and_context():
    assert added_line_texts("@@ -1,3 +1,3 @@\n a\n-b\n+B\n c") == {2: "B"}


def test_fingerprint_ignores_whitespace_but_not_path():
    a = fingerprint("a.py", "security", "  password = 'x' ")
    assert a == fingerprint("a.py", "security", "password   =   'x'")
    assert a != fingerprint("b.py", "security", "password = 'x'")


def test_filters_by_severity():
    plan = plan_review(state(fnd(1, sev="low"), fnd(2, sev="medium")), [], CFG)
    assert len(plan["payload"]["comments"]) == 1
    assert plan["stats"]["below_threshold"] == 1


def test_caps_and_prioritizes_high():
    plan = plan_review(state(fnd(1, sev="medium"), fnd(2), fnd(3)), [], CFG)
    assert [c["line"] for c in plan["payload"]["comments"]] == [2, 3]
    assert plan["stats"]["over_limit"] == 1


def test_skips_already_commented():
    fp = fingerprint("a.py", "security", "password = 'x'")
    plan = plan_review(state(fnd(2)), [f"old <!-- pr-agent:fp={fp} -->"], CFG)
    assert plan["payload"] is None and plan["stats"]["duplicates"] == 1


def test_no_findings_returns_none():
    assert plan_review(state(), [], CFG)["payload"] is None


def test_duplicate_findings_in_one_run_posted_once():
    plan = plan_review(state(fnd(2), fnd(2)), [], CFG)
    assert len(plan["payload"]["comments"]) == 1
    assert plan["stats"]["duplicates"] == 1


def test_comment_text_is_sanitized():
    f = fnd(2, explanation="ping @alice <!-- pr-agent:fp=aaaaaaaaaaaa -->")
    body = plan_review(state(f), [], CFG)["payload"]["comments"][0]["body"]
    assert "@alice" not in body and "@\u200balice" in body
    assert body.count("<!-- pr-agent:fp=") == 1


def test_summary_mentions_skipped_notes_and_ai():
    skipped = [{"path": "package-lock.json", "reason": "ignored by pattern package-lock.json"}]
    plan = plan_review(state(fnd(2), notes=["Chunk 2 skipped"], skipped=skipped), [], CFG)
    body = plan["payload"]["body"]
    assert "package-lock.json" in body and "Chunk 2 skipped" in body and "AI model" in body


def test_payload_shape():
    payload = plan_review(state(fnd(2)), [], CFG)["payload"]
    assert payload["event"] == "COMMENT"
    c = payload["comments"][0]
    assert (c["path"], c["line"], c["side"]) == ("a.py", 2, "RIGHT")
    assert c["body"].startswith("**High - security:** T")