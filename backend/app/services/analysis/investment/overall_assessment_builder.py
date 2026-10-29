from __future__ import annotations

from typing import Any


class OverallAssessmentBuilder:
    """
    Construye la evaluación global final de la interpretación
    macroeconómica.

    Este componente únicamente ensambla las interpretaciones
    previamente calculadas.

    No:

        - calcula scores,
        - vuelve a interpretar riesgo,
        - vuelve a interpretar transición,
        - vuelve a clasificar el régimen,
        - genera recomendaciones de inversión.

    Las reglas de interpretación pertenecen a las capas anteriores.
    """

    @staticmethod
    def build(
        *,
        environment: dict[str, Any],
        risk: dict[str, Any],
        opportunity: dict[str, Any],
        confidence: dict[str, Any],
        macro_bias: dict[str, Any],
        conviction: dict[str, Any],
        transition: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ensambla las principales dimensiones de la interpretación
        de inversión en una estructura global.

        La evaluación global es descriptiva y no constituye una
        recomendación de inversión.
        """

        return {
            # "assessment" se mantiene como alias retrocompatible de "macro_bias"
            # para clientes y endpoints existentes.
            "assessment": macro_bias.get(
                "state",
                "unknown",
            ),
            "direction": macro_bias.get(
                "direction",
                "unknown",
            ),
            "strength": macro_bias.get(
                "strength",
                "unknown",
            ),
            "coherence": macro_bias.get(
                "coherence",
                "unknown",
            ),
            "macro_bias": macro_bias.get(
                "state",
                "unknown",
            ),
            "conviction": conviction.get(
                "state",
                "unknown",
            ),
            "confidence": confidence.get(
                "state",
                "unknown",
            ),
            "environment": environment.get(
                "state",
                "unknown",
            ),
            "risk": risk.get(
                "state",
                "unknown",
            ),
            "opportunity": opportunity.get(
                "state",
                "unknown",
            ),
            "transition": {
                "detected": bool(
                    transition.get(
                        "detected",
                        False,
                    )
                ),
                "direction": transition.get(
                    "direction",
                    "unknown",
                ),
                "state": transition.get(
                    "state",
                    "none",
                ),
            },
            "reasons": list(
                dict.fromkeys(
                    macro_bias.get(
                        "reasons",
                        [],
                    )
                )
            ),
        }