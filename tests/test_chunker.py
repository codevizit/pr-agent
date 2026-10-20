import re

from agent.chunker import chunk_files

HDR = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def f(path, patch, status="added"):
    return {"path": path, "status": status, "additions": 0, "deletions": 0, "patch": patch}


def added_patch(n):
    body = "\n".join(f"+line {i} " + "x" * 30 for i in range(1, n + 1))
    return f"@@ -0,0 +1,{n} @@\n{body}"


def hunks_in(text):
    """Yield [header_match, old_line_count, new_line_count] for each hunk in a chunk."""
    cur = None
    for line in text.split("\n") + ["### END"]:
        if (line.startswith("@@ ") or line.startswith("### ")) and cur:
            yield cur
            cur = None
        m = HDR.match(line)
        if m:
            cur = [m, 0, 0]
        elif cur and line != "":
            k = line[:1]
            if k in (" ", "-"):
                cur[1] += 1
            if k in (" ", "+"):
                cur[2] += 1


def declared(m):
    return (1 if m[2] is None else int(m[2])), (1 if m[4] is None else int(m[4]))


def assert_headers_valid(chunks):
    for c in chunks:
        for m, o, n in hunks_in(c["text"]):
            assert declared(m) == (o, n), (m.group(0), o, n)


def test_empty():
    assert chunk_files([], 1000) == []


def test_small_files_share_one_chunk():
    chunks = chunk_files([f("a.py", added_patch(2)), f("b.py", added_patch(2))], 1000)
    assert len(chunks) == 1
    assert chunks[0]["files"] == ["a.py", "b.py"]


def test_full_chunk_starts_a_new_one():
    chunks = chunk_files([f("a.py", added_patch(10)), f("b.py", added_patch(10))], 600)
    assert [c["files"] for c in chunks] == [["a.py"], ["b.py"]]


def test_multi_hunk_file_splits_on_hunk_boundaries():
    def hunk(start):
        body = "\n".join(f" ctx {i} " + "y" * 30 for i in range(5))
        return f"@@ -{start},5 +{start},5 @@\n{body}"

    patch = "\n".join([hunk(1), hunk(50), hunk(100)])
    chunks = chunk_files([f("m.py", patch, "modified")], 350)
    assert len(chunks) == 3
    for c, start in zip(chunks, ("1", "50", "100")):
        assert len(c["text"]) <= 350
        found = [m.group(0) for m, _, _ in hunks_in(c["text"])]
        assert found == [f"@@ -{start},5 +{start},5 @@"]
    assert "[part 1/3]" in chunks[0]["text"]
    assert "[part 3/3]" in chunks[2]["text"]
    assert_headers_valid(chunks)


def test_oversized_new_file_split_keeps_valid_line_numbers():
    n = 120
    patch = added_patch(n)
    chunks = chunk_files([f("big.py", patch)], 1000)
    assert len(chunks) > 1
    assert all(len(c["text"]) <= 1000 for c in chunks)
    assert_headers_valid(chunks)
    expected_start, added = 1, []
    for c in chunks:
        for m, _, new_count in hunks_in(c["text"]):
            assert int(m[3]) == expected_start
            expected_start += new_count
        added += [ln for ln in c["text"].split("\n") if ln.startswith("+")]
    assert expected_start == n + 1
    assert added == patch.split("\n")[1:]


def test_giant_single_line_is_truncated_not_oversized():
    patch = "@@ -0,0 +1,2 @@\n+short\n+" + "z" * 5000
    chunks = chunk_files([f("min.js", patch)], 1000)
    assert all(len(c["text"]) <= 1000 for c in chunks)
    assert any("[truncated]" in c["text"] for c in chunks)
    assert_headers_valid(chunks)