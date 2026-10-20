import sys

from dotenv import load_dotenv

load_dotenv()

from agent.config import load_config
from agent.filters import filter_files
from agent.nodes.fetch_diff import fetch_diff

cfg = load_config()
for n in map(int, sys.argv[1:]):
    files = fetch_diff({"pr_number": n})["diff_files"]
    kept, skipped = filter_files(files, cfg)
    print(f"PR #{n}: kept={[k['path'] for k in kept]} "
          f"skipped={[(s['path'], s['reason']) for s in skipped]}")