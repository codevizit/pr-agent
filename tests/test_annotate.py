from agent.annotate import annotate_chunk
from agent.chunker import chunk_files

PR1_PATCH = """@@ -0,0 +1,9 @@
+import sqlite3
+
+DB_USER = "admin"
+DB_PASSWORD = "admin123"
+
+
+def get_user(conn: sqlite3.Connection, username: str):
+    query = f"SELECT * FROM users WHERE name = '{username}'"
+    return conn.execute(query).fetchall()
\\ No newline at end of file"""


def file(path, patch, status="added"):
    return {"path": path, "status": status, "additions": 0, "deletions": 0, "patch": patch}


def test_added_file_numbering():
    chunk = chunk_files([file("db_client.py", PR1_PATCH)], 12000)[0]
    text, valid = annotate_chunk(chunk["text"])
    assert valid == {"db_client.py": set(range(1, 10))}
    assert '    4 +DB_PASSWORD = "admin123"' in text
    assert '    8 +    query = f"SELECT' in text


def test_modified_file_context_and_removed_lines():
    patch = "@@ -1,4 +1,4 @@\n a\n-b\n+B\n c\n d"
    chunk = chunk_files([file("m.py", patch, "modified")], 12000)[0]
    text, valid = annotate_chunk(chunk["text"])
    assert valid == {"m.py": {2}}
    lines = text.split("\n")
    assert "    1  a" in lines
    assert "    2 +B" in lines
    assert " " * 6 + "-b" in lines
    assert "    4  d" in lines


def test_two_hunks_use_their_own_start_lines():
    patch = "@@ -1 +1,2 @@\n a\n+b\n@@ -50,2 +52,3 @@\n x\n+y\n z"
    chunk = chunk_files([file("m.py", patch, "modified")], 12000)[0]
    _, valid = annotate_chunk(chunk["text"])
    assert valid == {"m.py": {2, 53}}


def test_split_parts_cover_every_line_once():
    chunks = chunk_files([file("db_client.py", PR1_PATCH)], 200)
    assert len(chunks) == 3
    sets = [annotate_chunk(c["text"])[1]["db_client.py"] for c in chunks]
    assert sets == [set(range(1, 7)), {7, 8}, {9}]