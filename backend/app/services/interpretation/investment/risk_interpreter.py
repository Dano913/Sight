from __future__ import annotations

from typing import Any


class RiskInterpreter:
    """
    Interpreta la fragilidad y el deterioro del contexto macroeconómico.

    Este componente NO calcula una puntuación acumulativa.

    El riesgo macroeconómico se construye a partir de cuatro
    dimensiones principales:

        - estado económico y dirección,
        - deterioro de tendencia/momentum,
        - estrés de volatilidad,
        - posición y drawdown.

    La transición se interpreta según su dirección:
        - hacia deterioro/contraction -> evidencia de riesgo
        - hacia recuperación/expansion -> no se considera riesgo
        - mixed -> contexto incierto

    El régimen se utiliza como contexto de síntesis y no se vuelve
    a puntuar junto con sus componentes.

    Este componente no evalúa riesgo específico de un activo.
    """

    @classmethod
    def interpret(
        cls,
        *,
        growth: dict[str, Any],
        trend: dict[str, Any],
        momentum: dict[str, Any],
        volatility: dict[str, Any],
        position: dict[str, Any],
        transition: dict[str, Any],
        regime: str,
    ) -> dict[str, Any]:

        reasons: list[str] = []
        risk_dimensions: list[str] = []

        growth_risk = cls._growth_risk(
            growth=growth,
        )

        if growth_risk is not None:
            risk_dimensions.append(growth_risk)
            reasons.append(growth_risk)

        trend_risk = cls._trend_risk(
            trend=trend,
        )

        if trend_risk is not None:
            risk_dimensions.append(trend_risk)
            reasons.append(trend_risk)

        momentum_risk = cls._momentum_risk(
            momentum=momentum,
        )

        if momentum_risk is not None:
            risk_dimensions.append(momentum_risk)
            reasons.append(momentum_risk)

        volatility_risk = cls._volatility_risk(
            volatility=volatility,
        )

        if volatility_risk is not None:
            risk_dimensions.append(volatility_risk)
            reasons.append(volatility_risk)

        position_risk = cls._position_risk(
            position=position,
        )

        if position_risk is not None:
            risk_dimensions.append(position_risk)
            reasons.append(position_risk)

        transition_risk = cls._transition_risk(
            transition=transition,
        )

        if transition_risk is not None:
            risk_dimensions.append(transition_risk)
            reasons.append(transition_risk)

        regime_context = cls._regime_context(
            regime=regime,
        )

        if regime_context is not None:
            reasons.append(regime_context)

        state = cls._classify_state(
            regime=regime,
            risk_dimensions=risk_dimensions,
            volatility=volatility,
            position=position,
            transition=transition,
        )

        return {
            "state": state,
            "dimensions": {
                "growth": growth_risk,
                "trend": trend_risk,
                "momentum": momentum_risk,
                "volatility": volatility_risk,
                "position": position_risk,
                "transition": transition_risk,
            },
            "regime": regime,
            "transition": {
                "detected": bool(
                    transition.get(
                        "detected",
                        False,
                    )
                ),
                "direction": (
                    transition.get("direction")
                    or "unknown"
                ),
                "state": (
                    transition.get("state")
                    or "none"
                ),
            },
            "reasons": reasons,
        }

    @staticmethod
    def _growth_risk(
        *,
        growth: dict[str, Any],
    ) -> str | None:

        state = growth.get(
            "state",
            "unknown",
        )

        direction = growth.get(
            "direction",
            "unknown",
        )

        if (
            state == "negative"
            and direction == "deteriorating"
        ):
            return "negative_growth_deteriorating"

        if (
            state == "negative"
            and direction in {
                "stable",
                "unknown",
            }
        ):
            return "negative_growth"

        if (
            state == "positive"
            and direction == "deteriorating"
        ):
            return "growth_deteriorating"

        if state == "flat":
            return "flat_growth"

        return None

    @staticmethod
    def _trend_risk(
        *,
        trend: dict[str, Any],
    ) -> str | None:

        state = trend.get(
            "state",
            "unknown",
        )

        direction = trend.get(
            "direction",
            "unknown",
        )

        reversal = bool(
            trend.get(
                "reversal",
                False,
            )
        )

        if (
            state == "bearish"
            and direction == "deteriorating"
        ):
            return "bearish_trend_deteriorating"

        if (
            state == "bearish"
            and direction in {
                "stable",
                "unknown",
            }
        ):
            return "bearish_trend"

        if (
            state == "bullish"
            and direction == "deteriorating"
        ):
            if reversal:
                return "bullish_trend_reversing"

            return "bullish_trend_deteriorating"

        if (
            state == "mixed"
            and direction == "deteriorating"
        ):
            return "mixed_trend_deteriorating"

        return None

    @staticmethod
    def _momentum_risk(
        *,
        momentum: dict[str, Any],
    ) -> str | None:

        state = momentum.get(
            "state",
            "unknown",
        )

        direction = momentum.get(
            "direction",
            "unknown",
        )

        if (
            state == "negative"
            and direction == "deteriorating"
        ):
            return "negative_momentum_deteriorating"

        if (
            state == "negative"
            and direction in {
                "stable",
                "unknown",
            }
        ):
            return "negative_momentum"

        if (
            state == "positive"
            and direction == "deteriorating"
        ):
            return "positive_momentum_deteriorating"

        return None

    @staticmethod
    def _volatility_risk(
        *,
        volatility: dict[str, Any],
    ) -> str | None:

        level = volatility.get(
            "level",
            "unknown",
        )

        direction = volatility.get(
            "direction",
            "unknown",
        )

        stress = volatility.get(
            "stress",
            "unknown",
        )

        shock = bool(
            volatility.get(
                "shock",
                False,
            )
        )

        if shock:
            return "volatility_shock"

        if stress == "extreme":
            return "extreme_volatility_stress"

        if stress == "elevated":
            if direction == "rising":
                return "elevated_volatility_stress_rising"

            return "elevated_volatility_stress"

        if (
            level == "extreme"
            and direction == "rising"
        ):
            return "extreme_volatility_rising"

        if (
            level == "high"
            and direction == "rising"
        ):
            return "high_volatility_rising"

        if level == "high":
            return "high_volatility"

        return None

    @staticmethod
    def _position_risk(
        *,
        position: dict[str, Any],
    ) -> str | None:

        drawdown_state = position.get(
            "drawdown_state",
            "unknown",
        )

        direction = position.get(
            "direction",
            "unknown",
        )

        if drawdown_state == "severe":
            return "severe_drawdown"

        if drawdown_state == "significant":
            return "significant_drawdown"

        if (
            drawdown_state == "minor"
            and direction == "falling"
        ):
            return "drawdown_falling"

        return None

    @staticmethod
    def _transition_risk(
        *,
        transition: dict[str, Any],
    ) -> str | None:

        if not transition.get(
            "detected",
            False,
        ):
            return None

        direction = transition.get(
            "direction",
            "unknown",
        )

        state = transition.get(
            "state",
            "none",
        )

        if direction == "toward_contraction":
            return (
                f"strong_contraction_transition"
                if state == "strong"
                else "contraction_transition"
            )

        if direction == "toward_slowdown":
            return (
                f"strong_slowdown_transition"
                if state == "strong"
                else "slowdown_transition"
            )

        if direction == "toward_deterioration":
            return (
                f"strong_deterioration_transition"
                if state == "strong"
                else "deterioration_transition"
            )

        if direction == "mixed":
            return "mixed_transition"

        return None

    @staticmethod
    def _regime_context(
        *,
        regime: str,
    ) -> str | None:

        if regime == "contraction":
            return "contraction_regime"

        if regime == "slowdown":
            return "slowdown_regime"

        if regime == "stagnation":
            return "stagnation_regime"

        return None

    @classmethod
    def _classify_state(
        cls,
        *,
        regime: str,
        risk_dimensions: list[str],
        volatility: dict[str, Any],
        position: dict[str, Any],
        transition: dict[str, Any],
    ) -> str:

        severe_conditions = {
            "negative_growth_deteriorating",
            "bearish_trend_deteriorating",
            "negative_momentum_deteriorating",
            "extreme_volatility_stress",
            "volatility_shock",
            "severe_drawdown",
            "strong_contraction_transition",
        }

        if (
            regime == "contraction"
            and any(
                condition in severe_conditions
                for condition in risk_dimensions
            )
        ):
            return "high"

        if any(
            condition in severe_conditions
            for condition in risk_dimensions
        ):
            return "high"

        moderate_conditions = {
            "negative_growth",
            "growth_deteriorating",
            "bearish_trend",
            "bullish_trend_reversing",
            "bullish_trend_deteriorating",
            "mixed_trend_deteriorating",
            "negative_momentum",
            "positive_momentum_deteriorating",
            "high_volatility_rising",
            "high_volatility",
            "elevated_volatility_stress",
            "elevated_volatility_stress_rising",
            "significant_drawdown",
            "drawdown_falling",
            "contraction_transition",
            "slowdown_transition",
            "deterioration_transition",
        }

        moderate_count = sum(
            condition in moderate_conditions
            for condition in risk_dimensions
        )

        if moderate_count >= 2:
            return "elevated"

        if moderate_count == 1:
            return "moderate"

        if (
            regime in {
                "slowdown",
                "stagnation",
            }
        ):
            return "moderate"

        if (
            transition.get("direction")
            == "toward_deterioration"
        ):
            return "moderate"

        return "low"