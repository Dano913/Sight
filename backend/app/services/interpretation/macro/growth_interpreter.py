from __future__ import annotations

from typing import Any

import pandas as pd

from ..utils import safe_bool, safe_float, serialize


class GrowthInterpreter:
    """
    Interpreta el crecimiento o la variación de una serie.

    LOG:
        percentage_change representa la variación porcentual.

    RATE:
        change representa la variación absoluta de la tasa.
        No debe interpretarse como crecimiento porcentual.
    """

    GROWTH_FLAT_THRESHOLD = 0.001
    ACCELERATION_FLAT_THRESHOLD = 0.0

    @classmethod
    def interpret(
        cls,
        features: pd.Series,
        signals: pd.Series,
    ) -> dict[str, Any]:

        is_rate = (
            "percentage_change" not in features.index
            and "change" in features.index
        )

        if is_rate:
            variation = safe_float(features.get("change"))
        else:
            variation = safe_float(
                features.get("percentage_change")
            )

        acceleration = safe_float(features.get("acceleration"))

        positive = safe_bool(signals.get("positive_growth", False))
        negative = safe_bool(signals.get("negative_growth", False))
        accelerating = safe_bool(signals.get("accelerating_growth", False))
        decelerating = safe_bool(signals.get("decelerating_growth", False))
        reversal = safe_bool(signals.get("growth_reversal", False))

        # Estado basado en las señales, conservando la prioridad negativa.
        if negative:
            state = "negative"
        elif positive:
            state = "positive"
        else:
            state = "flat"

        # Dirección de la dinámica.
        if acceleration is None:
            direction = "unknown"
        elif acceleration > cls.ACCELERATION_FLAT_THRESHOLD:
            direction = "improving"
        elif acceleration < -cls.ACCELERATION_FLAT_THRESHOLD:
            direction = "deteriorating"
        else:
            direction = "stable"

        if acceleration is None:
            acceleration_state = "unknown"
        elif acceleration > cls.ACCELERATION_FLAT_THRESHOLD:
            acceleration_state = "positive"
        elif acceleration < -cls.ACCELERATION_FLAT_THRESHOLD:
            acceleration_state = "negative"
        else:
            acceleration_state = "stable"

        if accelerating:
            dynamic_state = "accelerating"
        elif decelerating:
            dynamic_state = "decelerating"
        else:
            dynamic_state = "stable"

        if is_rate:
            growth_rate_state = "not_applicable"
        elif variation is None:
            growth_rate_state = "unknown"
        elif variation > cls.GROWTH_FLAT_THRESHOLD:
            growth_rate_state = "positive"
        elif variation < -cls.GROWTH_FLAT_THRESHOLD:
            growth_rate_state = "negative"
        else:
            growth_rate_state = "flat"

        return {
            "state": state,
            "direction": direction,
            "acceleration": acceleration_state,
            "reversal": reversal,
            "percentage_change": (
                None if is_rate
                else serialize(features.get("percentage_change"))
            ),
            "growth_rate_state": growth_rate_state,
            "acceleration_value": serialize(
                features.get("acceleration")
            ),
            "dynamic_state": dynamic_state,
        }