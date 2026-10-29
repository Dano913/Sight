from __future__ import annotations

import numpy as np
import pandas as pd

from app.models.enums import GrowthMethod
from app.services.features.growth_features import growth_features


class TestGrowthFeatures:

    def test_returns_all_growth_features(self):
        series = pd.Series(
            [100.0, 105.0, 110.0, 115.0, 120.0, 125.0]
        )

        result = growth_features(
            series,
            frequency="annual",
        )

        expected_columns = [
            "log_difference",
            "percentage_change",
            "cumulative_growth",
            "momentum",
            "yoy_growth",
            "yoy_log_growth",
        ]

        assert list(result.columns) == expected_columns

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=6,
            freq="YS",
        )

        series = pd.Series(
            [100.0, 105.0, 110.0, 115.0, 120.0, 125.0],
            index=index,
        )

        result = growth_features(
            series,
            frequency="annual",
        )

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )

    def test_preserves_length(self):
        series = pd.Series(
            [100.0, 105.0, 110.0, 115.0, 120.0, 125.0]
        )

        result = growth_features(
            series,
            frequency="annual",
        )

        assert len(result) == len(series)

    def test_percentage_change(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        result = growth_features(
            series,
            frequency="annual",
        )

        expected = pd.Series(
            [
                np.nan,
                0.10,
                0.10,
                0.10,
            ]
        )

        pd.testing.assert_series_equal(
            result["percentage_change"],
            expected,
            check_names=False,
        )

    def test_log_difference(self):
        series = pd.Series(
            [100.0, 110.0, 121.0]
        )

        result = growth_features(
            series,
            frequency="annual",
        )

        expected = pd.Series(
            [
                np.nan,
                np.log(110 / 100),
                np.log(121 / 110),
            ]
        )

        pd.testing.assert_series_equal(
            result["log_difference"],
            expected,
            check_names=False,
        )

    def test_annual_yoy_growth(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        result = growth_features(
            series,
            frequency="annual",
        )

        expected = pd.Series(
            [
                np.nan,
                0.10,
                0.10,
                0.10,
            ]
        )

        pd.testing.assert_series_equal(
            result["yoy_growth"],
            expected,
            check_names=False,
        )

    def test_annual_yoy_log_growth(self):
        series = pd.Series(
            [100.0, 110.0, 121.0]
        )

        result = growth_features(
            series,
            frequency="annual",
        )

        expected = pd.Series(
            [
                np.nan,
                np.log(110 / 100),
                np.log(121 / 110),
            ]
        )

        pd.testing.assert_series_equal(
            result["yoy_log_growth"],
            expected,
            check_names=False,
        )

    def test_annual_cumulative_growth(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        result = growth_features(
            series,
            frequency="annual",
        )

        expected = pd.Series(
            [
                np.nan,
                0.10,
                0.21,
                0.331,
            ]
        )

        pd.testing.assert_series_equal(
            result["cumulative_growth"],
            expected,
            check_names=False,
        )

    def test_annual_momentum(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        result = growth_features(
            series,
            frequency="annual",
        )

        # annual → MOMENTUM_PERIODS = 2
        expected = pd.Series(
            [
                np.nan,
                np.nan,
                0.21,
                0.21,
            ]
        )

        pd.testing.assert_series_equal(
            result["momentum"],
            expected,
            check_names=False,
        )

    def test_rate_method_returns_correct_columns(self):
        series = pd.Series([1.0, 1.5, 2.0, 2.5])

        result = growth_features(
            series,
            frequency="quarterly",
            growth_method=GrowthMethod.RATE,
        )

        assert list(result.columns) == ["change", "yoy_change", "momentum"]

    def test_rate_method_handles_negative_values_and_zero_crossing(self):
        # Secuencia continua de subidas de tipos cruzando por 0%
        series = pd.Series(
            [-0.50, -0.25, 0.00, 0.25, 0.50, 0.75]
        )

        result = growth_features(
            series,
            frequency="annual",
            growth_method=GrowthMethod.RATE,
        )

        expected_change = pd.Series(
            [np.nan, 0.25, 0.25, 0.25, 0.25, 0.25]
        )
        expected_yoy = pd.Series(
            [np.nan, 0.25, 0.25, 0.25, 0.25, 0.25]
        )
        # Para frequency="annual", momentum_periods = 2
        expected_momentum = pd.Series(
            [np.nan, np.nan, 0.50, 0.50, 0.50, 0.50]
        )

        pd.testing.assert_series_equal(
            result["change"],
            expected_change,
            check_names=False,
        )
        pd.testing.assert_series_equal(
            result["yoy_change"],
            expected_yoy,
            check_names=False,
        )
        pd.testing.assert_series_equal(
            result["momentum"],
            expected_momentum,
            check_names=False,
        )

    def test_rate_method_quarterly_periods(self):
        series = pd.Series([1.0, 1.2, 1.5, 1.7, 2.0, 2.4])

        result = growth_features(
            series,
            frequency="quarterly",
            growth_method=GrowthMethod.RATE,
        )

        # quarterly → periods_per_year=4, momentum_periods=2
        assert len(result) == 6
        assert np.isnan(result["yoy_change"].iloc[0])
        assert np.isnan(result["yoy_change"].iloc[3])
        assert np.isclose(result["yoy_change"].iloc[4], 2.0 - 1.0)
        assert np.isclose(result["yoy_change"].iloc[5], 2.4 - 1.2)
        assert np.isclose(result["momentum"].iloc[2], 1.5 - 1.0)
        assert np.isclose(result["momentum"].iloc[3], 1.7 - 1.2)