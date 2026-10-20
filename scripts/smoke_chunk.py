import os
import sys

from dotenv import load_dotenv

load_dotenv()

from agent.chunker import chunk_files
from agent.config import load_config
from agent.filters import filter_files
from agent.nodes.fetch_diff import fetch_diff

cfg = load_config()
max_chars = int(os.getenv("MAX_CHARS", cfg["max_chunk_chars"]))
for n in map(int, sys.argv[1:]):
    files = fetch_diff({"pr_number": n})["diff_files"]
    kept, _ = filter_files(files, cfg)
    chunks = chunk_files(kept, max_chars)
    sizes = [c["chars"] for c in chunks]
    assert all(s <= max_chars for s in sizes), "a chunk is over the limit"
    print(f"PR #{n}: max={max_chars} chunks={len(chunks)} sizes={sizes} "
          f"files={[c['files'] for c in chunks]}")
    if os.getenv("SHOW"):
        for c in chunks:
            print("-" * 40)
            print(c["text"])