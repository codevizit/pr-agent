import json
import sys

from dotenv import load_dotenv

load_dotenv()

from agent.graphs.review_graph import build_review_graph

app = build_review_graph()
for n in map(int, sys.argv[1:]):
    out = app.invoke({"pr_number": n})
    print(f"PR #{n}: stats={out['post_stats']}")
    print(json.dumps(out["review_payload"], indent=2) if out["review_payload"] else "  nothing to post")