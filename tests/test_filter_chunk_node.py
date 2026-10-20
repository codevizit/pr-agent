from agent.nodes.filter_chunk import filter_chunk


def test_filter_chunk_node():
    files = [
        {"path": "package-lock.json", "status": "modified", "additions": 1, "deletions": 1,
         "patch": "@@ -1 +1 @@\n-a\n+b"},
        {"path": "a.py", "status": "added", "additions": 1, "deletions": 0,
         "patch": "@@ -0,0 +1 @@\n+x"},
    ]
    out = filter_chunk({"diff_files": files})
    assert [k["path"] for k in out["kept_files"]] == ["a.py"]
    assert [s["path"] for s in out["skipped_files"]] == ["package-lock.json"]
    assert len(out["chunks"]) == 1