import re

FILE_RE = re.compile(r"^### FILE: (.*) \((\w+)\)(?: \[part \d+/\d+\])?$")
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def annotate_chunk(text: str) -> tuple[str, dict[str, set[int]]]:
    """Prefix each new-side diff line with its real line number.

    Returns the annotated text and, per file, the set of added line numbers
    (the only lines a finding may point at).
    """
    out: list[str] = []
    valid: dict[str, set[int]] = {}
    path = None
    old_left = new_left = n_line = 0
    for line in text.split("\n"):
        m = FILE_RE.match(line)
        if m:
            path = m[1]
            valid.setdefault(path, set())
            old_left = new_left = 0
            out.append(line)
            continue
        h = HUNK_RE.match(line)
        if h:
            old_left = 1 if h[2] is None else int(h[2])
            new_left = 1 if h[4] is None else int(h[4])
            n_line = int(h[3])
            out.append(line)
            continue
        if line.startswith("\\"):
            out.append(f"{'':>5} {line}")
            continue
        if old_left <= 0 and new_left <= 0:
            out.append(line)  # separator or text outside a hunk
            continue
        kind = line[:1]
        if kind == "+":
            new_left -= 1
            valid[path].add(n_line)
            out.append(f"{n_line:>5} {line}")
            n_line += 1
        elif kind == "-":
            old_left -= 1
            out.append(f"{'':>5} {line}")
        else:  # context line (a space) or an empty context line
            old_left -= 1
            new_left -= 1
            out.append(f"{n_line:>5} {line}")
            n_line += 1
    return "\n".join(out), valid