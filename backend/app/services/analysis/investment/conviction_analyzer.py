from __future__ import annotations

from typing import Any


class ConvictionAnalyzer:
    """
    Sintetiza la solidez de la interpretación macroeconómica.

    La convicción describe hasta qué punto las distintas dimensiones
    de la interpretación forman una lectura macro consistente.

    No representa:

        - probabilidad de rentabilidad,
        - probabilidad de éxito de una inversión,
        - calidad de un activo,
        - recomendación de inversión,
        - intensidad del riesgo.

    La convicción debe distinguirse de confidence:

        confidence
            → claridad y coherencia de la interpretación económica.

        conviction
            → consistencia de la síntesis macroeconómica final.
    """

    @staticmethod
    def analyze(
        *,
        environment: dict[str, Any],
        risk: dict[str, Any],
        opportunity: dict[str, Any],
        confidence: dict[str, Any],
        transition: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Sintetiza la consistencia de la interpretación macroeconómica.

        No utiliza scores procedentes de otras capas y no crea un
        nuevo sistema de puntuación.
        """

        reasons: list[str] = []
        contradictions: list[str] = []

        confidence_state = confidence.get(
            "state",
            "very_low",
        )

        coherence = confidence.get(
            "coherence",
            "low",
        )

        environment_state = environment.get(
            "state",
            "unknown",
        )

        environment_coherence = environment.get(
            "coherence",
            "unknown",
        )

        risk_state = risk.get(
            "state",
            "unknown",
        )

        opportunity_state = opportunity.get(
            "state",
            "unknown",
        )

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

        # ----------------------------------------------------------
        # CONFIDENCE / COHERENCE
        # ----------------------------------------------------------

        if confidence_state == "high":
            reasons.append(
                "high_interpretation_clarity"
            )

        elif confidence_state == "moderate":
            reasons.append(
                "moderate_interpretation_clarity"
            )

        elif confidence_state in {
            "low",
            "very_low",
        }:
            reasons.append(
                "limited_interpretation_clarity"
            )

        if coherence == "high":
            reasons.append(
                "high_cross_dimension_coherence"
            )

        elif coherence == "medium":
            reasons.append(
                "moderate_cross_dimension_coherence"
            )

        elif coherence == "low":
            contradictions.append(
                "low_cross_dimension_coherence"
            )

        # ----------------------------------------------------------
        # ENVIRONMENT
        # ----------------------------------------------------------

        if environment_coherence == "high":
            reasons.append(
                "coherent_environment"
            )

        elif environment_coherence == "low":
            contradictions.append(
                "environment_uncertainty"
            )

        # ----------------------------------------------------------
        # ENVIRONMENT / RISK / OPPORTUNITY ALIGNMENT
        # ----------------------------------------------------------

        if (
            environment_state == "supportive"
            and risk_state in {
                "low",
                "moderate",
                "unknown",
            }
            and opportunity_state in {
                "established",
                "emerging",
                "supportive",
                "uncertain",
                "limited",
            }
        ):
            reasons.append(
                "environment_risk_alignment"
            )

        if (
            environment_state == "challenging"
            and risk_state in {
                "high",
                "extreme",
            }
        ):
            reasons.append(
                "environment_risk_alignment"
            )

        if (
            environment_state == "supportive"
            and risk_state == "extreme"
        ):
            contradictions.append(
                "supportive_environment_with_extreme_risk"
            )

        if (
            environment_state == "challenging"
            and opportunity_state in {
                "established",
                "supportive",
            }
        ):
            contradictions.append(
                "challenging_environment_with_supportive_opportunity"
            )

        # ----------------------------------------------------------
        # TRANSITION
        # ----------------------------------------------------------

        if transition_detected:
            if transition_state == "strong":
                reasons.append(
                    "clear_transition_evidence"
                )

            elif transition_state == "moderate":
                reasons.append(
                    "moderate_transition_evidence"
                )

            elif transition_state == "early":
                reasons.append(
                    "early_transition_evidence"
                )

            if transition_direction == "unknown":
                contradictions.append(
                    "transition_direction_unclear"
                )

            elif transition_direction == "mixed":
                contradictions.append(
                    "mixed_transition_direction"
                )

        # ----------------------------------------------------------
        # STATE
        # ----------------------------------------------------------

        if contradictions:
            state = "low"

        elif confidence_state == "very_low":
            state = "very_low"

        elif (
            confidence_state == "high"
            and coherence == "high"
            and environment_coherence
            in {
                "high",
                "medium",
            }
        ):
            state = "high"

        elif (
            confidence_state
            in {
                "high",
                "moderate",
            }
            and coherence
            in {
                "high",
                "medium",
            }
        ):
            state = "moderate"

        elif confidence_state == "low":
            state = "low"

        else:
            state = "very_low"

        # ----------------------------------------------------------
        # REASONS FOR CLEAR RISK / OPPORTUNITY SEPARATION
        # ----------------------------------------------------------

        if risk_state in {
            "high",
            "extreme",
        }:
            reasons.append(
                "high_risk_does_not_reduce_interpretation_clarity"
            )

        if opportunity_state in {
            "established",
            "emerging",
        }:
            reasons.append(
                "macro_opportunity_evidence_present"
            )

        return {
            "state": state,
            "coherence": coherence,
            "reasons": list(
                dict.fromkeys(reasons)
            ),
            "contradictions": list(
                dict.fromkeys(contradictions)
            ),
        }