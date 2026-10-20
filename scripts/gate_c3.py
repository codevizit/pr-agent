import math
import sys
from collections import Counter

from dotenv import load_dotenv

load_dotenv()

from agent.nodes.fetch_diff import fetch_diff
from agent.nodes.filter_chunk import filter_chunk
from agent.nodes.review_chunks import review_chunks

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
NEED = math.ceil(0.8 * N)


def prepare(pr):
    state = {"pr_number": pr}
    state.update(fetch_diff(state))
    state.update(filter_chunk(state))
    return state


def hit(out, lines):
    return any(f["line"] in lines and f["severity"] in ("medium", "high")
               for f in out["findings"])


s1, s3 = prepare(1), prepare(3)
tokens = calls = 0
sql = strict = lenient = skipped1 = 0
extras1, extras3 = Counter(), Counter()

for _ in range(N):
    out = review_chunks(s1)
    tokens += out["usage"]["tokens"]
    calls += out["usage"]["calls"]
    ok = not out["notes"]
    sql += ok and hit(out, {8})
    strict += ok and hit(out, {4})
    lenient += ok and hit(out, {3, 4})
    skipped1 += not ok
    for f in out["findings"]:
        if f["line"] not in {3, 4, 8}:
            extras1[(f["line"], f["severity"], f["title"])] += 1

clean3 = skipped3 = any3 = 0
for _ in range(N):
    out = review_chunks(s3)
    tokens += out["usage"]["tokens"]
    calls += out["usage"]["calls"]
    bad = [f for f in out["findings"] if f["severity"] in ("medium", "high")]
    clean3 += (not bad) and (not out["notes"])
    any3 += bool(out["findings"])
    skipped3 += bool(out["notes"])
    for f in bad:
        extras3[(f["line"], f["severity"], f["title"])] += 1

print(f"Runs per PR: {N}   needed to pass: {NEED}")
print(f"PR #1 SQL injection on line 8:          {sql}/{N}")
print(f"PR #1 password on line 4 (strict):      {strict}/{N}")
print(f"PR #1 password on line 3 or 4 (lenient): {lenient}/{N}")
print(f"PR #1 runs with a skipped chunk:        {skipped1}")
print(f"PR #3 runs with no medium/high:         {clean3}/{N}   (any finding at all: {any3})")
print(f"PR #3 runs with a skipped chunk:        {skipped3}")
print(f"LLM calls: {calls}   tokens: {tokens}   avg tokens per call: {tokens // max(calls, 1)}")
if extras1:
    print("Other findings on PR #1 (review by hand):")
    for (line, sev, title), c in extras1.items():
        print(f"  line {line} [{sev}] {title}  x{c}")
if extras3:
    print("Medium/high findings on PR #3 (false positives?):")
    for (line, sev, title), c in extras3.items():
        print(f"  line {line} [{sev}] {title}  x{c}")
strict_pass = sql >= NEED and strict >= NEED and clean3 >= NEED
lenient_pass = sql >= NEED and lenient >= NEED and clean3 >= NEED
print(f"VERDICT strict: {'PASS' if strict_pass else 'FAIL'}   lenient: {'PASS' if lenient_pass else 'FAIL'}")