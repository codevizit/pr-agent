from agent.chunker import chunk_files
from agent.config import load_config
from agent.filters import filter_files


def filter_chunk(state: dict) -> dict:
    cfg = load_config()
    kept, skipped = filter_files(state["diff_files"], cfg)
    return {
        "kept_files": kept,
        "skipped_files": skipped,
        "chunks": chunk_files(kept, cfg["max_chunk_chars"]),
    }