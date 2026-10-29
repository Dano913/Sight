from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.services.features.feature_engine import FeatureEngine


class TestFeatureEngine:

    def test_returns_dataframe(self):
        series = pd.Series(
            np.linspace(100.0, 150.0, 24)
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="monthly",
        )

        assert isinstance(result, pd.DataFrame)

    def test_returns_all_feature_families(self):
        series = pd.Series(
            np.linspace(100.0, 150.0, 24)
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="monthly",
        )

        expected_columns = {
            # Level
            "value",
            "rolling_mean",
            "rolling_median",
            "rolling_min",
            "rolling_max",
            "rolling_percentile",
            "rolling_zscore",
            "distance_from_rolling_mean",

            # Growth
            "log_difference",
            "percentage_change",
            "cumulative_growth",
            "momentum",
            "yoy_growth",
            "yoy_log_growth",

            # Trend
            "rolling_slope_short",
            "rolling_slope_medium",
            "rolling_slope_long",
            "acceleration",
            "slope_change",
            "trend_change",

            # Volatility
            "rolling_std",
            "rolling_volatility",
            "rolling_range",
            "volatility_change",
            "volatility_zscore",

            # Extreme
            "zscore",
            "percentile",
            "distance_from_max",
            "distance_from_min",
            "drawdown",
        }

        assert set(result.columns) == expected_columns

    def test_preserves_index(self):
        index = pd.date_range(
            "2010-01-01",
            periods=24,
            freq="MS",
        )

        series = pd.Series(
            np.linspace(100.0, 150.0, 24),
            index=index,
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="monthly",
        )

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )

    def test_preserves_length(self):
        series = pd.Series(
            np.linspace(100.0, 150.0, 24)
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="monthly",
        )

        assert len(result) == len(series)

    def test_contains_original_values(self):
        series = pd.Series(
            np.linspace(100.0, 150.0, 24)
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="monthly",
        )

        pd.testing.assert_series_equal(
            result["value"],
            series,
            check_names=False,
        )

    def test_respects_custom_windows(self):
        series = pd.Series(
            np.linspace(100.0, 150.0, 30)
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="monthly",
            level_window=3,
            trend_short_window=3,
            trend_medium_window=5,
            trend_long_window=8,
            volatility_window=4,
            extreme_window=5,
        )

        assert result["rolling_mean"].iloc[2] == pytest.approx(
            series.iloc[:3].mean()
        )

        assert pd.isna(
            result["rolling_mean"].iloc[1]
        )

        assert pd.isna(
            result["rolling_slope_long"].iloc[6]
        )

        assert not pd.isna(
            result["rolling_slope_long"].iloc[7]
        )

    def test_different_frequencies_are_supported(self):
        series = pd.Series(
            np.linspace(100.0, 150.0, 24)
        )

        for frequency in (
            "monthly",
            "quarterly",
            "annual",
        ):
            result = FeatureEngine.compute(
                series=series,
                frequency=frequency,
            )

            assert isinstance(
                result,
                pd.DataFrame,
            )

            assert len(result) == len(series)

    def test_invalid_frequency_is_rejected(self):
        series = pd.Series(
            np.linspace(100.0, 150.0, 24)
        )

        with pytest.raises(ValueError):
            FeatureEngine.compute(
                series=series,
                frequency="weekly",
            )

    def test_feature_families_do_not_modify_input(self):
        series = pd.Series(
            np.linspace(100.0, 150.0, 24)
        )

        original = series.copy()

        FeatureEngine.compute(
            series=series,
            frequency="monthly",
        )

        pd.testing.assert_series_equal(
            series,
            original,
        )