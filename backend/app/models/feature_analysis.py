from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class FeatureObservation(BaseModel):
    date: date
    features: dict[str, bool | float | int | None]


class FeatureAnalysisResult(BaseModel):
    indicator_code: str
    region_code: str
    observations: list[FeatureObservation]