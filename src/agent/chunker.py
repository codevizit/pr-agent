import re

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")


def split_hunks(patch: str) -> list[str]:
    hunks, cur = [], []
    for line in patch.split("\n"):
        if line.startswith("@@ ") and cur:
            hunks.append("\n".join(cur))
            cur = []
        cur.append(line)
    if cur:
        hunks.append("\n".join(cur))
    return hunks


def split_long_hunk(hunk: str, budget: int) -> list[str]:
    """Split one oversized hunk between lines, rewriting each piece's @@ header."""
    lines = hunk.split("\n")
    m = HUNK_RE.match(lines[0])
    if not m:
        raise ValueError(f"unparseable hunk header: {lines[0][:60]}")
    old_len0 = 1 if m[2] is None else int(m[2])
    new_len0 = 1 if m[4] is None else int(m[4])
    o_next = int(m[1]) + (1 if old_len0 == 0 else 0)
    n_next = int(m[3]) + (1 if new_len0 == 0 else 0)
    tail = m[5]
    limit = budget - len(lines[0]) - 20  # room for the rewritten header
    if limit < 100:
        raise ValueError("max_chunk_chars is too small for this file")

    pieces, body, size = [], [], 0
    o_start, n_start, o_len, n_len = o_next, n_next, 0, 0

    def flush():
        oh = o_start if o_len else o_start - 1
        nh = n_start if n_len else n_start - 1
        pieces.append("\n".join([f"@@ -{oh},{o_len} +{nh},{n_len} @@{tail}"] + body))

    for line in lines[1:]:
        if len(line) > limit:
            line = line[: limit - 20] + "...[truncated]"
        if body and size + len(line) + 1 > limit:
            flush()
            body, size = [], 0
            o_start, n_start, o_len, n_len = o_next, n_next, 0, 0
        body.append(line)
        size += len(line) + 1
        k = line[:1]
        if k == "-":
            o_len += 1
            o_next += 1
        elif k == "+":
            n_len += 1
            n_next += 1
        elif k == "\\":
            pass
        else:
            o_len += 1
            n_len += 1
            o_next += 1
            n_next += 1
    if body:
        flush()
    return pieces


def _header(f: dict, part: tuple[int, int] | None = None) -> str:
    h = f"### FILE: {f['path']} ({f['status']})"
    return h + (f" [part {part[0]}/{part[1]}]" if part else "")


def _file_pieces(f: dict, max_chars: int) -> list[str]:
    patch = f["patch"].rstrip("\n")
    whole = _header(f) + "\n" + patch
    if len(whole) <= max_chars:
        return [whole]
    budget = max_chars - len(_header(f, (999, 999))) - 1
    hunks = []
    for h in split_hunks(patch):
        hunks += [h] if len(h) <= budget else split_long_hunk(h, budget)
    bodies, cur = [], ""
    for h in hunks:
        if cur and len(cur) + 1 + len(h) > budget:
            bodies.append(cur)
            cur = h
        else:
            cur = f"{cur}\n{h}" if cur else h
    if cur:
        bodies.append(cur)
    n = len(bodies)
    return [_header(f, (i, n)) + "\n" + b for i, b in enumerate(bodies, 1)]


def chunk_files(files: list[dict], max_chars: int) -> list[dict]:
    texts: list[tuple[str, list[str]]] = []
    cur, cur_files = "", []
    for f in files:
        for piece in _file_pieces(f, max_chars):
            if cur and len(cur) + 2 + len(piece) > max_chars:
                texts.append((cur, cur_files))
                cur, cur_files = "", []
            cur = f"{cur}\n\n{piece}" if cur else piece
            if f["path"] not in cur_files:
                cur_files.append(f["path"])
    if cur:
        texts.append((cur, cur_files))
    return [
        {"index": i, "text": t, "files": fl, "chars": len(t)}
        for i, (t, fl) in enumerate(texts, 1)
    ]