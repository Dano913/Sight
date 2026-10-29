from __future__ import annotations

from typing import Any


class ConfidenceEstimator:
    """
    Estima la confianza en la interpretación macroeconómica.

    La confianza mide la coherencia y claridad de la evidencia disponible.
    NO representa:
        - probabilidad de que una predicción futura sea correcta,
        - rentabilidad esperada,
        - calidad de una inversión,
        - intensidad de una oportunidad,
        - nivel de riesgo.

    El estimador evita sumar puntuaciones arbitrarias de cada señal.

    La confianza se determina principalmente mediante:

        1. coherencia entre estado y dirección,
        2. coherencia entre growth, trend y momentum,
        3. presencia de contradicciones,
        4. claridad de la transición,
        5. claridad del régimen,
        6. existencia de señales desconocidas o insuficientes.

    Volatilidad y posición aportan contexto, pero no determinan por sí
    mismas la confianza de la interpretación económica.
    """

    @classmethod
    def estimate(
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
        contradictions: list[str] = []
        supporting_evidence: list[str] = []
        uncertainty: list[str] = []

        cls._evaluate_growth(
            growth=growth,
            supporting_evidence=supporting_evidence,
            uncertainty=uncertainty,
        )

        cls._evaluate_trend(
            trend=trend,
            supporting_evidence=supporting_evidence,
            uncertainty=uncertainty,
        )

        cls._evaluate_momentum(
            momentum=momentum,
            supporting_evidence=supporting_evidence,
            uncertainty=uncertainty,
        )

        cls._detect_cross_signal_contradictions(
            growth=growth,
            trend=trend,
            momentum=momentum,
            contradictions=contradictions,
        )

        cls._evaluate_transition(
            transition=transition,
            uncertainty=uncertainty,
            reasons=reasons,
        )

        cls._evaluate_regime(
            regime=regime,
            uncertainty=uncertainty,
            reasons=reasons,
        )

        cls._evaluate_context(
            volatility=volatility,
            position=position,
            uncertainty=uncertainty,
        )

        coherence = cls._classify_coherence(
            supporting_evidence=supporting_evidence,
            contradictions=contradictions,
            uncertainty=uncertainty,
        )

        state = cls._classify_confidence(
            coherence=coherence,
            contradictions=contradictions,
            uncertainty=uncertainty,
            growth=growth,
            trend=trend,
            momentum=momentum,
            transition=transition,
            regime=regime,
        )

        if supporting_evidence:
            reasons.append(
                f"{len(supporting_evidence)}_supporting_dimensions"
            )

        if contradictions:
            reasons.append(
                f"{len(contradictions)}_cross_signal_contradictions"
            )

        if uncertainty:
            reasons.append(
                f"{len(uncertainty)}_uncertainty_factors"
            )

        return {
            "state": state,
            "coherence": coherence,
            "reasons": reasons,
            "supporting_evidence": supporting_evidence,
            "contradictions": contradictions,
            "uncertainty": uncertainty,
            "context": {
                "regime": regime,
                "transition": {
                    "detected": bool(
                        transition.get("detected", False)
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
            },
        }

    # ------------------------------------------------------------------
    # Individual dimensions
    # ------------------------------------------------------------------

    @staticmethod
    def _evaluate_growth(
        *,
        growth: dict[str, Any],
        supporting_evidence: list[str],
        uncertainty: list[str],
    ) -> None:

        state = growth.get("state", "unknown")
        direction = growth.get("direction", "unknown")
        dynamic_state = growth.get(
            "dynamic_state",
            "unknown",
        )

        if state == "unknown":
            uncertainty.append("unknown_growth_state")
            return

        if direction == "unknown":
            uncertainty.append("unknown_growth_direction")
        elif direction in {
            "improving",
            "deteriorating",
            "stable",
        }:
            supporting_evidence.append(
                "growth_state_and_direction_available"
            )

        if dynamic_state == "unknown":
            uncertainty.append("unknown_growth_dynamic_state")

    @staticmethod
    def _evaluate_trend(
        *,
        trend: dict[str, Any],
        supporting_evidence: list[str],
        uncertainty: list[str],
    ) -> None:

        state = trend.get("state", "unknown")
        direction = trend.get("direction", "unknown")
        strength = trend.get("strength", "unknown")

        if state == "unknown":
            uncertainty.append("unknown_trend_state")
            return

        if state == "mixed":
            uncertainty.append("mixed_trend_structure")

        if direction == "unknown":
            uncertainty.append("unknown_trend_direction")
        else:
            supporting_evidence.append(
                "trend_state_and_direction_available"
            )

        if strength == "unknown":
            uncertainty.append("unknown_trend_strength")

    @staticmethod
    def _evaluate_momentum(
        *,
        momentum: dict[str, Any],
        supporting_evidence: list[str],
        uncertainty: list[str],
    ) -> None:

        state = momentum.get("state", "unknown")
        direction = momentum.get("direction", "unknown")

        if state == "unknown":
            uncertainty.append("unknown_momentum_state")
            return

        if direction == "unknown":
            uncertainty.append("unknown_momentum_direction")
        else:
            supporting_evidence.append(
                "momentum_state_and_direction_available"
            )

    # ------------------------------------------------------------------
    # Cross-signal coherence
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_cross_signal_contradictions(
        *,
        growth: dict[str, Any],
        trend: dict[str, Any],
        momentum: dict[str, Any],
        contradictions: list[str],
    ) -> None:

        growth_state = growth.get("state", "unknown")
        trend_state = trend.get("state", "unknown")
        momentum_state = momentum.get("state", "unknown")

        # Current economic state contradictions.

        if (
            growth_state == "positive"
            and trend_state == "bearish"
        ):
            contradictions.append(
                "positive_growth_vs_bearish_trend"
            )

        elif (
            growth_state == "negative"
            and trend_state == "bullish"
        ):
            contradictions.append(
                "negative_growth_vs_bullish_trend"
            )

        if (
            growth_state == "positive"
            and momentum_state == "negative"
        ):
            contradictions.append(
                "positive_growth_vs_negative_momentum"
            )

        elif (
            growth_state == "negative"
            and momentum_state == "positive"
        ):
            contradictions.append(
                "negative_growth_vs_positive_momentum"
            )

        # Trend / momentum structural divergence.

        if (
            trend_state == "bullish"
            and momentum_state == "negative"
        ):
            contradictions.append(
                "bullish_trend_vs_negative_momentum"
            )

        elif (
            trend_state == "bearish"
            and momentum_state == "positive"
        ):
            contradictions.append(
                "bearish_trend_vs_positive_momentum"
            )

    # ------------------------------------------------------------------
    # Transition
    # ------------------------------------------------------------------

    @staticmethod
    def _evaluate_transition(
        *,
        transition: dict[str, Any],
        uncertainty: list[str],
        reasons: list[str],
    ) -> None:

        detected = bool(
            transition.get("detected", False)
        )

        direction = transition.get(
            "direction",
            "unknown",
        )

        state = transition.get(
            "state",
            "none",
        )

        if not detected:
            if direction == "unknown":
                uncertainty.append(
                    "transition_direction_unknown"
                )
            return

        if direction == "unknown":
            uncertainty.append(
                "detected_transition_without_direction"
            )

        if state == "none":
            uncertainty.append(
                "detected_transition_without_state"
            )

        if direction == "mixed":
            uncertainty.append(
                "mixed_transition_direction"
            )

        if state in {"early", "moderate", "strong"}:
            reasons.append(
                f"{state}_transition_detected"
            )

    # ------------------------------------------------------------------
    # Regime
    # ------------------------------------------------------------------

    @staticmethod
    def _evaluate_regime(
        *,
        regime: str,
        uncertainty: list[str],
        reasons: list[str],
    ) -> None:

        valid_regimes = {
            "expansion",
            "late_expansion",
            "slowdown",
            "stagnation",
            "recovery",
            "contraction",
            "neutral",
        }

        if regime not in valid_regimes:
            uncertainty.append(
                "unknown_regime"
            )
            return

        if regime == "neutral":
            uncertainty.append(
                "neutral_regime"
            )

        reasons.append(
            f"regime_{regime}"
        )

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    @staticmethod
    def _evaluate_context(
        *,
        volatility: dict[str, Any],
        position: dict[str, Any],
        uncertainty: list[str],
    ) -> None:

        volatility_level = volatility.get(
            "level",
            "unknown",
        )
        volatility_stress = volatility.get(
            "stress",
            "unknown",
        )
        volatility_direction = volatility.get(
            "direction",
            "unknown",
        )

        position_state = position.get(
            "position",
            "unknown",
        )
        position_direction = position.get(
            "direction",
            "unknown",
        )

        # These variables do not lower confidence merely because they are
        # elevated or extreme. They only contribute uncertainty when the
        # interpretation itself lacks contextual information.

        if volatility_level == "unknown":
            uncertainty.append(
                "unknown_volatility_level"
            )

        if volatility_stress == "unknown":
            uncertainty.append(
                "unknown_volatility_stress"
            )

        if volatility_direction == "unknown":
            uncertainty.append(
                "unknown_volatility_direction"
            )

        if position_state == "unknown":
            uncertainty.append(
                "unknown_position"
            )

        if position_direction == "unknown":
            uncertainty.append(
                "unknown_position_direction"
            )

    # ------------------------------------------------------------------
    # Coherence
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_coherence(
        *,
        supporting_evidence: list[str],
        contradictions: list[str],
        uncertainty: list[str],
    ) -> str:

        contradiction_count = len(contradictions)
        uncertainty_count = len(uncertainty)
        evidence_count = len(supporting_evidence)

        if contradiction_count >= 3:
            return "low"

        if contradiction_count >= 2:
            return "low"

        if contradiction_count == 1:
            if evidence_count >= 3 and uncertainty_count <= 2:
                return "medium"
            return "low"

        if uncertainty_count >= 5:
            return "low"

        if uncertainty_count >= 3:
            return "medium"

        if evidence_count >= 3:
            return "high"

        if evidence_count >= 2:
            return "medium"

        return "low"

    # ------------------------------------------------------------------
    # Final confidence
    # ------------------------------------------------------------------

    @classmethod
    def _classify_confidence(
        cls,
        *,
        coherence: str,
        contradictions: list[str],
        uncertainty: list[str],
        growth: dict[str, Any],
        trend: dict[str, Any],
        momentum: dict[str, Any],
        transition: dict[str, Any],
        regime: str,
    ) -> str:

        if regime not in {
            "expansion",
            "late_expansion",
            "slowdown",
            "stagnation",
            "recovery",
            "contraction",
            "neutral",
        }:
            return "very_low"

        if (
            coherence == "low"
            or len(contradictions) >= 3
        ):
            return "low"

        if len(uncertainty) >= 5:
            return "low"

        core_states = (
            growth.get("state", "unknown"),
            trend.get("state", "unknown"),
            momentum.get("state", "unknown"),
        )

        if any(
            state == "unknown"
            for state in core_states
        ):
            return "low"

        transition_direction = transition.get(
            "direction",
            "unknown",
        )

        transition_state = transition.get(
            "state",
            "none",
        )

        # Strong coherence with a clearly defined transition can still
        # produce high confidence. Transition != uncertainty.
        if (
            coherence == "high"
            and len(contradictions) == 0
            and len(uncertainty) <= 1
        ):
            if transition_direction != "mixed":
                return "high"

        if (
            coherence in {"high", "medium"}
            and len(contradictions) <= 1
            and transition_state != "unknown"
        ):
            return "moderate"

        if coherence == "medium":
            return "low"

        return "very_low"