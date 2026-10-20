import pytest
from pydantic import ValidationError

from agent.schemas import Finding
from agent.validation import validate_findings

VALID = {"a.py": {3, 4}}


def fnd(path="a.py", line=4, **kw):
    base = dict(path=path, line=line, severity="high", category="security",
                title="t", explanation="e")
    base.update(kw)
    return Finding(**base)


def test_valid_finding_kept():
    kept, dropped = validate_findings([fnd()], VALID)
    assert len(kept) == 1 and dropped == []


def test_wrong_line_dropped():
    kept, dropped = validate_findings([fnd(line=99)], VALID)
    assert kept == [] and "line" in dropped[0][1]


def test_wrong_file_dropped():
    kept, dropped = validate_findings([fnd(path="b.py")], VALID)
    assert kept == [] and "file" in dropped[0][1]


def test_bad_severity_rejected():
    with pytest.raises(ValidationError):
        fnd(severity="critical")


def test_suggestion_optional():
    assert fnd().suggestion is None