from __future__ import annotations

from typing import Any


class MacroBiasAnalyzer:
    """
    Sintetiza el sesgo macroeconómico general.

    Este componente no vuelve a interpretar las dimensiones
    macroeconómicas ni calcula un score agregado.

    Consume las interpretaciones ya construidas por las capas
    anteriores:

        environment
        risk
        opportunity
        transition

    y las sintetiza en una descripción del sesgo macroeconómico.

    No:

        - calcula scores,
        - reinterpreta señales,
        - clasifica de nuevo el régimen,
        - selecciona activos,
        - genera recomendaciones BUY/SELL.
    """

    @staticmethod
    def analyze(
        *,
        environment: dict[str, Any],
        risk: dict[str, Any],
        opportunity: dict[str, Any],
        signals: dict[str, Any],
        regime: str,
        transition: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Sintetiza el sesgo macroeconómico a partir de las
        interpretaciones ya existentes.

        `signals` y `regime` permanecen en la firma por compatibilidad
        con el orquestador actual, pero no se reinterpretan aquí.
        """

        environment_state = environment.get("state", "unknown")
        environment_direction = environment.get(
            "directional_bias",
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

        reasons: list[str] = []

        # ----------------------------------------------------------
        # ENVIRONMENT
        # ----------------------------------------------------------

        if environment_state == "supportive":
            reasons.append(
                "supportive_environment"
            )

        elif environment_state == "challenging":
            reasons.append(
                "challenging_environment"
            )

        elif environment_state == "transitioning":
            reasons.append(
                "transitioning_environment"
            )

        elif environment_state == "neutral":
            reasons.append(
                "neutral_environment"
            )

        # ----------------------------------------------------------
        # RISK
        # ----------------------------------------------------------

        if risk_state == "high":
            reasons.append(
                "high_macro_risk"
            )

        elif risk_state == "elevated":
            reasons.append(
                "elevated_macro_risk"
            )

        elif risk_state == "extreme":
            reasons.append(
                "extreme_macro_risk"
            )

        elif risk_state == "moderate":
            reasons.append(
                "moderate_macro_risk"
            )

        # ----------------------------------------------------------
        # OPPORTUNITY
        # ----------------------------------------------------------

        if opportunity_state == "established":
            reasons.append(
                "established_macro_opportunity"
            )

        elif opportunity_state == "emerging":
            reasons.append(
                "emerging_macro_opportunity"
            )

        elif opportunity_state == "supportive":
            reasons.append(
                "supportive_macro_conditions"
            )

        elif opportunity_state == "limited":
            reasons.append(
                "limited_macro_opportunity"
            )

        # ----------------------------------------------------------
        # TRANSITION
        # ----------------------------------------------------------

        if transition_detected:
            reasons.append(
                "macro_transition"
            )

            if transition_direction in {
                "toward_slowdown",
                "toward_contraction",
                "toward_deterioration",
            }:
                reasons.append(
                    "macro_deterioration_transition"
                )

            elif transition_direction in {
                "toward_recovery",
                "toward_expansion",
                "toward_improvement",
            }:
                reasons.append(
                    "macro_improvement_transition"
                )

            if transition_state == "strong":
                reasons.append(
                    "strong_macro_transition"
                )

        # ----------------------------------------------------------
        # SYNTHESIS
        # ----------------------------------------------------------

        if environment_state == "challenging":
            if risk_state in {
                "high",
                "extreme",
            }:
                state = "defensive"

            elif (
                transition_direction
                in {
                    "toward_slowdown",
                    "toward_contraction",
                    "toward_deterioration",
                }
                and transition_state
                in {
                    "moderate",
                    "strong",
                }
            ):
                state = "defensive"

            else:
                state = "cautious"

        elif environment_state == "supportive":
            if (
                transition_direction
                in {
                    "toward_slowdown",
                    "toward_contraction",
                    "toward_deterioration",
                }
                and transition_state
                in {
                    "moderate",
                    "strong",
                }
            ):
                state = "cautious"

            else:
                state = "supportive"

        elif environment_state == "transitioning":
            if transition_direction in {
                "toward_recovery",
                "toward_expansion",
                "toward_improvement",
            }:
                state = "improving"

            elif transition_direction in {
                "toward_slowdown",
                "toward_contraction",
                "toward_deterioration",
            }:
                state = "deteriorating"

            else:
                state = "transitioning"

        else:
            if opportunity_state in {
                "established",
                "emerging",
            } and risk_state not in {
                "high",
                "extreme",
            }:
                state = "constructive"

            elif risk_state in {
                "high",
                "extreme",
            }:
                state = "cautious"

            else:
                state = "neutral"

        # ----------------------------------------------------------
        # DIRECTION
        # ----------------------------------------------------------

        if transition_direction in {
            "toward_recovery",
            "toward_expansion",
            "toward_improvement",
        }:
            direction = "improving"

        elif transition_direction in {
            "toward_slowdown",
            "toward_contraction",
            "toward_deterioration",
        }:
            direction = "deteriorating"

        elif environment_direction in {
            "improving",
            "deteriorating",
            "stable",
        }:
            direction = environment_direction

        else:
            direction = "unknown"

        # ----------------------------------------------------------
        # STRENGTH
        # ----------------------------------------------------------

        if transition_state == "strong":
            strength = "strong"
        elif transition_state == "moderate":
            strength = "moderate"
        elif transition_state == "early":
            strength = "weak"
        elif transition_detected:
            strength = "weak"
        else:
            strength = "unknown"

        # ----------------------------------------------------------
        # COHERENCE
        # ----------------------------------------------------------

        coherence = environment_coherence

        if coherence not in {
            "high",
            "medium",
            "low",
        }:
            coherence = "unknown"

        return {
            "state": state,
            "direction": direction,
            "strength": strength,
            "coherence": coherence,
            "reasons": list(
                dict.fromkeys(reasons)
            ),
        }