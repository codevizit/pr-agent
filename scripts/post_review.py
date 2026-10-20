import os
import sys

from dotenv import load_dotenv

load_dotenv()

from agent.graphs.review_graph import build_review_graph

n = int(sys.argv[1])
repo = os.environ.get("GITHUB_REPO", "?")
answer = input(f"Run the reviewer and POST comments to {repo} PR #{n}? [y/N] ")
if answer.strip().lower() != "y":
    sys.exit("Cancelled. Nothing was posted.")
os.environ["PR_AGENT_POST"] = "1"
out = build_review_graph().invoke({"pr_number": n})
print(f"PR #{n}: stats={out['post_stats']}")