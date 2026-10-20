from agent.config import load_config
from agent.filters import filter_files

CFG = load_config()


def f(path, patch="@@ -0,0 +1 @@\n+x"):
    return {"path": path, "status": "added", "additions": 1, "deletions": 0, "patch": patch}


def run(*files):
    kept, skipped = filter_files(list(files), CFG)
    return [k["path"] for k in kept], skipped


def test_our_three_prs():
    kept, skipped = run(f("db_client.py"), f("package-lock.json"), f("utils.py"))
    assert kept == ["db_client.py", "utils.py"]
    assert [s["path"] for s in skipped] == ["package-lock.json"]
    assert "package-lock.json" in skipped[0]["reason"]


def test_nested_lockfile_skipped():
    kept, skipped = run(f("web/package-lock.json"))
    assert kept == [] and len(skipped) == 1


def test_nested_build_dir_skipped():
    kept, _ = run(f("web/dist/app.js"))
    assert kept == []


def test_similar_names_not_skipped():
    kept, _ = run(f("rebuild/x.py"), f("src/build_utils.py"), f("src/distance.py"))
    assert kept == ["rebuild/x.py", "src/build_utils.py", "src/distance.py"]


def test_case_insensitive():
    kept, _ = run(f("IMG/Logo.PNG"))
    assert kept == []


def test_no_patch_skipped():
    kept, skipped = run(f("data.bin", patch=None))
    assert kept == [] and "no patch" in skipped[0]["reason"]


def test_empty_patch_skipped():
    kept, _ = run(f("empty.py", patch=""))
    assert kept == []


def test_normal_source_kept():
    kept, _ = run(f("src/app.py"))
    assert kept == ["src/app.py"]