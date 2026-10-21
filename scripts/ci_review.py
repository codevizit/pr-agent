import os
import sys

from dotenv import load_dotenv

load_dotenv()

from agent.graphs.review_graph import build_review_graph


def main() -> int:
    raw = os.environ.get("PR_NUMBER", "")
    if not raw.isdigit():
        print("PR_NUMBER is missing or not a number; nothing to review.")
        return 1
    pr = int(raw)
    out = build_review_graph().invoke({"pr_number": pr})
    print(f"PR #{pr}: stats={out['post_stats']} findings={len(out['findings'])} "
          f"dropped={len(out['dropped_findings'])} usage={out['usage']}")
    for note in out["notes"]:
        print(f"NOTE: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())