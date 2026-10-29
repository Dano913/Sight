from __future__ import annotations

from collections import Counter
from typing import Any


class GrowthRegimeAnalyzer:
    """Classifies the growth phase using growth, trend and momentum."""

    @staticmethod
    def analyze(
        interpretation: dict[str, Any] | None,
        evidence: list[dict[str, Any]],
    ) -> None:
        if not interpretation:
            return

        growth_state = (interpretation.get("growth") or {}).get("state")
        trend = interpretation.get("trend") or {}
        trend_state = trend.get("state")
        trend_direction = trend.get("direction")

        momentum = interpretation.get("momentum") or {}
        momentum_state = momentum.get("state")
        momentum_direction = momentum.get("direction")

        if growth_state == "positive":
            if (
                trend_state == "bullish"
                and momentum_state == "positive"
                and momentum_direction in {"improving", "stable"}
            ):
                regime = "expansion"
            elif (
                trend_state in {"bullish", "mixed"}
                and (
                    trend_direction == "deteriorating"
                    or momentum_direction == "deteriorating"
                )
            ):
                regime = "late_expansion"
            else:
                return

        elif growth_state == "negative":
            # An improving trend during negative growth suggests recovery,
            # even if the underlying trend has not yet turned bullish.
            if (
                trend_direction == "improving"
                or momentum_direction == "improving"
            ):
                regime = "recovery"
            elif trend_state == "bearish":
                regime = "contraction"
            else:
                return

        elif growth_state == "flat":
            regime = "stagnation"

        else:
            return

        evidence.append({
            "family": "growth",
            "indicator": "GDP",
            "regime": regime,
            "weight": 5.0,
            "confidence": "medium",
            "reason": (
                f"growth={growth_state}, trend={trend_state}, "
                f"trend_direction={trend_direction}, "
                f"momentum={momentum_state}, "
                f"momentum_direction={momentum_direction}"
            ),
        })


class ActivityRegimeAnalyzer:
    """Classifies activity using industrial production and retail sales."""

    CODES = {"INDUSTRIAL_PRODUCTION", "RETAIL_SALES"}

    @staticmethod
    def _direction(
        interpretation: dict[str, Any] | None,
    ) -> str | None:
        if not interpretation:
            return None

        growth = interpretation.get("growth") or {}
        trend = interpretation.get("trend") or {}

        # Growth direction describes acceleration, not the direction
        # of the underlying economic series.
        growth_state = growth.get("state")
        trend_state = trend.get("state")

        if growth_state == "positive":
            return "up"
        if growth_state == "negative":
            return "down"
        if growth_state == "flat":
            return "flat"

        if trend_state == "bullish":
            return "up"
        if trend_state == "bearish":
            return "down"

        return None

    @classmethod
    def analyze(
        cls,
        interpretations: dict[str, dict[str, Any] | None],
        evidence: list[dict[str, Any]],
    ) -> None:
        directions = {
            code: cls._direction(interpretations.get(code))
            for code in cls.CODES
            if code in interpretations
        }

        valid = [direction for direction in directions.values() if direction]

        if len(valid) < 2:
            return

        counts = Counter(valid)

        if counts["up"] >= 2:
            regime = "expansion"
            target_direction = "up"
        elif counts["down"] >= 2:
            regime = "contraction"
            target_direction = "down"
        elif counts["flat"] >= 2:
            regime = "stagnation"
            target_direction = "flat"
        else:
            return

        supporting_indicators = [
            code
            for code, direction in directions.items()
            if direction == target_direction
        ]

        evidence.append({
            "family": "activity",
            "indicator": "ACTIVITY",
            "indicators": supporting_indicators,
            "supporting_indicators": supporting_indicators,
            "regime": regime,
            "weight": 4.0,
            "confidence": "medium",
            "reason": f"activity_directions={directions}",
        })


class EmploymentRegimeAnalyzer:
    """Classifies labour-market conditions from unemployment."""

    @staticmethod
    def analyze(
        interpretation: dict[str, Any] | None,
        evidence: list[dict[str, Any]],
    ) -> None:
        if not interpretation:
            return

        trend = interpretation.get("trend") or {}
        growth = interpretation.get("growth") or {}

        growth_state = growth.get("state")
        trend_state = trend.get("state")
        trend_direction = trend.get("direction")

        # Do not infer the direction of unemployment from acceleration
        # or from a generic bullish/bearish trend label alone.
        # "Improving" means the trend is improving, not necessarily that
        # the unemployment rate is falling.
        if growth_state == "negative":
            regime = "expansion"
        elif growth_state == "positive":
            regime = "contraction"
        else:
            return

        evidence.append({
            "family": "employment",
            "indicator": "UNEMPLOYMENT",
            "regime": regime,
            "weight": 3.0,
            "confidence": "medium",
            "reason": (
                f"unemployment_growth={growth_state}, "
                f"unemployment_trend={trend_state}, "
                f"trend_direction={trend_direction}"
            ),
        })


class InflationRegimeAnalyzer:
    """Identifies inflation pressure from inflation and volatility."""

    @staticmethod
    def analyze(
        interpretation: dict[str, Any] | None,
        evidence: list[dict[str, Any]],
    ) -> None:
        if not interpretation:
            return

        growth = interpretation.get("growth") or {}
        trend = interpretation.get("trend") or {}
        volatility = interpretation.get("volatility") or {}

        growth_state = growth.get("state")
        trend_state = trend.get("state")
        stress = volatility.get("stress")
        shock = bool(volatility.get("shock"))

        elevated_volatility = stress in {"elevated", "extreme"} or shock

        if (
            growth_state == "positive"
            and trend_state == "bullish"
        ) or elevated_volatility:
            regime = "inflation_stress"
        elif growth_state == "negative" and trend_state == "bearish":
            regime = "disinflation"
        else:
            return

        evidence.append({
            "family": "inflation",
            "indicator": "INFLATION",
            "regime": regime,
            "weight": 2.0,
            "confidence": "medium",
            "reason": (
                f"inflation_growth={growth_state}, "
                f"inflation_trend={trend_state}, "
                f"volatility_stress={stress}, shock={shock}"
            ),
        })


class FinancialRegimeAnalyzer:
    """Identifies financial stress from volatility and market position."""

    CODES = {"INTEREST_RATE", "FINANCIAL_CONDITIONS"}

    @staticmethod
    def _is_stress(
        interpretation: dict[str, Any] | None,
    ) -> bool:
        if not interpretation:
            return False

        volatility = interpretation.get("volatility") or {}
        position = interpretation.get("position") or {}

        stress = volatility.get("stress")
        shock = bool(volatility.get("shock"))
        drawdown_state = position.get("drawdown_state")
        severe_drawdown = bool(position.get("severe_drawdown"))

        return (
            stress in {"elevated", "extreme"}
            or shock
            or drawdown_state == "severe_drawdown"
            or severe_drawdown
        )

    @classmethod
    def analyze(
        cls,
        interpretations: dict[str, dict[str, Any] | None],
        evidence: list[dict[str, Any]],
    ) -> None:
        for code, interpretation in interpretations.items():
            if code not in cls.CODES or not cls._is_stress(interpretation):
                continue

            evidence.append({
                "family": "financial",
                "indicator": code,
                "regime": "financial_stress",
                "weight": 2.0,
                "confidence": "medium",
                "reason": f"financial_stress_indicator={code}",
            })