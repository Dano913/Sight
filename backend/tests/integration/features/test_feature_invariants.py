from __future__ import annotations

import pandas as pd

from app.services.features.feature_engine import FeatureEngine


class TestFeatureEngineInvariants:

    def test_output_preserves_index(self):
        index = pd.date_range(
            "2000-01-01",
            periods=20,
            freq="YE",
        )

        series = pd.Series(
            range(100, 120),
            index=index,
            dtype=float,
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        assert result.index.equals(series.index)

    def test_output_preserves_length(self):
        series = pd.Series(
            range(100, 120),
            dtype=float,
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        assert len(result) == len(series)

    def test_original_series_is_not_modified(self):
        series = pd.Series(
            [100.0, 105.0, 110.0, 108.0, 115.0]
        )

        original = series.copy()

        FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        pd.testing.assert_series_equal(
            series,
            original,
        )

    def test_output_contains_only_expected_feature_columns(self):
        series = pd.Series(
            [100.0, 105.0, 110.0, 115.0, 120.0] * 4,
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        expected_columns = {
            "value",
            "rolling_mean",
            "rolling_median",
            "rolling_min",
            "rolling_max",
            "rolling_percentile",
            "rolling_zscore",
            "distance_from_rolling_mean",
            "log_difference",
            "percentage_change",
            "cumulative_growth",
            "momentum",
            "yoy_growth",
            "yoy_log_growth",
            "rolling_slope_short",
            "rolling_slope_medium",
            "rolling_slope_long",
            "acceleration",
            "slope_change",
            "trend_change",
            "rolling_std",
            "rolling_volatility",
            "rolling_range",
            "volatility_change",
            "volatility_zscore",
            "zscore",
            "percentile",
            "distance_from_max",
            "distance_from_min",
            "drawdown",
        }

        assert set(result.columns) == expected_columns

    def test_value_feature_equals_input_series(self):
        series = pd.Series(
            [100.0, 105.0, 97.0, 110.0, 120.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        pd.testing.assert_series_equal(
            result["value"],
            series,
            check_names=False,
        )

    def test_rolling_min_is_never_greater_than_rolling_max(self):
        series = pd.Series(
            [100.0, 105.0, 97.0, 110.0, 103.0, 120.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            level_window=3,
        )

        valid = result[
            ["rolling_min", "rolling_max"]
        ].dropna()

        assert (
            valid["rolling_min"]
            <= valid["rolling_max"]
        ).all()

    def test_rolling_mean_is_between_min_and_max(self):
        series = pd.Series(
            [100.0, 105.0, 97.0, 110.0, 103.0, 120.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            level_window=3,
        )

        valid = result[
            [
                "rolling_min",
                "rolling_mean",
                "rolling_max",
            ]
        ].dropna()

        assert (
            valid["rolling_min"]
            <= valid["rolling_mean"]
        ).all()

        assert (
            valid["rolling_mean"]
            <= valid["rolling_max"]
        ).all()

    def test_drawdown_is_never_positive(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0, 115.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        assert (
            result["drawdown"]
            .dropna()
            .le(0.0)
            .all()
        )

    def test_distance_from_max_is_never_positive(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0, 115.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            extreme_window=3,
        )

        assert (
            result["distance_from_max"]
            .dropna()
            .le(0.0)
            .all()
        )

    def test_distance_from_min_is_never_negative(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0, 115.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            extreme_window=3,
        )

        assert (
            result["distance_from_min"]
            .dropna()
            .ge(0.0)
            .all()
        )

    def test_constant_series_has_zero_growth_and_volatility(self):
        series = pd.Series(
            [100.0] * 20
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        assert (
            result["percentage_change"]
            .dropna()
            .eq(0.0)
            .all()
        )

        assert (
            result["log_difference"]
            .dropna()
            .eq(0.0)
            .all()
        )

        assert (
            result["rolling_std"]
            .dropna()
            .eq(0.0)
            .all()
        )

        assert (
            result["rolling_volatility"]
            .dropna()
            .eq(0.0)
            .all()
        )

    def test_constant_series_has_zero_drawdown(self):
        series = pd.Series(
            [100.0] * 20
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        assert (
            result["drawdown"]
            .eq(0.0)
            .all()
        )

    def test_rolling_range_equals_max_minus_min(self):
        series = pd.Series(
            [100.0, 105.0, 97.0, 110.0, 103.0, 120.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            level_window=3,
        )

        valid = result[
            [
                "rolling_range",
                "rolling_max",
                "rolling_min",
            ]
        ].dropna()

        expected = (
            valid["rolling_max"]
            - valid["rolling_min"]
        )

        pd.testing.assert_series_equal(
            valid["rolling_range"],
            expected,
            check_names=False,
        )

    def test_distance_from_max_is_zero_at_rolling_maximum(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0, 115.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            extreme_window=3,
        )

        rolling_max = (
            series.rolling(3).max()
        )

        mask = (
            series == rolling_max
        )

        assert (
            result.loc[mask, "distance_from_max"]
            .eq(0.0)
            .all()
        )

    def test_distance_from_min_is_zero_at_rolling_minimum(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0, 115.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            extreme_window=3,
        )

        rolling_min = (
            series.rolling(3).min()
        )

        mask = (
            series == rolling_min
        )

        assert (
            result.loc[mask, "distance_from_min"]
            .eq(0.0)
            .all()
        )

    def test_log_difference_matches_log_return(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        expected = (
            series / series.shift(1)
        ).apply(
            lambda x: __import__("numpy").log(x)
        )

        pd.testing.assert_series_equal(
            result["log_difference"],
            expected,
            check_names=False,
        )

    def test_momentum_is_positive_when_current_value_is_higher(self):
        series = pd.Series(
            [100.0, 105.0, 110.0, 120.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        assert (
            result["momentum"]
            .dropna()
            .gt(0)
            .all()
        )

    def test_momentum_is_negative_when_current_value_is_lower(self):
        series = pd.Series(
            [130.0, 120.0, 110.0, 105.0, 100.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        assert (
            result["momentum"]
            .dropna()
            .lt(0)
            .all()
        )

    def test_increasing_series_has_positive_slopes(self):
        series = pd.Series(
            [100.0, 105.0, 110.0, 115.0, 120.0, 125.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert (
            result["rolling_slope_short"]
            .dropna()
            .gt(0)
            .all()
        )

        assert (
            result["rolling_slope_medium"]
            .dropna()
            .gt(0)
            .all()
        )

        assert (
            result["rolling_slope_long"]
            .dropna()
            .gt(0)
            .all()
        )

    def test_decreasing_series_has_negative_slopes(self):
        series = pd.Series(
            [125.0, 120.0, 115.0, 110.0, 105.0, 100.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert (
            result["rolling_slope_short"]
            .dropna()
            .lt(0)
            .all()
        )

        assert (
            result["rolling_slope_medium"]
            .dropna()
            .lt(0)
            .all()
        )

        assert (
            result["rolling_slope_long"]
            .dropna()
            .lt(0)
            .all()
        )

    def test_trend_change_is_bounded(self):
        series = pd.Series(
            [100.0, 120.0, 90.0, 130.0, 80.0, 140.0, 100.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        valid = (
            result["trend_change"]
            .dropna()
        )

        assert valid.ge(-1.0).all()
        assert valid.le(1.0).all()

    def test_new_maximum_has_zero_drawdown(self):
        series = pd.Series(
            [100.0, 110.0, 105.0, 120.0, 115.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        running_max = series.cummax()

        mask = (
            series == running_max
        )

        assert (
            result.loc[mask, "drawdown"]
            .eq(0.0)
            .all()
        )