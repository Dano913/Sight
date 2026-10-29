from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.features.trend_features import trend_features


class TestTrendFeatures:

    def test_returns_all_trend_features(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0, 140.0, 150.0]
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        expected_columns = [
            "rolling_slope_short",
            "rolling_slope_medium",
            "rolling_slope_long",
            "acceleration",
            "slope_change",
            "trend_change",
        ]

        assert list(result.columns) == expected_columns

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=6,
            freq="YS",
        )

        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0, 140.0, 150.0],
            index=index,
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )

    def test_preserves_length(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0, 140.0, 150.0]
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        assert len(result) == len(series)

    def test_short_slope(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        expected = pd.Series(
            [
                np.nan,
                10.0,
                10.0,
                10.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["rolling_slope_short"],
            expected,
            check_names=False,
        )

    def test_medium_slope(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                10.0,
                10.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["rolling_slope_medium"],
            expected,
            check_names=False,
        )

    def test_long_slope(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                np.nan,
                10.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["rolling_slope_long"],
            expected,
            check_names=False,
        )

    def test_acceleration(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 135.0]
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                0.0,
                5.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["acceleration"],
            expected,
            check_names=False,
        )

    def test_slope_change(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 135.0]
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                0.0,
                5.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["slope_change"],
            expected,
            check_names=False,
        )

    def test_trend_change_for_constant_trend(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0, 140.0]
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        # Las tres pendientes son iguales:
        # no existe cambio relativo de tendencia.
        expected = pd.Series(
            [
                np.nan,
                np.nan,
                np.nan,
                0.0,
                0.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["trend_change"],
            expected,
            check_names=False,
        )

    def test_trend_change_flat_series_returns_zero_not_nan(self):
        series = pd.Series(
            [100.0, 100.0, 100.0, 100.0, 100.0]
        )

        result = trend_features(
            series,
            short_window=2,
            medium_window=3,
            long_window=4,
        )

        # Cuando las pendientes son todas 0, trend_change no debe ser NaN sino 0.0
        expected = pd.Series(
            [
                np.nan,
                np.nan,
                np.nan,
                0.0,
                0.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["trend_change"],
            expected,
            check_names=False,
        )