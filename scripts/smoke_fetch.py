import sys

from dotenv import load_dotenv

load_dotenv()

from agent.nodes.fetch_diff import fetch_diff

out = fetch_diff({"pr_number": int(sys.argv[1])})
for f in out["diff_files"]:
    print(f["path"], f["status"], f"+{f['additions']}/-{f['deletions']}",
          "patch" if f["patch"] else "NO PATCH")