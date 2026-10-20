import sys

from dotenv import load_dotenv

load_dotenv()

from agent.annotate import annotate_chunk
from agent.graphs.review_graph import build_review_graph

app = build_review_graph()
for n in map(int, sys.argv[1:]):
    out = app.invoke({"pr_number": n})
    if not out["chunks"]:
        print(f"PR #{n}: no chunks")
    for c in out["chunks"]:
        text, valid = annotate_chunk(c["text"])
        print(f"PR #{n} chunk {c['index']} valid lines: {({p: sorted(s) for p, s in valid.items()})}")
        print(text)
        print("-" * 40)