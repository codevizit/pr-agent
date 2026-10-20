import sys

from dotenv import load_dotenv

load_dotenv()

from agent.graphs.review_graph import build_review_graph

app = build_review_graph()
for n in map(int, sys.argv[1:]):
    out = app.invoke({"pr_number": n})
    print(f"PR #{n}: findings={len(out['findings'])} dropped={len(out['dropped_findings'])} "
          f"notes={out['notes']} usage={out['usage']}")
    for f in out["findings"]:
        print(f"  {f['path']}:{f['line']} [{f['severity']}/{f['category']}] {f['title']}")
        print(f"    {f['explanation']}")
        if f["suggestion"]:
            print(f"    fix: {f['suggestion']}")
    for d in out["dropped_findings"]:
        print(f"  DROPPED {d['path']}:{d['line']} ({d['reason']}) {d['title']}")