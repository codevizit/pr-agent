import sys

from dotenv import load_dotenv

load_dotenv()

from agent.graphs.review_graph import build_review_graph

app = build_review_graph()
for n in map(int, sys.argv[1:]):
    out = app.invoke({"pr_number": n})
    print(f"PR #{n}: files={len(out['diff_files'])} kept={len(out['kept_files'])} "
          f"skipped={len(out['skipped_files'])} chunks={len(out['chunks'])} "
          f"sizes={[c['chars'] for c in out['chunks']]}")