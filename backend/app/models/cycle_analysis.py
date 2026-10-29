from typing import Any
from pydantic import BaseModel


class CycleEvidence(BaseModel):
    method: str
    period_years: float
    power: float


class RobustCycle(BaseModel):
    period_years: float
    score: float
    confidence: str
    methods: list[str]
    method_count: int
    method_coverage: float
    cycles_observable: float
    period_dispersion: float
    evidence: list[CycleEvidence]


class CycleAnalysisResult(BaseModel):
    start_date: str
    end_date: str
    observations: int
    growth_observations: int

    growth: dict[str, Any]
    hp: dict[str, Any]
    linear_detrend: dict[str, Any]

    robust_cycles: list[RobustCycle]