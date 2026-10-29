from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.services.features.utils.transformations import (
    log_difference,
    percentage_change,
    cumulative_growth,
)


class TestLogDifference:

    def test_basic_log_difference(self):
        series = pd.Series([100.0, 110.0, 121.0])

        result = log_difference(series)

        expected = pd.Series(
            [
                np.nan,
                np.log(110 / 100),
                np.log(121 / 110),
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_log_difference_with_periods(self):
        series = pd.Series([100.0, 110.0, 121.0, 133.1])

        result = log_difference(
            series,
            periods=2,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                np.log(121 / 100),
                np.log(133.1 / 110),
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_log_difference_constant_series(self):
        series = pd.Series([100.0, 100.0, 100.0])

        result = log_difference(series)

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

    def test_log_difference_rejects_non_positive_values(self):
        series = pd.Series([100.0, 0.0, 110.0])

        with pytest.raises(ValueError):
            log_difference(series)


class TestPercentageChange:

    def test_basic_percentage_change(self):
        series = pd.Series([100.0, 110.0, 121.0])

        result = percentage_change(series)

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

    def test_percentage_change_with_periods(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        result = percentage_change(
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

    def test_percentage_change_decrease(self):
        series = pd.Series([100.0, 90.0])

        result = percentage_change(series)

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

    def test_percentage_change_constant_series(self):
        series = pd.Series([100.0, 100.0, 100.0])

        result = percentage_change(series)

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


class TestCumulativeGrowth:

    def test_basic_cumulative_growth(self):
        series = pd.Series(
            [100.0, 110.0, 121.0]
        )

        result = cumulative_growth(
            series,
            periods=1,
        )

        expected = pd.Series(
            [
                np.nan,
                0.10,
                0.21,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_cumulative_growth_with_periods(self):
        series = pd.Series(
            [
                100.0,
                110.0,
                121.0,
                133.1,
            ]
        )

        result = cumulative_growth(
            series,
            periods=2,
        )

        expected = pd.Series(
            [
                np.nan,
                np.nan,
                0.21,
                0.331,
            ]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_cumulative_growth_constant_series(self):
        series = pd.Series(
            [100.0, 100.0, 100.0]
        )

        result = cumulative_growth(
            series,
            periods=1,
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


class TestTransformationsProperties:

    def test_output_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=3,
            freq="YS",
        )

        series = pd.Series(
            [100.0, 110.0, 121.0],
            index=index,
        )

        result = percentage_change(series)

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )

    def test_output_has_same_length(self):
        series = pd.Series(
            [100.0, 110.0, 121.0, 133.1]
        )

        for function in (
            log_difference,
            percentage_change,
        ):
            result = function(series)

            assert len(result) == len(series)