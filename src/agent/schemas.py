from typing import Literal

from pydantic import BaseModel, Field


class Finding(BaseModel):
    path: str
    line: int
    severity: Literal["low", "medium", "high"]
    category: Literal["bug", "security"]
    title: str = Field(max_length=100)
    explanation: str
    suggestion: str | None = None


class ChunkReview(BaseModel):
    findings: list[Finding] = []