from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.features.utils.statistics import (
    zscore,
    percentile,
)


class TestZscore:

    def test_basic_zscore(self):
        series = pd.Series([1.0, 2.0, 3.0])

        result = zscore(series)

        expected = (
            series - series.mean()
        ) / series.std()

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_constant_series(self):
        series = pd.Series([5.0, 5.0, 5.0])

        result = zscore(series)

        expected = pd.Series(
            [0.0, 0.0, 0.0]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=3,
            freq="YS",
        )

        series = pd.Series(
            [1.0, 2.0, 3.0],
            index=index,
        )

        result = zscore(series)

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )

    def test_output_has_same_length(self):
        series = pd.Series(
            [1.0, 2.0, 3.0, 4.0]
        )

        result = zscore(series)

        assert len(result) == len(series)


class TestPercentile:

    def test_basic_percentile(self):
        series = pd.Series(
            [10.0, 20.0, 30.0, 40.0]
        )

        result = percentile(series)

        expected = pd.Series(
            [0.25, 0.50, 0.75, 1.00]
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

        result = percentile(series)

        expected = pd.Series(
            [
                2 / 3,
                2 / 3,
                2 / 3,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_ties_use_average_rank(self):
        series = pd.Series(
            [10.0, 10.0, 20.0]
        )

        result = percentile(series)

        expected = pd.Series(
            [
                0.5,
                0.5,
                1.0,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=3,
            freq="YS",
        )

        series = pd.Series(
            [10.0, 20.0, 30.0],
            index=index,
        )

        result = percentile(series)

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )

    def test_output_has_same_length(self):
        series = pd.Series(
            [10.0, 20.0, 30.0, 40.0]
        )

        result = percentile(series)

        assert len(result) == len(series)