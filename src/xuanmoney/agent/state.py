from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from xuanmoney.domain import AnalysisResult


class AgentPhase(StrEnum):
    RECEIVED = "received"
    COMPUTING = "computing"
    VALIDATING = "validating"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class FinanceAgentState(BaseModel):
    query: str
    phase: AgentPhase = AgentPhase.RECEIVED
    plan: list[str] = Field(default_factory=list)
    result: AnalysisResult | None = None
    errors: list[str] = Field(default_factory=list)
