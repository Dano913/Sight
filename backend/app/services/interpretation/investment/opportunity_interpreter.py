from __future__ import annotations

from typing import Any


class OpportunityInterpreter:
    """
    Interpreta la presencia de condiciones macroeconómicas compatibles
    con una oportunidad de inversión.

    Este componente NO:
        - calcula una puntuación acumulativa,
        - selecciona activos,
        - determina valoración,
        - recomienda comprar o vender,
        - interpreta automáticamente una posición baja como oportunidad.

    La oportunidad se entiende como una combinación de evidencia macro
    potencialmente favorable y/o un cambio de régimen que pueda justificar
    un análisis posterior.

    La interpretación se mantiene separada de:
        - environment: descripción del entorno macro,
        - risk: fragilidad o deterioro,
        - confidence: calidad/coherencia de la evidencia.
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
        evidence: list[dict[str, Any]] = []

        cls._add_growth_evidence(
            growth=growth,
            reasons=reasons,
            evidence=evidence,
        )

        cls._add_trend_evidence(
            trend=trend,
            reasons=reasons,
            evidence=evidence,
        )

        cls._add_momentum_evidence(
            momentum=momentum,
            reasons=reasons,
            evidence=evidence,
        )

        cls._add_transition_evidence(
            transition=transition,
            reasons=reasons,
            evidence=evidence,
        )

        cls._add_regime_evidence(
            regime=regime,
            reasons=reasons,
            evidence=evidence,
        )

        cls._add_volatility_context(
            volatility=volatility,
            reasons=reasons,
            evidence=evidence,
        )

        cls._add_position_context(
            position=position,
            reasons=reasons,
            evidence=evidence,
        )

        state = cls._classify_state(
            growth=growth,
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            transition=transition,
            regime=regime,
        )

        return {
            "state": state,
            "regime": regime,
            "transition": {
                "detected": bool(transition.get("detected", False)),
                "direction": transition.get("direction") or "unknown",
                "state": transition.get("state") or "none",
            },
            "evidence": evidence,
            "reasons": reasons,
            "context": {
                "volatility": {
                    "level": volatility.get("level", "unknown"),
                    "direction": volatility.get("direction", "unknown"),
                    "stress": volatility.get("stress", "unknown"),
                    "shock": bool(volatility.get("shock", False)),
                },
                "position": {
                    "position": position.get("position", "unknown"),
                    "direction": position.get("direction", "unknown"),
                    "drawdown_state": position.get(
                        "drawdown_state",
                        "unknown",
                    ),
                    "extreme": position.get("extreme", "none"),
                },
            },
        }

    @staticmethod
    def _add_growth_evidence(
        *,
        growth: dict[str, Any],
        reasons: list[str],
        evidence: list[dict[str, Any]],
    ) -> None:

        state = growth.get("state", "unknown")
        direction = growth.get("direction", "unknown")
        dynamic_state = growth.get("dynamic_state", "unknown")

        if state == "positive" and direction == "improving":
            reason = "positive_growth_improving"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "growth",
                    "signal": reason,
                    "meaning": "positive growth with improving direction",
                }
            )

        elif state == "positive" and dynamic_state == "accelerating":
            reason = "positive_growth_accelerating"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "growth",
                    "signal": reason,
                    "meaning": "positive growth with accelerating dynamics",
                }
            )

        elif state == "negative" and direction == "improving":
            reason = "negative_growth_improving"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "growth",
                    "signal": reason,
                    "meaning": "negative growth but improving direction",
                }
            )

    @staticmethod
    def _add_trend_evidence(
        *,
        trend: dict[str, Any],
        reasons: list[str],
        evidence: list[dict[str, Any]],
    ) -> None:

        state = trend.get("state", "unknown")
        direction = trend.get("direction", "unknown")
        strength = trend.get("strength", "unknown")

        if state == "bullish" and direction == "strengthening":
            reason = "bullish_trend_strengthening"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "trend",
                    "signal": reason,
                    "meaning": "bullish trend with strengthening dynamics",
                }
            )

        elif state == "bullish" and direction == "stable":
            reason = "bullish_trend_stable"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "trend",
                    "signal": reason,
                    "meaning": "bullish trend remains stable",
                    "strength": strength,
                }
            )

        elif state == "bearish" and direction == "improving":
            reason = "bearish_trend_improving"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "trend",
                    "signal": reason,
                    "meaning": "bearish trend showing improvement",
                }
            )

    @staticmethod
    def _add_momentum_evidence(
        *,
        momentum: dict[str, Any],
        reasons: list[str],
        evidence: list[dict[str, Any]],
    ) -> None:

        state = momentum.get("state", "unknown")
        direction = momentum.get("direction", "unknown")

        if state == "positive" and direction == "improving":
            reason = "positive_momentum_improving"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "momentum",
                    "signal": reason,
                    "meaning": "positive momentum with improving dynamics",
                }
            )

        elif state == "negative" and direction == "improving":
            reason = "negative_momentum_improving"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "momentum",
                    "signal": reason,
                    "meaning": "negative momentum but improving dynamics",
                }
            )

    @staticmethod
    def _add_transition_evidence(
        *,
        transition: dict[str, Any],
        reasons: list[str],
        evidence: list[dict[str, Any]],
    ) -> None:

        if not transition.get("detected", False):
            return

        direction = transition.get("direction", "unknown")
        state = transition.get("state", "none")

        opportunity_directions = {
            "toward_recovery",
            "toward_expansion",
            "toward_improvement",
        }

        if direction in opportunity_directions:
            reason = f"{direction}_transition"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "transition",
                    "signal": reason,
                    "meaning": (
                        "economic dynamics are moving toward a "
                        "potentially more supportive state"
                    ),
                    "state": state,
                }
            )

        elif direction == "mixed":
            evidence.append(
                {
                    "type": "transition",
                    "signal": "mixed_transition",
                    "meaning": "transition evidence is directionally mixed",
                    "state": state,
                }
            )

    @staticmethod
    def _add_regime_evidence(
        *,
        regime: str,
        reasons: list[str],
        evidence: list[dict[str, Any]],
    ) -> None:

        if regime == "recovery":
            reason = "recovery_regime"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "regime",
                    "signal": reason,
                    "meaning": "current regime is classified as recovery",
                }
            )

        elif regime == "expansion":
            reason = "expansion_regime"
            reasons.append(reason)
            evidence.append(
                {
                    "type": "regime",
                    "signal": reason,
                    "meaning": "current regime is classified as expansion",
                }
            )

        elif regime == "late_expansion":
            evidence.append(
                {
                    "type": "regime",
                    "signal": "late_expansion_regime",
                    "meaning": (
                        "current regime is late expansion; "
                        "opportunity context requires additional evidence"
                    ),
                }
            )

    @staticmethod
    def _add_volatility_context(
        *,
        volatility: dict[str, Any],
        reasons: list[str],
        evidence: list[dict[str, Any]],
    ) -> None:

        level = volatility.get("level", "unknown")
        direction = volatility.get("direction", "unknown")
        stress = volatility.get("stress", "unknown")
        shock = bool(volatility.get("shock", False))

        if shock:
            evidence.append(
                {
                    "type": "volatility",
                    "signal": "volatility_shock",
                    "meaning": (
                        "volatility shock is present; opportunity "
                        "interpretation requires additional context"
                    ),
                }
            )
            return

        if direction == "falling":
            reasons.append("falling_volatility")
            evidence.append(
                {
                    "type": "volatility",
                    "signal": "falling_volatility",
                    "meaning": "volatility is decreasing",
                }
            )
        elif stress in {"elevated", "extreme"}:
            evidence.append(
                {
                    "type": "volatility",
                    "signal": "volatility_stress",
                    "meaning": (
                        "volatility is historically elevated; "
                        "this is contextual rather than inherently "
                        "positive or negative"
                    ),
                    "level": level,
                    "stress": stress,
                }
            )

    @staticmethod
    def _add_position_context(
        *,
        position: dict[str, Any],
        reasons: list[str],
        evidence: list[dict[str, Any]],
    ) -> None:

        position_state = position.get("position", "unknown")
        direction = position.get("direction", "unknown")
        drawdown_state = position.get("drawdown_state", "unknown")
        extreme = position.get("extreme", "none")

        if position_state in {"lower_extreme", "lower"}:
            evidence.append(
                {
                    "type": "position",
                    "signal": "lower_position",
                    "meaning": (
                        "the indicator is at a relatively low historical "
                        "position; this does not by itself establish an "
                        "investment opportunity"
                    ),
                    "position": position_state,
                }
            )

        if drawdown_state in {"significant", "severe"}:
            evidence.append(
                {
                    "type": "position",
                    "signal": "drawdown_context",
                    "meaning": (
                        "the indicator is experiencing a material drawdown; "
                        "this is contextual and requires interpretation "
                        "alongside economic direction"
                    ),
                    "drawdown_state": drawdown_state,
                }
            )

        if direction == "recovering":
            evidence.append(
                {
                    "type": "position",
                    "signal": "position_recovering",
                    "meaning": "the indicator is recovering from a lower position",
                    "extreme": extreme,
                }
            )

    @classmethod
    def _classify_state(
        cls,
        *,
        growth: dict[str, Any],
        trend: dict[str, Any],
        momentum: dict[str, Any],
        volatility: dict[str, Any],
        transition: dict[str, Any],
        regime: str,
    ) -> str:

        transition_direction = transition.get("direction", "unknown")
        transition_state = transition.get("state", "none")

        growth_state = growth.get("state", "unknown")
        growth_direction = growth.get("direction", "unknown")
        growth_dynamic = growth.get("dynamic_state", "unknown")

        trend_state = trend.get("state", "unknown")
        trend_direction = trend.get("direction", "unknown")

        momentum_state = momentum.get("state", "unknown")
        momentum_direction = momentum.get("direction", "unknown")

        volatility_stress = volatility.get("stress", "unknown")
        volatility_shock = bool(volatility.get("shock", False))

        strong_transition = transition_state in {"moderate", "strong"}

        improving_evidence = 0

        if growth_direction == "improving":
            improving_evidence += 1

        if growth_dynamic == "accelerating":
            improving_evidence += 1

        if trend_direction == "strengthening":
            improving_evidence += 1

        if momentum_direction == "improving":
            improving_evidence += 1

        if transition_direction in {
            "toward_recovery",
            "toward_expansion",
            "toward_improvement",
        }:
            improving_evidence += 2

        supportive_regime = regime in {"recovery", "expansion"}

        if (
            improving_evidence >= 3
            and supportive_regime
            and not volatility_shock
        ):
            return "established"

        if (
            transition_direction in {
                "toward_recovery",
                "toward_expansion",
                "toward_improvement",
            }
            and strong_transition
        ):
            return "emerging"

        if (
            growth_state == "positive"
            and trend_state == "bullish"
            and momentum_state == "positive"
            and not volatility_shock
        ):
            return "supportive"

        if (
            growth_direction == "improving"
            or trend_direction == "strengthening"
            or momentum_direction == "improving"
        ):
            return "emerging"

        if volatility_stress == "extreme" or volatility_shock:
            return "uncertain"

        return "limited"