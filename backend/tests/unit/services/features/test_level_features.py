from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.features.level_features import level_features


class TestLevelFeatures:

    def test_returns_all_level_features(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0, 140.0]
        )

        result = level_features(
            series,
            window=3,
        )

        expected_columns = [
            "value",
            "rolling_mean",
            "rolling_median",
            "rolling_min",
            "rolling_max",
            "rolling_percentile",
            "rolling_zscore",
            "distance_from_rolling_mean",
        ]

        assert list(result.columns) == expected_columns

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=5,
            freq="YS",
        )

        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0, 140.0],
            index=index,
        )

        result = level_features(
            series,
            window=3,
        )

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )

    def test_preserves_length(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0, 140.0]
        )

        result = level_features(
            series,
            window=3,
        )

        assert len(result) == len(series)

    def test_value(self):
        series = pd.Series(
            [100.0, 110.0, 120.0]
        )

        result = level_features(
            series,
            window=2,
        )

        pd.testing.assert_series_equal(
            result["value"],
            series,
            check_names=False,
        )

    def test_rolling_mean(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = level_features(
            series,
            window=2,
        )

        expected = pd.Series(
            [
                np.nan,
                105.0,
                115.0,
                125.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["rolling_mean"],
            expected,
            check_names=False,
        )

    def test_rolling_median(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = level_features(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                110.0,
                120.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["rolling_median"],
            expected,
            check_names=False,
        )

    def test_rolling_min(self):
        series = pd.Series(
            [100.0, 110.0, 90.0, 130.0]
        )

        result = level_features(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                90.0,
                90.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["rolling_min"],
            expected,
            check_names=False,
        )

    def test_rolling_max(self):
        series = pd.Series(
            [100.0, 110.0, 90.0, 130.0]
        )

        result = level_features(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                110.0,
                130.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["rolling_max"],
            expected,
            check_names=False,
        )

    def test_rolling_percentile(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 90.0]
        )

        result = level_features(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                1.0,
                1 / 3,
            ]
        )

        pd.testing.assert_series_equal(
            result["rolling_percentile"],
            expected,
            check_names=False,
        )

    def test_rolling_zscore(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = level_features(
            series,
            window=3,
        )

        expected_last = (
            130.0 - 120.0
        ) / pd.Series(
            [110.0, 120.0, 130.0]
        ).std()

        assert np.isnan(result["rolling_zscore"].iloc[0])
        assert np.isnan(result["rolling_zscore"].iloc[1])
        assert np.isclose(
            result["rolling_zscore"].iloc[3],
            expected_last,
        )

    def test_distance_from_rolling_mean(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = level_features(
            series,
            window=2,
        )

        expected = pd.Series(
            [
                np.nan,
                (110.0 - 105.0) / 105.0,
                (120.0 - 115.0) / 115.0,
                (130.0 - 125.0) / 125.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["distance_from_rolling_mean"],
            expected,
            check_names=False,
        )