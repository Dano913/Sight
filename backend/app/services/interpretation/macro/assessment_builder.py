from __future__ import annotations

from typing import Any


class AssessmentBuilder:
    """
    Construye un resumen semántico de la interpretación económica.

    Este componente no vuelve a clasificar growth, trend, momentum,
    volatility o position.

    Su función es únicamente sintetizar:

        - régimen actual
        - dirección agregada
        - transición
        - coherencia entre las principales dimensiones

    No realiza una valoración de inversión.
    """

    @classmethod
    def build(
        cls,
        *,
        growth: dict[str, Any] | None = None,
        trend: dict[str, Any] | None = None,
        momentum: dict[str, Any] | None = None,
        volatility: dict[str, Any] | None = None,
        position: dict[str, Any] | None = None,
        transition: dict[str, Any] | None = None,
        regime: str = "neutral",
    ) -> dict[str, Any]:

        growth = growth or {}
        trend = trend or {}
        momentum = momentum or {}
        volatility = volatility or {}
        position = position or {}
        transition = transition or {}

        directions = [
            growth.get("direction"),
            trend.get("direction"),
            momentum.get("direction"),
        ]

        improving_count = directions.count("improving")
        deteriorating_count = directions.count("deteriorating")
        stable_count = directions.count("stable")

        known_directions = [
            direction
            for direction in directions
            if direction not in {
                None,
                "unknown",
            }
        ]

        # ==========================================================
        # DIRECCIÓN AGREGADA
        # ==========================================================

        if improving_count >= 2 and improving_count > deteriorating_count:
            directional_bias = "improving"

        elif (
            deteriorating_count >= 2
            and deteriorating_count > improving_count
        ):
            directional_bias = "deteriorating"

        elif (
            stable_count >= 2
            and stable_count > improving_count
            and stable_count > deteriorating_count
        ):
            directional_bias = "stable"

        elif improving_count > 0 and deteriorating_count > 0:
            directional_bias = "mixed"

        elif improving_count == 1 and deteriorating_count == 0:
            directional_bias = "improving"

        elif deteriorating_count == 1 and improving_count == 0:
            directional_bias = "deteriorating"

        else:
            directional_bias = "unknown"

        # ==========================================================
        # COHERENCIA
        # ==========================================================

        if not known_directions:
            coherence = "unknown"
        elif len(known_directions) == 1:
            coherence = "medium"
        elif (
            improving_count == len(known_directions)
            or deteriorating_count == len(known_directions)
            or stable_count == len(known_directions)
        ):
            coherence = "high"
        elif (
            improving_count > 0
            and deteriorating_count > 0
        ):
            coherence = "low"
        else:
            coherence = "medium"

        # ==========================================================
        # TRANSICIÓN
        # ==========================================================

        transition_detected = bool(
            transition.get("detected", False)
        )

        transition_direction = transition.get(
            "direction",
            "unknown",
        )

        transition_state = transition.get(
            "state",
            "none",
        )

        # ==========================================================
        # ASSESSMENT
        # ==========================================================

        assessment_map = {
            "expansion": "expanding",
            "late_expansion": "maturing",
            "slowdown": "slowing",
            "stagnation": "stagnant",
            "recovery": "improving",
            "contraction": "contracting",
            "neutral": "neutral",
        }

        assessment = assessment_map.get(
            regime,
            "neutral",
        )

        # ==========================================================
        # RAZONES DESCRIPTIVAS
        # ==========================================================

        reasons: list[str] = []

        if growth.get("state") == "positive":
            reasons.append("positive_growth")
        elif growth.get("state") == "negative":
            reasons.append("negative_growth")

        if growth.get("direction") == "improving":
            reasons.append("growth_improving")
        elif growth.get("direction") == "deteriorating":
            reasons.append("growth_deteriorating")

        if trend.get("state") == "bullish":
            reasons.append("bullish_trend")
        elif trend.get("state") == "bearish":
            reasons.append("bearish_trend")
        elif trend.get("state") == "mixed":
            reasons.append("mixed_trend")

        if trend.get("direction") == "improving":
            reasons.append("trend_improving")
        elif trend.get("direction") == "deteriorating":
            reasons.append("trend_deteriorating")

        if momentum.get("state") == "positive":
            reasons.append("positive_momentum")
        elif momentum.get("state") == "negative":
            reasons.append("negative_momentum")

        if momentum.get("direction") == "improving":
            reasons.append("momentum_improving")
        elif momentum.get("direction") == "deteriorating":
            reasons.append("momentum_deteriorating")

        if volatility.get("level") == "high":
            reasons.append("high_volatility")
        elif volatility.get("level") == "extreme":
            reasons.append("extreme_volatility")

        if volatility.get("direction") == "rising":
            reasons.append("volatility_rising")
        elif volatility.get("direction") == "falling":
            reasons.append("volatility_falling")

        if position.get("drawdown_state") == "significant":
            reasons.append("significant_drawdown")
        elif position.get("drawdown_state") == "severe":
            reasons.append("severe_drawdown")

        if position.get("position") == "upper_extreme":
            reasons.append("upper_extreme_position")
        elif position.get("position") == "lower_extreme":
            reasons.append("lower_extreme_position")

        if transition_detected:
            reasons.append(
                f"transition_{transition_direction}"
            )

        # ==========================================================
        # CONFIANZA DEL RESUMEN
        # ==========================================================
        #
        # No intenta medir "probabilidad de que el régimen sea
        # correcto". Solo refleja cuánta coherencia estructural
        # tenemos en la interpretación actual.
        #

        transition_confidence = transition.get(
            "confidence",
            "low",
        )

        if coherence == "high":
            confidence = "high"

        elif coherence == "medium":
            if transition_confidence == "high":
                confidence = "high"
            else:
                confidence = "medium"

        else:
            confidence = "low"

        return {
            "state": assessment,
            "directional_bias": directional_bias,
            "regime": regime,
            "coherence": coherence,
            "transition_detected": transition_detected,
            "transition_direction": transition_direction,
            "transition_state": transition_state,
            "confidence": confidence,
            "reasons": reasons,
        }