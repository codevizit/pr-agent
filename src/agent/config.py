from pathlib import Path

import yaml

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config.yaml"


def load_config(path: str | Path | None = None) -> dict:
    with open(path or DEFAULT_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if cfg["max_chunk_chars"] < 1000:
        raise ValueError("max_chunk_chars must be at least 1000")
    if cfg.get("min_severity") not in ("low", "medium", "high"):
        raise ValueError("min_severity must be low, medium or high")
    return cfg