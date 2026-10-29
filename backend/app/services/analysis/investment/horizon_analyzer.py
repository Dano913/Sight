from __future__ import annotations

from typing import Any


class HorizonAnalyzer:
    """
    Evalúa el contexto macroeconómico por horizonte temporal.

    No representa:

        - rentabilidad esperada,
        - valoración de activos,
        - probabilidad de subida o bajada,
        - recomendación de inversión.

    Cada horizonte resume las dinámicas macroeconómicas más
    relevantes para ese plazo.

    Horizonte corto:
        transición, momentum y volatilidad.

    Horizonte medio:
        crecimiento, tendencia y transición.

    Horizonte largo:
        régimen, tendencia y coherencia del entorno.
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
    ) -> dict[str, str]:
        """
        Construye una descripción macroeconómica por horizonte.

        Los argumentos signals y opportunity se mantienen por
        compatibilidad con el orquestador actual, pero la clasificación
        se basa en las interpretaciones semánticas canónicas.
        """

        return {
            "short_term": HorizonAnalyzer._analyze_short_term(
                risk=risk,
                transition=transition,
                volatility=environment.get(
                    "context",
                    {},
                ).get(
                    "volatility",
                    {},
                ),
            ),
            "medium_term": HorizonAnalyzer._analyze_medium_term(
                environment=environment,
                transition=transition,
            ),
            "long_term": HorizonAnalyzer._analyze_long_term(
                environment=environment,
                regime=regime,
            ),
        }

    @staticmethod
    def _analyze_short_term(
        *,
        risk: dict[str, Any],
        transition: dict[str, Any],
        volatility: dict[str, Any],
    ) -> str:
        """
        Resume las dinámicas macroeconómicas de corto plazo.

        Se priorizan:

            - transición,
            - volatilidad,
            - riesgo macro inmediato.
        """

        transition_direction = transition.get(
            "direction",
            "unknown",
        )

        transition_state = transition.get(
            "state",
            "none",
        )

        volatility_level = volatility.get(
            "level",
            "unknown",
        )

        volatility_direction = volatility.get(
            "direction",
            "unknown",
        )

        volatility_stress = volatility.get(
            "stress",
            "unknown",
        )

        risk_state = risk.get(
            "state",
            "unknown",
        )

        if transition_direction in {
            "toward_contraction",
            "toward_slowdown",
            "toward_deterioration",
        } and transition_state in {
            "moderate",
            "strong",
        }:
            return "deteriorating"

        if transition_direction in {
            "toward_recovery",
            "toward_expansion",
            "toward_improvement",
        } and transition_state in {
            "moderate",
            "strong",
        }:
            return "improving"

        if (
            volatility_stress in {
                "elevated",
                "extreme",
            }
            or volatility_level == "extreme"
            or volatility_direction == "rising"
        ):
            return "volatile"

        if risk_state in {
            "high",
            "extreme",
        }:
            return "fragile"

        if transition_state == "early":
            return "transitioning"

        return "stable"

    @staticmethod
    def _analyze_medium_term(
        *,
        environment: dict[str, Any],
        transition: dict[str, Any],
    ) -> str:
        """
        Resume la dinámica macroeconómica de medio plazo.

        El medio plazo da mayor peso a la dirección de la transición
        y al comportamiento persistente del entorno.
        """

        environment_state = environment.get(
            "state",
            "unknown",
        )

        environment_direction = environment.get(
            "directional_bias",
            "unknown",
        )

        transition_direction = transition.get(
            "direction",
            "unknown",
        )

        transition_state = transition.get(
            "state",
            "none",
        )

        if transition_direction in {
            "toward_contraction",
            "toward_slowdown",
            "toward_deterioration",
        } and transition_state in {
            "moderate",
            "strong",
        }:
            return "deteriorating"

        if transition_direction in {
            "toward_recovery",
            "toward_expansion",
            "toward_improvement",
        } and transition_state in {
            "moderate",
            "strong",
        }:
            return "improving"

        if environment_state == "challenging":
            return "weak"

        if environment_state == "supportive":
            return "supportive"

        if environment_state == "transitioning":
            return "transitioning"

        if environment_direction in {
            "improving",
            "deteriorating",
        }:
            return environment_direction

        return "stable"

    @staticmethod
    def _analyze_long_term(
        *,
        environment: dict[str, Any],
        regime: str,
    ) -> str:
        """
        Resume el contexto estructural observable actualmente.

        No intenta predecir el régimen futuro. Describe el régimen
        actual y su orientación general.
        """

        environment_state = environment.get(
            "state",
            "unknown",
        )

        coherence = environment.get(
            "coherence",
            "unknown",
        )

        if regime == "contraction":
            return "contracting"

        if regime == "slowdown":
            return "slowing"

        if regime == "stagnation":
            return "stagnant"

        if regime == "recovery":
            return "recovering"

        if regime == "expansion":
            return "expanding"

        if regime == "late_expansion":
            return "maturing"

        if environment_state == "challenging":
            return "weak"

        if environment_state == "supportive":
            return "supportive"

        if coherence == "low":
            return "uncertain"

        return "stable"