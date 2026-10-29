from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.features.volatility_features import volatility_features


class TestVolatilityFeatures:

    def test_returns_all_volatility_features(self):
        series = pd.Series(
            [100.0, 110.0, 100.0, 120.0, 115.0, 130.0]
        )

        result = volatility_features(
            series,
            window=3,
        )

        expected_columns = [
            "rolling_std",
            "rolling_volatility",
            "rolling_range",
            "volatility_change",
            "volatility_zscore",
        ]

        assert list(result.columns) == expected_columns

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=6,
            freq="YS",
        )

        series = pd.Series(
            [100.0, 110.0, 100.0, 120.0, 115.0, 130.0],
            index=index,
        )

        result = volatility_features(
            series,
            window=3,
        )

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )

    def test_preserves_length(self):
        series = pd.Series(
            [100.0, 110.0, 100.0, 120.0, 115.0, 130.0]
        )

        result = volatility_features(
            series,
            window=3,
        )

        assert len(result) == len(series)

    def test_rolling_std(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0]
        )

        result = volatility_features(
            series,
            window=3,
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
            result["rolling_std"],
            expected,
            check_names=False,
        )

    def test_rolling_range(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 100.0]
        )

        result = volatility_features(
            series,
            window=3,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                20.0,
                20.0,
            ]
        )

        pd.testing.assert_series_equal(
            result["rolling_range"],
            expected,
            check_names=False,
        )

    def test_rolling_volatility_is_calculated(self):
        series = pd.Series(
            [100.0, 110.0, 100.0, 120.0, 115.0]
        )

        result = volatility_features(
            series,
            window=3,
        )

        assert result["rolling_volatility"].notna().any()

    def test_volatility_change(self):
        series = pd.Series(
            [100.0, 110.0, 100.0, 120.0, 115.0, 130.0]
        )

        result = volatility_features(
            series,
            window=3,
        )

        expected = result["rolling_volatility"].diff()

        pd.testing.assert_series_equal(
            result["volatility_change"],
            expected,
            check_names=False,
        )

    def test_volatility_zscore_is_based_on_volatility(self):
        series = pd.Series(
            [100.0, 110.0, 100.0, 120.0, 115.0, 130.0, 125.0]
        )

        result = volatility_features(
            series,
            window=3,
        )

        volatility = result["rolling_volatility"]

        expected = (
            volatility
            - volatility.rolling(3).mean()
        ) / volatility.rolling(3).std()

        pd.testing.assert_series_equal(
            result["volatility_zscore"],
            expected,
            check_names=False,
        )