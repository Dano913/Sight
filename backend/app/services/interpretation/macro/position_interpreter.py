from __future__ import annotations

from typing import Any

import pandas as pd

from ..utils import safe_bool, safe_float, serialize


class PositionInterpreter:
    """
    Interpreta la posición actual de una serie respecto a su histórico.

    Separa claramente:

        position:
            ubicación relativa dentro de la distribución histórica.

        mean_position:
            distancia respecto a la media móvil.

        drawdown:
            distancia respecto al máximo previo.

        direction:
            evolución reciente desde un extremo.

        extreme:
            indica si la observación se encuentra en una zona
            históricamente extrema.

    Este intérprete es descriptivo.
    No determina si una posición es buena, mala, barata o cara.
    """

    DRAWDOWN_THRESHOLD = -0.10

    POSITION_UPPER_EXTREME = 0.90
    POSITION_UPPER = 0.75
    POSITION_LOWER = 0.25
    POSITION_LOWER_EXTREME = 0.10

    MEAN_DISTANCE_THRESHOLD = 0.05

    @classmethod
    def interpret(
        cls,
        features: pd.Series,
        signals: pd.Series,
    ) -> dict[str, Any]:
        percentile = safe_float(features.get("percentile"))
        rolling_percentile = safe_float(features.get("rolling_percentile"))
        zscore = safe_float(features.get("zscore"))
        distance_from_mean = safe_float(
            features.get("distance_from_rolling_mean")
        )
        distance_from_max = safe_float(
            features.get("distance_from_max")
        )
        distance_from_min = safe_float(
            features.get("distance_from_min")
        )
        drawdown = safe_float(features.get("drawdown"))

        near_high = safe_bool(signals.get("near_historical_high", False))
        near_low = safe_bool(signals.get("near_historical_low", False))
        significant_drawdown = safe_bool(
            signals.get("significant_drawdown", False)
        )
        severe_drawdown = safe_bool(
            signals.get("severe_drawdown", False)
        )
        historical_extreme_high = safe_bool(
            signals.get("historical_extreme_high", False)
        )
        historical_extreme_low = safe_bool(
            signals.get("historical_extreme_low", False)
        )
        recovering = safe_bool(
            signals.get("recovering_from_drawdown", False)
        )
        falling_from_high = safe_bool(
            signals.get("falling_from_high", False)
        )

        position = cls._classify_position(
            percentile=percentile,
            historical_extreme_high=historical_extreme_high,
            historical_extreme_low=historical_extreme_low,
            near_high=near_high,
            near_low=near_low,
        )

        mean_position = cls._classify_mean_position(
            distance_from_mean
        )

        drawdown_state = cls._classify_drawdown(
            drawdown=drawdown,
            significant_drawdown=significant_drawdown,
            severe_drawdown=severe_drawdown,
        )

        direction = cls._classify_direction(
            recovering=recovering,
            falling_from_high=falling_from_high,
        )

        extreme = cls._classify_extreme(
            historical_extreme_high=historical_extreme_high,
            historical_extreme_low=historical_extreme_low,
        )

        state = cls._classify_state(
            position=position,
            drawdown_state=drawdown_state,
            extreme=extreme,
        )

        return {
            "state": state,

            "position": position,
            "mean_position": mean_position,
            "drawdown_state": drawdown_state,
            "direction": direction,
            "extreme": extreme,

            "near_high": near_high,
            "near_low": near_low,

            "historical_extreme_high": historical_extreme_high,
            "historical_extreme_low": historical_extreme_low,

            "significant_drawdown": significant_drawdown,
            "severe_drawdown": severe_drawdown,

            "recovering_from_drawdown": recovering,
            "falling_from_high": falling_from_high,

            "zscore": serialize(features.get("zscore")),
            "percentile": serialize(features.get("percentile")),
            "rolling_percentile": serialize(
                features.get("rolling_percentile")
            ),
            "distance_from_mean": serialize(
                features.get("distance_from_rolling_mean")
            ),
            "distance_from_max": serialize(
                features.get("distance_from_max")
            ),
            "distance_from_min": serialize(
                features.get("distance_from_min")
            ),
            "drawdown": serialize(features.get("drawdown")),
        }

    @classmethod
    def _classify_position(
        cls,
        *,
        percentile: float | None,
        historical_extreme_high: bool,
        historical_extreme_low: bool,
        near_high: bool,
        near_low: bool,
    ) -> str:
        """
        Clasifica únicamente la ubicación relativa de la observación.
        """

        if percentile is None:
            return "unknown"

        if (
            historical_extreme_high
            or percentile >= cls.POSITION_UPPER_EXTREME
        ):
            return "upper_extreme"

        if (
            historical_extreme_low
            or percentile <= cls.POSITION_LOWER_EXTREME
        ):
            return "lower_extreme"

        if near_high or percentile >= cls.POSITION_UPPER:
            return "upper"

        if near_low or percentile <= cls.POSITION_LOWER:
            return "lower"

        return "middle"

    @classmethod
    def _classify_mean_position(
        cls,
        distance_from_mean: float | None,
    ) -> str:
        """
        Clasifica la distancia respecto a la media móvil.
        """

        if distance_from_mean is None:
            return "unknown"

        if distance_from_mean > cls.MEAN_DISTANCE_THRESHOLD:
            return "well_above_mean"

        if distance_from_mean > 0:
            return "above_mean"

        if distance_from_mean < -cls.MEAN_DISTANCE_THRESHOLD:
            return "well_below_mean"

        if distance_from_mean < 0:
            return "below_mean"

        return "at_mean"

    @classmethod
    def _classify_drawdown(
        cls,
        *,
        drawdown: float | None,
        significant_drawdown: bool,
        severe_drawdown: bool,
    ) -> str:
        """
        Clasifica la situación de drawdown independientemente
        de la posición histórica.
        """

        if drawdown is None:
            return "unknown"

        if severe_drawdown:
            return "severe"

        if significant_drawdown:
            return "significant"

        if drawdown <= cls.DRAWDOWN_THRESHOLD:
            return "significant"

        if drawdown < 0:
            return "minor"

        return "none"

    @staticmethod
    def _classify_direction(
        *,
        recovering: bool,
        falling_from_high: bool,
    ) -> str:
        """
        Describe la evolución reciente de la posición.
        """

        if recovering and not falling_from_high:
            return "recovering"

        if falling_from_high and not recovering:
            return "falling"

        if recovering and falling_from_high:
            return "mixed"

        return "stable"

    @staticmethod
    def _classify_extreme(
        *,
        historical_extreme_high: bool,
        historical_extreme_low: bool,
    ) -> str:
        """
        Identifica si la posición se encuentra en un extremo histórico.
        """

        if historical_extreme_high and historical_extreme_low:
            return "mixed"

        if historical_extreme_high:
            return "high"

        if historical_extreme_low:
            return "low"

        return "none"

    @staticmethod
    def _classify_state(
        *,
        position: str,
        drawdown_state: str,
        extreme: str,
    ) -> str:
        """
        Genera un resumen descriptivo de la posición.

        No mezcla aquí si la situación es favorable o desfavorable.
        """

        if drawdown_state == "severe":
            return "severe_drawdown"

        if drawdown_state == "significant":
            return "drawdown"

        if extreme == "high":
            return "historical_high"

        if extreme == "low":
            return "historical_low"

        if position == "upper":
            return "upper"

        if position == "lower":
            return "lower"

        if position == "upper_extreme":
            return "upper_extreme"

        if position == "lower_extreme":
            return "lower_extreme"

        if position == "middle":
            return "normal"

        return "unknown"