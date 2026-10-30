from __future__ import annotations

from typing import Any

import pandas as pd

from ..utils import safe_bool, safe_float, serialize


class TrendInterpreter:
    """
    Interpreta la estructura temporal de la tendencia.

    Separa:

        state:
            estructura actual de la tendencia.

        direction:
            evolución reciente de la tendencia.

        strength:
            intensidad de la tendencia.

        reversal:
            indica si se ha detectado una reversión.

    La estructura se obtiene comparando las pendientes de:

        - corto plazo
        - medio plazo
        - largo plazo

    Importante:
        `bullish` o `bearish` describen el estado actual.

        `improving` o `deteriorating` describen su evolución.

        No deben mezclarse ambos conceptos.
    """

    TREND_EPSILON = 1e-12
    TREND_CHANGE_THRESHOLD = 0.30

    @classmethod
    def interpret(
        cls,
        features: pd.Series,
        signals: pd.Series,
    ) -> dict[str, Any]:

        short_slope = safe_float(
            features.get("rolling_slope_short")
        )

        medium_slope = safe_float(
            features.get("rolling_slope_medium")
        )

        long_slope = safe_float(
            features.get("rolling_slope_long")
        )

        acceleration = safe_float(
            features.get("acceleration")
        )

        slope_change = safe_float(
            features.get("slope_change")
        )

        trend_change = safe_float(
            features.get("trend_change")
        )

        bullish = safe_bool(
            signals.get("bullish_trend", False)
        )

        bearish = safe_bool(
            signals.get("bearish_trend", False)
        )

        mixed = safe_bool(
            signals.get("mixed_trend", False)
        )

        reversal = safe_bool(
            signals.get("trend_reversal", False)
        )

        strengthening = safe_bool(
            signals.get("trend_strengthening", False)
        )

        weakening = safe_bool(
            signals.get("trend_weakening", False)
        )

        # ---------------------------------------------------------
        # 1. INDIVIDUAL SLOPE DIRECTIONS
        # ---------------------------------------------------------

        short_direction = cls._slope_direction(
            short_slope
        )

        medium_direction = cls._slope_direction(
            medium_slope
        )

        long_direction = cls._slope_direction(
            long_slope
        )

        # ---------------------------------------------------------
        # 2. CURRENT TREND STATE
        # ---------------------------------------------------------
        #
        # State describes the current structure.
        #
        # We deliberately do NOT encode changes such as:
        #
        #     bullish_weakening
        #     bearish_improving
        #     recovery
        #
        # Those belong to `direction`.

        if (
            short_slope is not None
            and medium_slope is not None
            and long_slope is not None
        ):

            if (
                short_slope > cls.TREND_EPSILON
                and medium_slope > cls.TREND_EPSILON
                and long_slope > cls.TREND_EPSILON
            ):
                state = "bullish"

            elif (
                short_slope < -cls.TREND_EPSILON
                and medium_slope < -cls.TREND_EPSILON
                and long_slope < -cls.TREND_EPSILON
            ):
                state = "bearish"

            elif (
                abs(short_slope) <= cls.TREND_EPSILON
                and abs(medium_slope) <= cls.TREND_EPSILON
                and abs(long_slope) <= cls.TREND_EPSILON
            ):
                state = "neutral"

            else:
                state = "mixed"

        elif bullish:
            state = "bullish"

        elif bearish:
            state = "bearish"

        elif mixed:
            state = "mixed"

        else:
            state = "unknown"

        # ---------------------------------------------------------
        # 3. TREND DIRECTION
        # ---------------------------------------------------------
        #
        # Direction describes whether the trend structure is
        # improving or deteriorating.
        #
        # Strengthening / weakening signals are preferred because
        # they represent the intended interpretation of trend
        # dynamics.
        #
        # If neither signal is available, trend_change is used.

        if strengthening and not weakening:
            direction = "improving"

        elif weakening and not strengthening:
            direction = "deteriorating"

        elif trend_change is None:
            direction = "unknown"

        elif trend_change > cls.TREND_CHANGE_THRESHOLD:
            direction = "improving"

        elif trend_change < -cls.TREND_CHANGE_THRESHOLD:
            direction = "deteriorating"

        else:
            direction = "stable"

        # ---------------------------------------------------------
        # 4. CHANGE STATE
        # ---------------------------------------------------------
        #
        # Compatibility field.
        #
        # `direction` is now the canonical semantic field.
        # This field can eventually be removed once downstream
        # consumers migrate.

        if weakening and not strengthening:
            change_state = "weakening"

        elif strengthening and not weakening:
            change_state = "strengthening"

        elif trend_change is None:
            change_state = "unknown"

        elif trend_change > cls.TREND_CHANGE_THRESHOLD:
            change_state = "strengthening"

        elif trend_change < -cls.TREND_CHANGE_THRESHOLD:
            change_state = "weakening"

        else:
            change_state = "stable"

        # ---------------------------------------------------------
        # 5. TREND STRENGTH
        # ---------------------------------------------------------

        slopes = [
            value
            for value in (
                short_slope,
                medium_slope,
                long_slope,
            )
            if value is not None
        ]

        if not slopes:
            strength = "unknown"

        else:
            average_abs_slope = sum(
                abs(value)
                for value in slopes
            ) / len(slopes)

            if average_abs_slope <= cls.TREND_EPSILON:
                strength = "weak"

            elif (
                trend_change is not None
                and abs(trend_change) > 1
            ):
                strength = "strong"

            else:
                strength = "moderate"

        # ---------------------------------------------------------
        # 6. RETURN
        # ---------------------------------------------------------

        return {
            # Canonical semantic fields
            "state": state,
            "direction": direction,
            "strength": strength,
            "reversal": reversal,

            # Compatibility field
            "change_state": change_state,

            # Multi-horizon evidence
            "short_direction": short_direction,
            "medium_direction": medium_direction,
            "long_direction": long_direction,

            # Raw signal information
            "bullish": bullish,
            "bearish": bearish,
            "mixed": mixed,
            "strengthening": strengthening,
            "weakening": weakening,

            # Raw metrics
            "short_slope": serialize(
                features.get("rolling_slope_short")
            ),
            "medium_slope": serialize(
                features.get("rolling_slope_medium")
            ),
            "long_slope": serialize(
                features.get("rolling_slope_long")
            ),
            "acceleration": serialize(
                features.get("acceleration")
            ),
            "slope_change": serialize(
                features.get("slope_change")
            ),
            "trend_change": serialize(
                features.get("trend_change")
            ),
        }

    @staticmethod
    def _slope_direction(
        slope: float | None,
    ) -> str:

        if slope is None:
            return "unknown"

        if slope > 0:
            return "up"

        if slope < 0:
            return "down"

        return "flat"