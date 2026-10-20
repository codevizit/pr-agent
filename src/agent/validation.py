from agent.schemas import Finding


def validate_findings(
    findings: list[Finding], valid_lines: dict[str, set[int]]
) -> tuple[list[Finding], list[tuple[Finding, str]]]:
    kept, dropped = [], []
    for f in findings:
        lines = valid_lines.get(f.path)
        if lines is None:
            dropped.append((f, "file not in this chunk"))
        elif f.line not in lines:
            dropped.append((f, "line not an added line in the diff"))
        else:
            kept.append(f)
    return kept, dropped