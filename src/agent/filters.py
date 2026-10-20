from fnmatch import fnmatchcase
from pathlib import PurePosixPath


def _match(path: str, patterns: list[str]) -> str | None:
    """Return the first pattern matching the path or any trailing part of it."""
    parts = PurePosixPath(path.lower()).parts
    for pattern in patterns:
        p = pattern.lower()
        for i in range(len(parts)):
            if fnmatchcase("/".join(parts[i:]), p):
                return pattern
    return None


def filter_files(files: list[dict], cfg: dict) -> tuple[list[dict], list[dict]]:
    kept, skipped = [], []
    for f in files:
        pattern = _match(f["path"], cfg["ignore_globs"])
        if pattern:
            skipped.append({"path": f["path"], "reason": f"ignored by pattern {pattern}"})
        elif not f.get("patch"):
            skipped.append(
                {"path": f["path"], "reason": "no patch (binary or too large for GitHub to show)"}
            )
        else:
            kept.append(f)
    return kept, skipped