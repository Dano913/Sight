from __future__ import annotations

from typing import Any


class AlertAnalyzer:
    """
    Genera alertas a partir de eventos o condiciones macroeconómicas
    ya identificadas por las capas anteriores.

    Este componente NO:

        - calcula scores,
        - recalcula el riesgo,
        - reinterpreta la transición,
        - convierte una posición histórica en una alerta por sí misma,
        - genera recomendaciones de inversión.

    Una alerta representa una condición concreta que merece atención.
    """

    @staticmethod
    def analyze(
        *,
        signals: dict[str, Any],
        transition: dict[str, Any],
    ) -> list[str]:
        """
        Genera una lista de eventos macroeconómicos relevantes.

        `signals` se mantiene en la interfaz por compatibilidad, pero
        las alertas se obtienen preferentemente de las estructuras
        semánticas canónicas de riesgo y transición.
        """

        alerts: list[str] = []

        # ----------------------------------------------------------
        # TRANSITION
        # ----------------------------------------------------------

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

        if transition_detected:
            if transition_direction == "toward_slowdown":
                alerts.append(
                    "transition_toward_slowdown"
                )

            elif transition_direction == "toward_contraction":
                alerts.append(
                    "transition_toward_contraction"
                )

            elif transition_direction == "toward_recovery":
                alerts.append(
                    "transition_toward_recovery"
                )

            elif transition_direction == "toward_expansion":
                alerts.append(
                    "transition_toward_expansion"
                )

            elif transition_direction == "toward_improvement":
                alerts.append(
                    "transition_toward_improvement"
                )

            elif transition_direction == "toward_deterioration":
                alerts.append(
                    "transition_toward_deterioration"
                )

        # ----------------------------------------------------------
        # TRANSITION INTENSITY
        # ----------------------------------------------------------

        if transition_state == "strong":
            alerts.append(
                "strong_macro_transition"
            )

        elif transition_state == "moderate":
            alerts.append(
                "moderate_macro_transition"
            )

        # ----------------------------------------------------------
        # COMBINED TRANSITION CONDITIONS
        # ----------------------------------------------------------

        if (
            transition_detected
            and transition_direction
            in {
                "toward_slowdown",
                "toward_contraction",
            }
            and transition_state
            in {
                "moderate",
                "strong",
            }
        ):
            alerts.append(
                "macro_deterioration_transition"
            )

        if (
            transition_detected
            and transition_direction
            in {
                "toward_recovery",
                "toward_expansion",
            }
            and transition_state
            in {
                "moderate",
                "strong",
            }
        ):
            alerts.append(
                "macro_improvement_transition"
            )

        # ----------------------------------------------------------
        # SIGNAL EVENTS
        # ----------------------------------------------------------
        #
        # Estos eventos proceden de estructuras semánticas ya
        # generadas por SignalGenerator.
        #
        # No se utilizan nombres antiguos como:
        #
        #   trend_reversal
        #   trend_weakening
        #   volatility_risk
        #   near_historical_high
        #
        # porque esos conceptos ya tienen representación propia
        # en trend / volatility / position.
        #

        trend = signals.get(
            "trend",
            {},
        )

        volatility = signals.get(
            "volatility",
            {},
        )

        position = signals.get(
            "position",
            {},
        )

        if trend.get("reversal"):
            alerts.append(
                "trend_reversal"
            )

        if volatility.get("shock"):
            alerts.append(
                "volatility_shock"
            )

        if position.get("severe_drawdown"):
            alerts.append(
                "severe_drawdown"
            )

        return list(
            dict.fromkeys(alerts)
        )