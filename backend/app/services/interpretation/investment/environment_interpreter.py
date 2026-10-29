from __future__ import annotations

from typing import Any


class EnvironmentInterpreter:
    """
    Sintetiza el entorno macroeconómico para la capa de inversión.

    Este componente NO vuelve a interpretar growth, trend, momentum,
    volatility o position.

    Utiliza la semántica producida por EconomicInterpretationService
    para describir:

        - el régimen económico actual,
        - la dirección agregada,
        - la transición,
        - la coherencia entre dimensiones.

    Volatilidad y posición se conservan como contexto descriptivo,
    pero no se convierten automáticamente en factores favorables
    o desfavorables.

    No calcula puntuaciones de inversión, oportunidades, riesgos,
    valoración ni señales de compra/venta.
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
        """
        Construye una síntesis del entorno macroeconómico.

        La interpretación económica ya ha sido realizada por
        EconomicInterpretationService. Aquí solamente se organiza
        esa información para que la capa de inversión pueda
        consumirla sin volver a clasificar los componentes.
        """

        directional_bias = cls._get_directional_bias(
            growth=growth,
            trend=trend,
            momentum=momentum,
        )

        coherence = cls._get_coherence(
            growth=growth,
            trend=trend,
            momentum=momentum,
        )

        transition_detected = bool(
            transition.get("detected", False)
        )

        transition_direction = (
            transition.get("direction")
            or "unknown"
        )

        transition_state = (
            transition.get("state")
            or "none"
        )

        environment_state = cls._classify_environment(
            regime=regime,
            directional_bias=directional_bias,
            transition_direction=transition_direction,
            transition_state=transition_state,
        )

        return {
            "state": environment_state,
            "regime": regime,
            "directional_bias": directional_bias,
            "coherence": coherence,
            "transition": {
                "detected": transition_detected,
                "direction": transition_direction,
                "state": transition_state,
                "confidence": (
                    transition.get("confidence")
                    or "low"
                ),
            },
            "context": {
                "volatility": {
                    "level": volatility.get(
                        "level",
                        "unknown",
                    ),
                    "direction": volatility.get(
                        "direction",
                        "unknown",
                    ),
                    "stress": volatility.get(
                        "stress",
                        "unknown",
                    ),
                    "shock": bool(
                        volatility.get(
                            "shock",
                            False,
                        )
                    ),
                },
                "position": {
                    "position": position.get(
                        "position",
                        "unknown",
                    ),
                    "direction": position.get(
                        "direction",
                        "unknown",
                    ),
                    "drawdown_state": position.get(
                        "drawdown_state",
                        "unknown",
                    ),
                    "extreme": position.get(
                        "extreme",
                        "none",
                    ),
                },
            },
        }

    @staticmethod
    def _get_directional_bias(
        *,
        growth: dict[str, Any],
        trend: dict[str, Any],
        momentum: dict[str, Any],
    ) -> str:
        """
        Determina la dirección agregada a partir de las tres
        dimensiones dinámicas principales.

        No utiliza puntuaciones.
        """

        directions = [
            growth.get("direction"),
            trend.get("direction"),
            momentum.get("direction"),
        ]

        improving = directions.count("improving")
        deteriorating = directions.count("deteriorating")
        stable = directions.count("stable")

        known = [
            direction
            for direction in directions
            if direction not in {
                None,
                "unknown",
            }
        ]

        if not known:
            return "unknown"

        if (
            improving >= 2
            and improving > deteriorating
        ):
            return "improving"

        if (
            deteriorating >= 2
            and deteriorating > improving
        ):
            return "deteriorating"

        if (
            stable >= 2
            and stable > improving
            and stable > deteriorating
        ):
            return "stable"

        if improving > 0 and deteriorating > 0:
            return "mixed"

        if improving > 0:
            return "improving"

        if deteriorating > 0:
            return "deteriorating"

        if stable > 0:
            return "stable"

        return "unknown"

    @staticmethod
    def _get_coherence(
        *,
        growth: dict[str, Any],
        trend: dict[str, Any],
        momentum: dict[str, Any],
    ) -> str:
        """
        Describe el grado de acuerdo entre growth, trend y momentum.

        No mide confianza estadística.
        """

        directions = [
            growth.get("direction"),
            trend.get("direction"),
            momentum.get("direction"),
        ]

        known = [
            direction
            for direction in directions
            if direction not in {
                None,
                "unknown",
            }
        ]

        if not known:
            return "unknown"

        unique_directions = set(known)

        if len(unique_directions) == 1:
            return "high"

        if (
            "improving" in unique_directions
            and "deteriorating" in unique_directions
        ):
            return "low"

        return "medium"

    @staticmethod
    def _classify_environment(
        *,
        regime: str,
        directional_bias: str,
        transition_direction: str,
        transition_state: str,
    ) -> str:
        """
        Clasifica el entorno utilizando el régimen actual como
        referencia principal y la dirección/transición como contexto.

        No utiliza volatilidad ni posición para decidir si el entorno
        es favorable o desfavorable.
        """

        if regime in {
            "contraction",
            "slowdown",
        }:
            return "challenging"

        if regime in {
            "expansion",
            "recovery",
        }:
            if (
                directional_bias == "deteriorating"
                and transition_state in {
                    "moderate",
                    "strong",
                }
            ):
                return "transitioning"

            return "supportive"

        if regime == "late_expansion":
            if (
                transition_direction == "toward_slowdown"
                and transition_state in {
                    "moderate",
                    "strong",
                }
            ):
                return "transitioning"

            return "supportive"

        if regime == "stagnation":
            return "neutral"

        return "neutral"