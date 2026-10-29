from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.services.features.feature_engine import FeatureEngine


class TestFeatureEngineEdgeCases:

    def test_very_short_series(self):
        series = pd.Series(
            [100.0, 101.0, 102.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            level_window=8,
            trend_short_window=4,
            trend_medium_window=8,
            trend_long_window=16,
            volatility_window=8,
            extreme_window=8,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(series)
        assert result.index.equals(series.index)

    def test_nan_values_are_handled(self):
        series = pd.Series(
            [100.0, 102.0, np.nan, 106.0, 108.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(series)
        assert result.index.equals(series.index)

    def test_zero_values_are_rejected(self):
        series = pd.Series(
            [100.0, 90.0, 0.0, 10.0, 20.0]
        )

        with pytest.raises(ValueError):
            FeatureEngine.compute(
                series=series,
                frequency="annual",
                trend_short_window=3,
                trend_medium_window=4,
                trend_long_window=5,
            )

    def test_negative_values(self):
        series = pd.Series(
            [100.0, 90.0, -10.0, -20.0, -30.0]
        )

        with pytest.raises(ValueError):
            FeatureEngine.compute(
                series=series,
                frequency="annual",
                trend_short_window=3,
                trend_medium_window=4,
                trend_long_window=5,
            )

    def test_windows_larger_than_series(self):
        series = pd.Series(
            [100.0, 102.0, 104.0, 106.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            level_window=20,
            trend_short_window=10,
            trend_medium_window=20,
            trend_long_window=30,
            volatility_window=20,
            extreme_window=20,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(series)

        assert result["rolling_mean"].isna().all()
        assert result["rolling_median"].isna().all()
        assert result["rolling_min"].isna().all()
        assert result["rolling_max"].isna().all()

    def test_invalid_frequency(self):
        series = pd.Series(
            [100.0, 102.0, 104.0, 106.0]
        )

        with pytest.raises(ValueError):
            FeatureEngine.compute(
                series=series,
                frequency="weekly",
            )

    def test_constant_series(self):
        series = pd.Series(
            [100.0] * 10
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["percentage_change"].dropna().eq(0).all()

        assert np.allclose(
            result["rolling_slope_short"].dropna(),
            0,
        )

        assert np.allclose(
            result["rolling_slope_medium"].dropna(),
            0,
        )

        assert np.allclose(
            result["rolling_slope_long"].dropna(),
            0,
        )

        assert np.allclose(
            result["acceleration"].dropna(),
            0,
        )

        assert result["drawdown"].dropna().eq(0).all()

    def test_extreme_change(self):
        series = pd.Series(
            [
                100.0,
                101.0,
                1000000.0,
                1000001.0,
                1000002.0,
            ]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(series)

        assert np.isfinite(
            result["percentage_change"].dropna()
        ).all()

    def test_datetime_index_is_preserved(self):
        index = pd.date_range(
            start="2020-01-01",
            periods=10,
            freq="YE",
        )

        series = pd.Series(
            [
                100.0,
                101.0,
                102.0,
                103.0,
                104.0,
                105.0,
                106.0,
                107.0,
                108.0,
                109.0,
            ],
            index=index,
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        assert result.index.equals(index)
        assert isinstance(result.index, pd.DatetimeIndex)

    def test_non_datetime_index_is_preserved(self):
        index = pd.Index(
            ["a", "b", "c", "d", "e"]
        )

        series = pd.Series(
            [100.0, 101.0, 102.0, 103.0, 104.0],
            index=index,
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        assert result.index.equals(index)

    def test_input_series_is_not_modified(self):
        series = pd.Series(
            [100.0, 102.0, 104.0, 106.0, 108.0]
        )

        original = series.copy()

        FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        pd.testing.assert_series_equal(
            series,
            original,
        )