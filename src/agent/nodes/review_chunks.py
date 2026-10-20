import json
from pathlib import Path

from groq import BadRequestError
from pydantic import ValidationError

from agent.annotate import annotate_chunk
from agent.clients.llm import ask_json
from agent.schemas import ChunkReview
from agent.validation import validate_findings

PROMPT = (Path(__file__).resolve().parents[1] / "prompts" / "review.md").read_text(
    encoding="utf-8"
)


def _new_usage() -> dict:
    return {"calls": 0, "tokens": 0, "prompt_tokens": 0, "completion_tokens": 0, "latency_s": 0.0}


def _review_one(annotated: str):
    """Ask the model once, retry once on invalid output. Returns (review, usage, error)."""
    usage = _new_usage()
    user, error = annotated, "unknown"
    for _ in range(2):
        usage["calls"] += 1
        try:
            out = ask_json(PROMPT, user)
        except (BadRequestError, json.JSONDecodeError) as e:
            error = f"model output rejected: {str(e)[:200]}"
        else:
            usage["tokens"] += out["tokens"]
            usage["prompt_tokens"] += out.get("prompt_tokens", 0)
            usage["completion_tokens"] += out.get("completion_tokens", 0)
            usage["latency_s"] += out["latency_s"]
            try:
                return ChunkReview.model_validate(out["data"]), usage, None
            except ValidationError as e:
                error = f"schema mismatch: {str(e)[:300]}"
        user = (
            f"{annotated}\n\nYour previous reply was invalid ({error}). "
            "Reply again with only valid JSON in the required shape."
        )
    return None, usage, error


def review_chunks(state: dict) -> dict:
    findings, dropped, notes = [], [], []
    usage = _new_usage()
    for chunk in state["chunks"]:
        annotated, valid = annotate_chunk(chunk["text"])
        review, u, error = _review_one(annotated)
        for k in usage:
            usage[k] += u[k]
        if review is None:
            notes.append(f"Chunk {chunk['index']} ({', '.join(chunk['files'])}) skipped: {error}")
            continue
        kept, bad = validate_findings(review.findings, valid)
        findings += [f.model_dump() for f in kept]
        dropped += [{**f.model_dump(), "reason": r} for f, r in bad]
    usage["latency_s"] = round(usage["latency_s"], 2)
    return {"findings": findings, "dropped_findings": dropped, "notes": notes, "usage": usage}