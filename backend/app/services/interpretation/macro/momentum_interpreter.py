from __future__ import annotations

from typing import Any

import pandas as pd

from ..utils import safe_bool, safe_float, serialize


class MomentumInterpreter:
    """
    Interpreta el estado y la evolución del momentum.

    Separa:

        state:
            situación actual del momentum.

        direction:
            evolución del momentum.

        acceleration:
            aceleración asociada al momentum.

    No mezcla el nivel actual con su evolución.

    Ejemplos:

        momentum < 0 + improving
            → momentum negativo pero mejorando.

        momentum > 0 + deteriorating
            → momentum positivo pero perdiendo fuerza.
    """

    ACCELERATION_EPSILON = 0.0

    @classmethod
    def interpret(
        cls,
        features: pd.Series,
        signals: pd.Series,
    ) -> dict[str, Any]:

        momentum = safe_float(
            features.get("momentum")
        )

        acceleration = safe_float(
            features.get("acceleration")
        )

        positive = safe_bool(
            signals.get("positive_momentum", False)
        )

        negative = safe_bool(
            signals.get("negative_momentum", False)
        )

        improving = safe_bool(
            signals.get("momentum_improving", False)
        )

        weakening = safe_bool(
            signals.get("momentum_weakening", False)
        )

        # ---------------------------------------------------------
        # 1. CURRENT STATE
        # ---------------------------------------------------------

        if momentum is None:
            state = "unknown"

        elif positive:
            state = "positive"

        elif negative:
            state = "negative"

        elif momentum > 0:
            state = "positive"

        elif momentum < 0:
            state = "negative"

        else:
            state = "neutral"

        # ---------------------------------------------------------
        # 2. DIRECTION
        # ---------------------------------------------------------
        #
        # Direction describes the evolution of momentum.
        #
        # It is deliberately independent from the current state.
        #
        # Therefore:
        #
        #   negative + improving
        #
        # is valid.
        #
        # And:
        #
        #   positive + deteriorating
        #
        # is also valid.

        if improving and not weakening:
            direction = "improving"

        elif weakening and not improving:
            direction = "deteriorating"

        elif acceleration is None:
            direction = "unknown"

        elif acceleration > cls.ACCELERATION_EPSILON:
            direction = "improving"

        elif acceleration < -cls.ACCELERATION_EPSILON:
            direction = "deteriorating"

        else:
            direction = "stable"

        # ---------------------------------------------------------
        # 3. ACCELERATION STATE
        # ---------------------------------------------------------

        if acceleration is None:
            acceleration_state = "unknown"

        elif acceleration > cls.ACCELERATION_EPSILON:
            acceleration_state = "positive"

        elif acceleration < -cls.ACCELERATION_EPSILON:
            acceleration_state = "negative"

        else:
            acceleration_state = "stable"

        # ---------------------------------------------------------
        # 4. RETURN
        # ---------------------------------------------------------

        return {
            # Canonical semantic fields
            "state": state,
            "direction": direction,
            "acceleration": acceleration_state,

            # Raw values
            "value": serialize(
                features.get("momentum")
            ),
            "acceleration_value": serialize(
                features.get("acceleration")
            ),

            # Compatibility fields
            "positive": positive,
            "negative": negative,
            "improving": improving,
            "weakening": weakening,
        }