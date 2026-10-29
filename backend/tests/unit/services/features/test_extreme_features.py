from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.features.extreme_features import extreme_features


class TestExtremeFeatures:

    def test_returns_all_extreme_features(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0, 115.0]
        )

        result = extreme_features(
            series,
            window=3,
        )

        expected_columns = [
            "zscore",
            "percentile",
            "distance_from_max",
            "distance_from_min",
            "drawdown",
        ]

        assert list(result.columns) == expected_columns

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=5,
            freq="YS",
        )

        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0, 115.0],
            index=index,
        )

        result = extreme_features(
            series,
            window=3,
        )

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )

    def test_preserves_length(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0, 115.0]
        )

        result = extreme_features(
            series,
            window=3,
        )

        assert len(result) == len(series)

    def test_zscore(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = extreme_features(
            series,
            window=3,
        )

        expected = (
            series - series.mean()
        ) / series.std()

        pd.testing.assert_series_equal(
            result["zscore"],
            expected,
            check_names=False,
        )

    def test_percentile(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = extreme_features(
            series,
            window=3,
        )

        expected = series.rank(
            method="average",
            pct=True,
        )

        pd.testing.assert_series_equal(
            result["percentile"],
            expected,
            check_names=False,
        )

    def test_distance_from_max(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0]
        )

        result = extreme_features(
            series,
            window=3,
        )

        rolling_max = series.rolling(3).max()

        expected = (
            series - rolling_max
        ) / rolling_max

        pd.testing.assert_series_equal(
            result["distance_from_max"],
            expected,
            check_names=False,
        )

    def test_distance_from_min(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0]
        )

        result = extreme_features(
            series,
            window=3,
        )

        rolling_min = series.rolling(3).min()

        expected = (
            series - rolling_min
        ) / rolling_min

        pd.testing.assert_series_equal(
            result["distance_from_min"],
            expected,
            check_names=False,
        )

    def test_drawdown(self):
        series = pd.Series(
            [100.0, 120.0, 110.0, 90.0, 130.0]
        )

        result = extreme_features(
            series,
            window=3,
        )

        running_max = series.cummax()

        expected = (
            series - running_max
        ) / running_max

        pd.testing.assert_series_equal(
            result["drawdown"],
            expected,
            check_names=False,
        )

    def test_new_maximum_has_zero_drawdown(self):
        series = pd.Series(
            [100.0, 120.0, 110.0, 130.0]
        )

        result = extreme_features(
            series,
            window=3,
        )

        assert result["drawdown"].iloc[1] == 0.0
        assert result["drawdown"].iloc[3] == 0.0

    def test_values_below_maximum_have_negative_drawdown(self):
        series = pd.Series(
            [100.0, 120.0, 110.0]
        )

        result = extreme_features(
            series,
            window=3,
        )

        assert result["drawdown"].iloc[2] < 0.0

    def test_negative_series_distance_from_max_preserves_sign(self):
        # Para valores negativos, si cae respecto al máximo, distance_from_max debe ser negativo
        series = pd.Series([-1.0, -1.0, -2.0, -3.0])

        result = extreme_features(
            series,
            window=3,
        )

        # En la observación 2 (valor -2.0): max ventana es -1.0. Caída relativa: (-2.0 - (-1.0)) / |-1.0| = -1.0 (-100%)
        assert result["distance_from_max"].iloc[2] == -1.0
        assert result["distance_from_max"].iloc[2] < 0.0

    def test_zero_rolling_extremes_avoids_infinities(self):
        series = pd.Series([0.0, 0.0, 0.0])

        result = extreme_features(
            series,
            window=2,
        )

        assert not np.isinf(result["distance_from_max"]).any()
        assert not np.isinf(result["distance_from_min"]).any()
        assert not np.isinf(result["drawdown"]).any()