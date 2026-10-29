from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.services.features.utils.validation import (
    validate_frequency,
    periods_per_year,
    prepare_series,
)


class TestValidateFrequency:

    def test_valid_frequencies(self):
        for frequency in (
            "monthly",
            "quarterly",
            "annual",
        ):
            assert validate_frequency(frequency) is None

    def test_invalid_frequency(self):
        with pytest.raises(ValueError):
            validate_frequency("weekly")

    def test_invalid_frequency_empty(self):
        with pytest.raises(ValueError):
            validate_frequency("")


class TestPeriodsPerYear:

    def test_monthly(self):
        assert periods_per_year("monthly") == 12

    def test_quarterly(self):
        assert periods_per_year("quarterly") == 4

    def test_annual(self):
        assert periods_per_year("annual") == 1

    def test_invalid_frequency(self):
        with pytest.raises(ValueError):
            periods_per_year("weekly")


class TestPrepareSeries:

    def test_rejects_non_series(self):
        with pytest.raises(TypeError):
            prepare_series([1, 2, 3])

    def test_converts_numeric_values(self):
        series = pd.Series(
            ["100", "110", "120"]
        )

        result = prepare_series(series)

        expected = pd.Series(
            [100.0, 110.0, 120.0]
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_removes_invalid_numeric_values(self):
        series = pd.Series(
            [100.0, "invalid", 110.0]
        )

        result = prepare_series(series)

        expected = pd.Series(
            [100.0, 110.0],
            index=[0, 2],
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_removes_nan(self):
        series = pd.Series(
            [100.0, np.nan, 110.0]
        )

        result = prepare_series(series)

        expected = pd.Series(
            [100.0, 110.0],
            index=[0, 2],
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_removes_infinity(self):
        series = pd.Series(
            [100.0, np.inf, -np.inf, 110.0]
        )

        result = prepare_series(series)

        expected = pd.Series(
            [100.0, 110.0],
            index=[0, 3],
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_sorts_index(self):
        index = pd.to_datetime(
            [
                "2022-01-01",
                "2020-01-01",
                "2021-01-01",
            ]
        )

        series = pd.Series(
            [120.0, 100.0, 110.0],
            index=index,
        )

        result = prepare_series(series)

        expected_index = pd.to_datetime(
            [
                "2020-01-01",
                "2021-01-01",
                "2022-01-01",
            ]
        )

        expected = pd.Series(
            [100.0, 110.0, 120.0],
            index=expected_index,
        )

        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False,
        )

    def test_does_not_modify_original_series(self):
        series = pd.Series(
            [120.0, 100.0, 110.0]
        )

        original = series.copy()

        prepare_series(series)

        pd.testing.assert_series_equal(
            series,
            original,
        )

    def test_empty_after_cleaning(self):
        series = pd.Series(
            [np.nan, np.inf, -np.inf]
        )

        with pytest.raises(ValueError):
            prepare_series(series)

    def test_require_positive_accepts_positive_values(self):
        series = pd.Series(
            [100.0, 110.0, 120.0]
        )

        result = prepare_series(
            series,
            require_positive=True,
        )

        pd.testing.assert_series_equal(
            result,
            series,
        )

    def test_require_positive_rejects_zero(self):
        series = pd.Series(
            [100.0, 0.0, 120.0]
        )

        with pytest.raises(ValueError):
            prepare_series(
                series,
                require_positive=True,
            )

    def test_require_positive_rejects_negative(self):
        series = pd.Series(
            [100.0, -10.0, 120.0]
        )

        with pytest.raises(ValueError):
            prepare_series(
                series,
                require_positive=True,
            )

    def test_preserves_index(self):
        index = pd.date_range(
            "2020-01-01",
            periods=3,
            freq="YS",
        )

        series = pd.Series(
            [100.0, 110.0, 120.0],
            index=index,
        )

        result = prepare_series(series)

        pd.testing.assert_index_equal(
            result.index,
            series.index,
        )