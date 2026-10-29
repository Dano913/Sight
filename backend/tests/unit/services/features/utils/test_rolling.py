from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.features.utils.rolling import (
    rolling_zscore,
    rolling_percentile,
    rolling_slope,
    rolling_mean,
    rolling_std,
    rolling_min,
    rolling_max,
    rolling_range,
    rolling_median,
)


class TestRollingZscore:

    def test_basic(self):
        series = pd.Series([1.0, 2.0, 3.0, 4.0])

        result = rolling_zscore(
            series,
            window=3,
        )

        expected = (
            series
            - series.rolling(3).mean()
        ) / series.rolling(3).std()

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_constant_window(self):
        series = pd.Series(
            [5.0, 5.0, 5.0, 5.0]
        )

        result = rolling_zscore(
            series,
            window=3,
        )

        expected = pd.Series(
            [np.nan, np.nan, np.nan, np.nan]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )


class TestRollingPercentile:

    def test_basic(self):
        series = pd.Series(
            [10.0, 20.0, 30.0, 40.0]
        )

        result = rolling_percentile(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                1.0,
                1.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_current_value_in_middle(self):
        series = pd.Series(
            [10.0, 30.0, 20.0]
        )

        result = rolling_percentile(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                2 / 3,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_constant_window(self):
        series = pd.Series(
            [5.0, 5.0, 5.0]
        )

        result = rolling_percentile(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                1.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )


class TestRollingSlope:

    def test_positive_linear_trend(self):
        series = pd.Series(
            [10.0, 12.0, 14.0, 16.0]
        )

        result = rolling_slope(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                2.0,
                2.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_negative_linear_trend(self):
        series = pd.Series(
            [10.0, 8.0, 6.0, 4.0]
        )

        result = rolling_slope(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                -2.0,
                -2.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_constant_series(self):
        series = pd.Series(
            [5.0, 5.0, 5.0]
        )

        result = rolling_slope(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                0.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )


class TestRollingBasic:

    def test_mean(self):
        series = pd.Series(
            [1.0, 2.0, 3.0, 4.0]
        )

        result = rolling_mean(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                2.0,
                3.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_std(self):
        series = pd.Series(
            [1.0, 2.0, 3.0, 4.0]
        )

        result = rolling_std(
            series,
            window=3,
        )

        expected = series.rolling(3).std()

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_min(self):
        series = pd.Series(
            [3.0, 1.0, 4.0, 2.0]
        )

        result = rolling_min(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                1.0,
                1.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_max(self):
        series = pd.Series(
            [3.0, 1.0, 4.0, 2.0]
        )

        result = rolling_max(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                4.0,
                4.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_range(self):
        series = pd.Series(
            [3.0, 1.0, 4.0, 2.0]
        )

        result = rolling_range(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                3.0,
                3.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_median(self):
        series = pd.Series(
            [1.0, 4.0, 2.0, 8.0]
        )

        result = rolling_median(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                2.0,
                4.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )


class TestRollingProperties:

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=5,
            freq="YS",
        )

        series = pd.Series(
            [10.0, 20.0, 30.0, 40.0, 50.0],
            index=index,
        )

        functions = [
            lambda s: rolling_zscore(s, 3),
            lambda s: rolling_percentile(s, 3),
            lambda s: rolling_slope(s, 3),
            lambda s: rolling_mean(s, 3),
            lambda s: rolling_std(s, 3),
            lambda s: rolling_min(s, 3),
            lambda s: rolling_max(s, 3),
            lambda s: rolling_range(s, 3),
            lambda s: rolling_median(s, 3),
        ]

        for function in functions:
            result = function(series)

            pd.testing.assert_index_equal(
                result.index,
                series.index,
            )

    def test_output_has_same_length(self):
        series = pd.Series(
            [10.0, 20.0, 30.0, 40.0, 50.0]
        )

        functions = [
            lambda s: rolling_zscore(s, 3),
            lambda s: rolling_percentile(s, 3),
            lambda s: rolling_slope(s, 3),
            lambda s: rolling_mean(s, 3),
            lambda s: rolling_std(s, 3),
            lambda s: rolling_min(s, 3),
            lambda s: rolling_max(s, 3),
            lambda s: rolling_range(s, 3),
            lambda s: rolling_median(s, 3),
        ]

        for function in functions:
            result = function(series)

            assert len(result) == len(series)