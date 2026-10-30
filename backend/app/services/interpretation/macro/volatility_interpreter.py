from __future__ import annotations

from typing import Any

import pandas as pd

from ..utils import safe_bool, safe_float, serialize


class VolatilityInterpreter:
    """
    Interpreta la volatilidad separando:

        level:
            nivel actual de volatilidad.

        direction:
            evolución de la volatilidad.

        stress:
            grado de desviación respecto a su comportamiento habitual.

        shock:
            evento de volatilidad excepcional.

    No mezcla estas dimensiones en un único estado compuesto.

    Ejemplo:

        level = high
        direction = rising
        stress = elevated
        shock = False

    significa que la volatilidad es alta, está aumentando y
    presenta cierto estrés respecto a su comportamiento habitual,
    pero no se ha detectado un shock.
    """

    VOLATILITY_ELEVATED_ZSCORE = 1.0
    VOLATILITY_EXTREME_ZSCORE = 2.0

    @classmethod
    def interpret(
        cls,
        features: pd.Series,
        signals: pd.Series,
    ) -> dict[str, Any]:

        volatility = safe_float(
            features.get("rolling_volatility")
        )

        volatility_zscore = safe_float(
            features.get("volatility_zscore")
        )

        volatility_change = safe_float(
            features.get("volatility_change")
        )

        high = safe_bool(
            signals.get("high_volatility", False)
        )

        extreme = safe_bool(
            signals.get("extreme_volatility", False)
        )

        increasing = safe_bool(
            signals.get("volatility_increasing", False)
        )

        decreasing = safe_bool(
            signals.get("volatility_decreasing", False)
        )

        shock = safe_bool(
            signals.get("volatility_shock", False)
        )

        # ---------------------------------------------------------
        # 1. CURRENT LEVEL
        # ---------------------------------------------------------

        if extreme:
            level = "extreme"

        elif high:
            level = "high"

        elif volatility is None:
            level = "unknown"

        else:
            level = "normal"

        # ---------------------------------------------------------
        # 2. DIRECTION
        # ---------------------------------------------------------
        #
        # Rising/falling describe the evolution of volatility,
        # not whether the situation is good or bad.

        if increasing and not decreasing:
            direction = "rising"

        elif decreasing and not increasing:
            direction = "falling"

        elif volatility_change is None:
            direction = "unknown"

        elif volatility_change > 0:
            direction = "rising"

        elif volatility_change < 0:
            direction = "falling"

        else:
            direction = "stable"

        # ---------------------------------------------------------
        # 3. STRESS
        # ---------------------------------------------------------
        #
        # Stress measures how unusual the current volatility is
        # relative to its historical distribution.

        if volatility_zscore is None:
            stress = "unknown"

        elif (
            volatility_zscore
            >= cls.VOLATILITY_EXTREME_ZSCORE
        ):
            stress = "extreme"

        elif (
            volatility_zscore
            >= cls.VOLATILITY_ELEVATED_ZSCORE
        ):
            stress = "elevated"

        else:
            stress = "normal"

        # ---------------------------------------------------------
        # 4. RETURN
        # ---------------------------------------------------------

        return {
            # Canonical semantic fields
            "level": level,
            "direction": direction,
            "stress": stress,
            "shock": shock,

            # Compatibility / raw signal fields
            "high": high,
            "extreme": extreme,
            "increasing": increasing,
            "decreasing": decreasing,

            # Raw values
            "volatility": serialize(
                features.get("rolling_volatility")
            ),
            "volatility_zscore": serialize(
                features.get("volatility_zscore")
            ),
            "volatility_change": serialize(
                features.get("volatility_change")
            ),
        }