from typing import TypedDict


class ReviewState(TypedDict, total=False):
    pr_number: int
    diff_files: list[dict]
    kept_files: list[dict]
    skipped_files: list[dict]
    chunks: list[dict]
    findings: list[dict]
    dropped_findings: list[dict]
    notes: list[str]
    usage: dict
    review_payload: dict | None
    post_stats: dict