from __future__ import annotations

import pandas as pd


class FeatureAnalysisService:
    """
    Convierte los features estadísticos generados por FeatureEngine
    en señales analíticas.

    No calcula nuevos features. Adapta las señales de crecimiento
    al tipo de serie:
      - LOG: utiliza percentage_change.
      - RATE: utiliza change.

    La interpretación económica pertenece a
    EconomicInterpretationService.
    """

    SLOPE_EPSILON = 1e-10
    STRONG_TREND_CHANGE_THRESHOLD = 0.50

    HIGH_VOLATILITY_ZSCORE = 2.0
    EXTREME_VOLATILITY_ZSCORE = 3.0
    HIGH_VOLATILITY_MULTIPLIER = 1.5

    SIGNIFICANT_DRAWDOWN = -0.10
    SEVERE_DRAWDOWN = -0.20

    NEAR_HIGH_THRESHOLD = -0.05
    NEAR_LOW_THRESHOLD = 0.05

    REQUIRED_COLUMNS = {
        "momentum",
        "rolling_slope_short",
        "rolling_slope_medium",
        "rolling_slope_long",
        "acceleration",
        "slope_change",
        "trend_change",
        "rolling_volatility",
        "volatility_change",
        "volatility_zscore",
        "drawdown",
        "distance_from_max",
        "distance_from_min",
        "percentile",
    }

    @classmethod
    def analyze(cls, features: pd.DataFrame) -> pd.DataFrame:
        """
        Genera señales analíticas conservando el índice de entrada.

        Admite features de series LOG y RATE.
        """

        cls._validate_features(features)

        signals = pd.DataFrame(index=features.index)

        # ==========================================================
        # GROWTH / CHANGE
        # ==========================================================

        if "percentage_change" in features.columns:
            growth_signal = features["percentage_change"]
        else:
            # En series RATE se interpreta como variación absoluta
            # de la tasa, no como crecimiento porcentual.
            growth_signal = features["change"]

        signals["series_increasing"] = growth_signal > 0
        signals["series_decreasing"] = growth_signal < 0

        # Compatibilidad con las señales existentes.
        # En series RATE estas señales representan una subida o
        # bajada de la tasa, no crecimiento económico.
        signals["positive_growth"] = growth_signal > 0
        signals["negative_growth"] = growth_signal < 0

        acceleration = features["acceleration"]

        signals["accelerating_growth"] = acceleration > 0
        signals["decelerating_growth"] = acceleration < 0

        if not signals.empty:
            signals.iloc[
                0, signals.columns.get_loc("accelerating_growth")
            ] = False
            signals.iloc[
                0, signals.columns.get_loc("decelerating_growth")
            ] = False

        # ==========================================================
        # TREND
        # ==========================================================

        slopes = features[
            [
                "rolling_slope_short",
                "rolling_slope_medium",
                "rolling_slope_long",
            ]
        ]

        available_slopes = slopes.notna().sum(axis=1)
        positive_slopes = (
            slopes > cls.SLOPE_EPSILON
        ).sum(axis=1)
        negative_slopes = (
            slopes < -cls.SLOPE_EPSILON
        ).sum(axis=1)
        neutral_slopes = (
            slopes.abs() <= cls.SLOPE_EPSILON
        ).sum(axis=1)

        signals["bullish_trend"] = (
            (available_slopes >= 2)
            & (positive_slopes == available_slopes)
        )

        signals["bearish_trend"] = (
            (available_slopes >= 2)
            & (negative_slopes == available_slopes)
        )

        signals["mixed_trend"] = (
            (available_slopes >= 2)
            & ~signals["bullish_trend"]
            & ~signals["bearish_trend"]
        )

        signals["neutral_trend"] = (
            (available_slopes > 0)
            & (neutral_slopes == available_slopes)
        )

        # ==========================================================
        # TREND STRUCTURE
        # ==========================================================

        short_slope = features["rolling_slope_short"]
        medium_slope = features["rolling_slope_medium"]
        long_slope = features["rolling_slope_long"]

        signals["short_term_bullish"] = (
            short_slope > cls.SLOPE_EPSILON
        )
        signals["short_term_bearish"] = (
            short_slope < -cls.SLOPE_EPSILON
        )
        signals["medium_term_bullish"] = (
            medium_slope > cls.SLOPE_EPSILON
        )
        signals["medium_term_bearish"] = (
            medium_slope < -cls.SLOPE_EPSILON
        )
        signals["long_term_bullish"] = (
            long_slope > cls.SLOPE_EPSILON
        )
        signals["long_term_bearish"] = (
            long_slope < -cls.SLOPE_EPSILON
        )

        # ==========================================================
        # TREND WEAKENING / STRENGTHENING
        # ==========================================================

        slope_change = features["slope_change"]

        signals["trend_strengthening"] = slope_change > 0
        signals["trend_weakening"] = slope_change < 0

        signals["strong_trend_strengthening"] = (
            slope_change >= cls.STRONG_TREND_CHANGE_THRESHOLD
        )
        signals["strong_trend_weakening"] = (
            slope_change <= -cls.STRONG_TREND_CHANGE_THRESHOLD
        )

        # ==========================================================
        # TREND REVERSAL
        # ==========================================================

        trend_change = features["trend_change"]
        previous_trend_change = trend_change.shift(1)

        positive_to_negative = (
            (previous_trend_change > cls.SLOPE_EPSILON)
            & (trend_change < -cls.SLOPE_EPSILON)
        )

        negative_to_positive = (
            (previous_trend_change < -cls.SLOPE_EPSILON)
            & (trend_change > cls.SLOPE_EPSILON)
        )

        signals["trend_reversal"] = (
            positive_to_negative | negative_to_positive
        )

        # ==========================================================
        # GROWTH / RATE DIRECTION REVERSAL
        # ==========================================================

        previous_growth = growth_signal.shift(1)

        signals["growth_reversal"] = (
            ((previous_growth > 0) & (growth_signal < 0))
            | ((previous_growth < 0) & (growth_signal > 0))
        )

        # ==========================================================
        # MOMENTUM
        # ==========================================================

        momentum = features["momentum"]

        signals["positive_momentum"] = momentum > 0
        signals["negative_momentum"] = momentum < 0
        signals["momentum_improving"] = momentum.diff() > 0
        signals["momentum_weakening"] = momentum.diff() < 0

        # ==========================================================
        # VOLATILITY
        # ==========================================================

        rolling_volatility = features["rolling_volatility"]
        volatility_zscore = features["volatility_zscore"]
        volatility_change = features["volatility_change"]

        volatility_mean = (
            rolling_volatility.expanding(min_periods=1).mean()
        )

        signals["high_volatility"] = (
            (
                volatility_zscore
                > cls.HIGH_VOLATILITY_ZSCORE
            )
            | (
                rolling_volatility
                > (
                    volatility_mean
                    * cls.HIGH_VOLATILITY_MULTIPLIER
                )
            )
        )

        signals["extreme_volatility"] = (
            volatility_zscore > cls.EXTREME_VOLATILITY_ZSCORE
        )
        signals["volatility_increasing"] = volatility_change > 0
        signals["volatility_decreasing"] = volatility_change < 0

        signals["volatility_shock"] = (
            (volatility_zscore > cls.HIGH_VOLATILITY_ZSCORE)
            & (volatility_change > 0)
        )

        # ==========================================================
        # DRAWDOWN
        # ==========================================================

        drawdown = features["drawdown"]

        signals["significant_drawdown"] = (
            drawdown < cls.SIGNIFICANT_DRAWDOWN
        )
        signals["severe_drawdown"] = (
            drawdown < cls.SEVERE_DRAWDOWN
        )

        # ==========================================================
        # HISTORICAL POSITION
        # ==========================================================

        distance_from_max = features["distance_from_max"]
        distance_from_min = features["distance_from_min"]

        signals["near_historical_high"] = (
            distance_from_max.notna()
            & (
                distance_from_max
                > cls.NEAR_HIGH_THRESHOLD
            )
        )

        signals["near_historical_low"] = (
            distance_from_min.notna()
            & (
                distance_from_min
                < cls.NEAR_LOW_THRESHOLD
            )
        )

        # ==========================================================
        # EXTREME POSITION
        # ==========================================================

        percentile = features["percentile"]

        signals["historical_extreme_high"] = percentile >= 0.95
        signals["historical_extreme_low"] = percentile <= 0.05

        # ==========================================================
        # RECOVERY / FALLING FROM HIGH
        # ==========================================================

        drawdown_change = drawdown.diff()

        signals["recovering_from_drawdown"] = (
            (drawdown < 0) & (drawdown_change > 0)
        )

        distance_from_max_change = distance_from_max.diff()

        signals["falling_from_high"] = (
            (distance_from_max < 0)
            & (distance_from_max_change < 0)
        )

        return signals

    @staticmethod
    def _validate_features(features: pd.DataFrame) -> None:
        if not isinstance(features, pd.DataFrame):
            raise TypeError(
                "features debe ser un pandas.DataFrame"
            )

        missing_columns = (
            FeatureAnalysisService.REQUIRED_COLUMNS
            - set(features.columns)
        )

        if missing_columns:
            raise ValueError(
                "Faltan columnas necesarias para el análisis: "
                f"{sorted(missing_columns)}"
            )

        has_percentage_change = (
            "percentage_change" in features.columns
        )
        has_rate_change = "change" in features.columns

        if not has_percentage_change and not has_rate_change:
            raise ValueError(
                "Falta una columna de variación: se requiere "
                "'percentage_change' para series LOG o 'change' "
                "para series RATE."
            )

        if features.empty:
            return