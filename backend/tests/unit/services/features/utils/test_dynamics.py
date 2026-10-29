from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.features.utils.dynamics import (
    acceleration,
    rolling_volatility,
    drawdown,
    distance_from_rolling_mean,
    momentum,
)


class TestAcceleration:

    def test_basic_acceleration(self):
        series = pd.Series(
            [10.0, 12.0, 16.0, 22.0]
        )

        result = acceleration(series)

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

    def test_constant_series(self):
        series = pd.Series(
            [10.0, 10.0, 10.0]
        )

        result = acceleration(series)

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


class TestRollingVolatility:

    def test_basic_rolling_volatility(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        result = rolling_volatility(
            series,
            window=3,
        )

        returns = series.pct_change()

        expected = returns.rolling(3).std()

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_window_controls_observations(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        result = rolling_volatility(
            series,
            window=2,
        )

        returns = series.pct_change()

        expected = returns.rolling(2).std()

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )


class TestDrawdown:

    def test_drawdown_from_running_maximum(self):
        series = pd.Series(
            [100.0, 120.0, 90.0, 110.0, 80.0]
        )

        result = drawdown(series)

        expected = pd.Series(
            [
                0.0,
                0.0,
                -0.25,
                -1 / 12,
                -1 / 3,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_new_high_resets_drawdown(self):
        series = pd.Series(
            [100.0, 90.0, 110.0]
        )

        result = drawdown(series)

        expected = pd.Series(
            [
                0.0,
                -0.10,
                0.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_constant_series(self):
        series = pd.Series(
            [100.0, 100.0, 100.0]
        )

        result = drawdown(series)

        expected = pd.Series(
            [0.0, 0.0, 0.0]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )


class TestDistanceFromRollingMean:

    def test_basic_distance(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = distance_from_rolling_mean(
            series,
            window=3,
        )

        rolling_mean = series.rolling(3).mean()

        expected = (
            (series - rolling_mean)
            / rolling_mean
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_value_equal_to_mean(self):
        series = pd.Series(
            [100.0, 100.0, 100.0]
        )

        result = distance_from_rolling_mean(
            series,
            window=2,
        )

        expected = pd.Series(
            [
                np.nan,
                0.0,
                0.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )


class TestMomentum:

    def test_basic_momentum(self):
        series = pd.Series(
            [100.0, 110.0, 121.0]
        )

        result = momentum(
            series,
            periods=1,
        )

        expected = pd.Series(
            [
                np.nan,
                0.10,
                0.10,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_momentum_with_periods(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        result = momentum(
            series,
            periods=2,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                0.21,
                0.21,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_negative_momentum(self):
        series = pd.Series(
            [100.0, 90.0]
        )

        result = momentum(
            series,
            periods=1,
        )

        expected = pd.Series(
            [
                np.nan,
                -0.10,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )


class TestDynamicsProperties:

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=5,
            freq="YS",
        )

        series = pd.Series(
            [100.0, 110.0, 90.0, 120.0, 100.0],
            index=index,
        )

        functions = [
            acceleration,
            drawdown,
        ]

        for function in functions:
            result = function(series)

            pd.testing.assert_index_equal(
                result.index,
                series.index,
            )

        rolling_functions = [
            lambda s: rolling_volatility(s, window=3),
            lambda s: distance_from_rolling_mean(s, window=3),
            lambda s: momentum(s, periods=2),
        ]

        for function in rolling_functions:
            result = function(series)

            pd.testing.assert_index_equal(
                result.index,
                series.index,
            )