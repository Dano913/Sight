from __future__ import annotations

import pandas as pd

from app.models.enums import GrowthMethod

from .level_features import level_features
from .growth_features import growth_features
from .trend_features import trend_features
from .volatility_features import volatility_features
from .extreme_features import extreme_features


class FeatureEngine:

    """
    - Recibe la serie original del cliente y sus parámetros.
    - Compute calcula las features llamando a los archivos.
    - Envia las features a la clase FeatureAnalysisService.
    """

    @classmethod
    def compute(
        cls,
        series: pd.Series,
        frequency: str,
        *,
        growth_method: GrowthMethod = GrowthMethod.LOG,
        level_window: int = 8,
        trend_short_window: int = 4,
        trend_medium_window: int = 8,
        trend_long_window: int = 16,
        volatility_window: int = 8,
        extreme_window: int = 8,
    ) -> pd.DataFrame:

        feature_frames = [

            level_features(
                series=series,
                window=level_window,
            ),

            growth_features(
                series=series,
                frequency=frequency,
                growth_method=growth_method,
            ),

            trend_features(
                series=series,
                short_window=trend_short_window,
                medium_window=trend_medium_window,
                long_window=trend_long_window,
            ),

            volatility_features(
                series=series,
                window=volatility_window,
            ),

            extreme_features(
                series=series,
                window=extreme_window,
            ),
        ]

        for features in feature_frames:

            if not isinstance(
                features,
                pd.DataFrame,
            ):
                raise TypeError(
                    "Cada familia de features debe devolver "
                    "un pandas.DataFrame"
                )

        if not feature_frames:
            return pd.DataFrame(
                index=series.index,
            )

        return pd.concat(
            feature_frames,
            axis=1,
        )