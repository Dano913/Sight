from __future__ import annotations

from typing import Any


class TransitionDetector:
    """
    Detecta cambios en la dinámica económica a partir de los
    intérpretes estructurales.

    La transición describe evolución del entorno económico.
    No clasifica oportunidades, riesgos ni valoraciones.

    Semántica principal:

        state:
            none / early / moderate / strong

        direction:
            toward_improvement
            toward_deterioration
            toward_slowdown
            toward_recovery
            toward_expansion
            toward_contraction
            mixed
            unknown

        type:
            tipo de transición dominante.

        confidence:
            confianza en la detección de la transición.

    Importante:
        volatilidad, drawdown y posición no son por sí mismos
        transiciones económicas. Pueden actuar como evidencia
        contextual, pero no deben convertirse automáticamente
        en una transición.
    """

    @staticmethod
    def detect(
        *,
        growth: dict[str, Any] | None = None,
        trend: dict[str, Any] | None = None,
        momentum: dict[str, Any] | None = None,
        volatility: dict[str, Any] | None = None,
        position: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        growth = growth or {}
        trend = trend or {}
        momentum = momentum or {}
        volatility = volatility or {}
        position = position or {}

        evidence: list[dict[str, Any]] = []

        # ==========================================================
        # DESACELERACIÓN
        # ==========================================================

        if (
            growth.get("state") == "positive"
            and growth.get("direction") == "deteriorating"
        ):
            evidence.append(
                {
                    "type": "toward_slowdown",
                    "weight": 2,
                    "reason": "positive_growth_but_deteriorating_growth_direction",
                }
            )

        if (
            trend.get("direction") == "deteriorating"
            and trend.get("state") in {
                "bullish",
                "mixed",
            }
        ):
            evidence.append(
                {
                    "type": "toward_slowdown",
                    "weight": 2,
                    "reason": "trend_deteriorating_from_non_bearish_state",
                }
            )

        if (
            momentum.get("state") == "positive"
            and momentum.get("direction") == "deteriorating"
        ):
            evidence.append(
                {
                    "type": "toward_slowdown",
                    "weight": 2,
                    "reason": "positive_momentum_but_deteriorating",
                }
            )

        # ==========================================================
        # CONTRACCIÓN
        # ==========================================================

        if (
            growth.get("state") == "negative"
            and growth.get("direction") == "deteriorating"
        ):
            evidence.append(
                {
                    "type": "toward_contraction",
                    "weight": 3,
                    "reason": "negative_growth_with_further_deterioration",
                }
            )

        if (
            trend.get("state") == "bearish"
            and trend.get("direction") == "deteriorating"
        ):
            evidence.append(
                {
                    "type": "toward_contraction",
                    "weight": 3,
                    "reason": "bearish_trend_with_further_deterioration",
                }
            )

        if (
            momentum.get("state") == "negative"
            and momentum.get("direction") == "deteriorating"
        ):
            evidence.append(
                {
                    "type": "toward_contraction",
                    "weight": 3,
                    "reason": "negative_momentum_with_further_deterioration",
                }
            )

        # ==========================================================
        # RECUPERACIÓN
        # ==========================================================

        if (
            growth.get("state") == "negative"
            and growth.get("direction") == "improving"
        ):
            evidence.append(
                {
                    "type": "toward_recovery",
                    "weight": 3,
                    "reason": "negative_growth_but_improving",
                }
            )

        if (
            trend.get("state") == "bearish"
            and trend.get("direction") == "improving"
        ):
            evidence.append(
                {
                    "type": "toward_recovery",
                    "weight": 3,
                    "reason": "bearish_trend_but_improving",
                }
            )

        if (
            momentum.get("state") == "negative"
            and momentum.get("direction") == "improving"
        ):
            evidence.append(
                {
                    "type": "toward_recovery",
                    "weight": 3,
                    "reason": "negative_momentum_but_improving",
                }
            )

        # ==========================================================
        # EXPANSIÓN
        # ==========================================================

        if (
            growth.get("state") == "positive"
            and growth.get("direction") == "improving"
        ):
            evidence.append(
                {
                    "type": "toward_expansion",
                    "weight": 3,
                    "reason": "positive_growth_with_improving_direction",
                }
            )

        if (
            trend.get("state") == "bullish"
            and trend.get("direction") == "improving"
        ):
            evidence.append(
                {
                    "type": "toward_expansion",
                    "weight": 3,
                    "reason": "bullish_trend_with_improving_direction",
                }
            )

        if (
            momentum.get("state") == "positive"
            and momentum.get("direction") == "improving"
        ):
            evidence.append(
                {
                    "type": "toward_expansion",
                    "weight": 3,
                    "reason": "positive_momentum_with_improving_direction",
                }
            )

        # ==========================================================
        # MEJORA ESTRUCTURAL
        # ==========================================================

        improving_components = 0

        if growth.get("direction") == "improving":
            improving_components += 1

        if trend.get("direction") == "improving":
            improving_components += 1

        if momentum.get("direction") == "improving":
            improving_components += 1

        if improving_components >= 2:
            evidence.append(
                {
                    "type": "structural_improvement",
                    "weight": improving_components,
                    "reason": "growth_trend_and_momentum_show_improvement",
                }
            )

        # ==========================================================
        # DETERIORO ESTRUCTURAL
        # ==========================================================

        deteriorating_components = 0

        if growth.get("direction") == "deteriorating":
            deteriorating_components += 1

        if trend.get("direction") == "deteriorating":
            deteriorating_components += 1

        if momentum.get("direction") == "deteriorating":
            deteriorating_components += 1

        if deteriorating_components >= 2:
            evidence.append(
                {
                    "type": "structural_deterioration",
                    "weight": deteriorating_components,
                    "reason": "growth_trend_and_momentum_show_deterioration",
                }
            )

        # ==========================================================
        # REVERSIÓN
        # ==========================================================
        #
        # Una reversión no se considera una transición económica
        # independiente. Se utiliza como evidencia adicional de que
        # existe un cambio de dirección.
        #

        if trend.get("reversal"):
            if trend.get("direction") == "improving":
                evidence.append(
                    {
                        "type": "reversal_toward_improvement",
                        "weight": 2,
                        "reason": "trend_reversal_with_improving_direction",
                    }
                )
            elif trend.get("direction") == "deteriorating":
                evidence.append(
                    {
                        "type": "reversal_toward_deterioration",
                        "weight": 2,
                        "reason": "trend_reversal_with_deteriorating_direction",
                    }
                )

        # ==========================================================
        # AGREGACIÓN
        # ==========================================================

        return TransitionDetector._aggregate_evidence(evidence)

    @staticmethod
    def _aggregate_evidence(
        evidence: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if not evidence:
            return {
                "detected": False,
                "state": "none",
                "direction": "unknown",
                "type": "none",
                "score": 0,
                "confidence": "low",
                "reasons": [],
                "evidence": [],
            }

        scores: dict[str, int] = {}

        for item in evidence:
            transition_type = item["type"]

            scores[transition_type] = (
                scores.get(transition_type, 0)
                + int(item["weight"])
            )

        dominant_type = max(
            scores,
            key=scores.get,
        )

        dominant_score = scores[dominant_type]

        total_score = sum(scores.values())

        dominant_share = (
            dominant_score / total_score
            if total_score > 0
            else 0.0
        )

        # ==========================================================
        # DIRECCIÓN
        # ==========================================================

        direction_map = {
            "toward_slowdown": "toward_slowdown",
            "toward_contraction": "toward_contraction",
            "toward_recovery": "toward_recovery",
            "toward_expansion": "toward_expansion",
            "structural_improvement": "toward_improvement",
            "structural_deterioration": "toward_deterioration",
            "reversal_toward_improvement": "toward_improvement",
            "reversal_toward_deterioration": "toward_deterioration",
        }

        direction = direction_map.get(
            dominant_type,
            "unknown",
        )

        # ==========================================================
        # INTENSIDAD
        # ==========================================================

        if dominant_score >= 6:
            state = "strong"
        elif dominant_score >= 4:
            state = "moderate"
        elif dominant_score >= 2:
            state = "early"
        else:
            state = "none"

        # ==========================================================
        # COHERENCIA
        # ==========================================================

        if dominant_share >= 0.75:
            confidence = "high"
        elif dominant_share >= 0.50:
            confidence = "medium"
        else:
            confidence = "low"

        # Si existe evidencia importante en direcciones
        # contrapuestas, la transición debe considerarse mixta.

        improvement_score = sum(
            score
            for transition_type, score in scores.items()
            if transition_type in {
                "toward_recovery",
                "toward_expansion",
                "structural_improvement",
                "reversal_toward_improvement",
            }
        )

        deterioration_score = sum(
            score
            for transition_type, score in scores.items()
            if transition_type in {
                "toward_slowdown",
                "toward_contraction",
                "structural_deterioration",
                "reversal_toward_deterioration",
            }
        )

        if (
            improvement_score > 0
            and deterioration_score > 0
        ):
            difference = abs(
                improvement_score - deterioration_score
            )

            if difference <= 1:
                direction = "mixed"
                confidence = "low"

        return {
            "detected": state != "none",
            "state": state,
            "direction": direction,
            "type": dominant_type,
            "score": dominant_score,
            "total_score": total_score,
            "dominant_share": dominant_share,
            "confidence": confidence,
            "reasons": [
                item["reason"]
                for item in evidence
                if item["type"] == dominant_type
            ],
            "evidence": evidence,
        }