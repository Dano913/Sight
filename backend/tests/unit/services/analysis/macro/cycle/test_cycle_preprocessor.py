from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd
import pytest

from app.services.analysis.cycle.cycle_preprocessor import (
    CyclePreprocessor,
)


@dataclass
class Observation:
    date: date
    value: float


class TestPrepareSeries:

    def test_returns_sorted_dates_values_and_frequency(
        self,
    ):
        observations = [
            Observation(date(2022, 1, 1), 120.0),
            Observation(date(2020, 1, 1), 100.0),
            Observation(date(2021, 1, 1), 110.0),
        ]

        dates, values, observations_per_year, use_log = (
            CyclePreprocessor.prepare_series(
                observations
            )
        )

        assert list(dates) == [
            np.datetime64("2020-01-01"),
            np.datetime64("2021-01-01"),
            np.datetime64("2022-01-01"),
        ]

        assert np.allclose(
            values,
            [100.0, 110.0, 120.0],
        )

        assert observations_per_year == 1

    def test_raises_for_empty_observations(
        self,
    ):
        with pytest.raises(
            ValueError,
            match="No hay observaciones",
        ):
            CyclePreprocessor.prepare_series([])

    def test_removes_non_finite_values(
        self,
    ):
        observations = [
            Observation(date(2020, 1, 1), 100.0),
            Observation(date(2020, 4, 1), float("nan")),
            Observation(date(2020, 7, 1), 120.0),
            Observation(date(2020, 10, 1), 130.0),
        ]

        dates, values, observations_per_year, use_log = (
            CyclePreprocessor.prepare_series(
                observations
            )
        )

        assert len(values) == 3

        assert np.allclose(
            values,
            [100.0, 120.0, 130.0],
        )

        assert observations_per_year == 4

    def test_removes_infinite_values(
        self,
    ):
        observations = [
            Observation(date(2020, 1, 1), 100.0),
            Observation(date(2020, 4, 1), float("inf")),
            Observation(date(2020, 7, 1), 120.0),
            Observation(date(2020, 10, 1), 130.0),
        ]

        dates, values, observations_per_year, use_log = (
            CyclePreprocessor.prepare_series(
                observations
            )
        )

        assert len(values) == 3

        assert np.allclose(
            values,
            [100.0, 120.0, 130.0],
        )

        assert observations_per_year == 4

    def test_preserves_non_positive_values(
        self,
    ):
        observations = [
            Observation(date(2020, 1, 1), 100.0),
            Observation(date(2020, 4, 1), 0.0),
            Observation(date(2020, 7, 1), 120.0),
            Observation(date(2020, 10, 1), 130.0),
        ]

        dates, values, observations_per_year, use_log = (
            CyclePreprocessor.prepare_series(
                observations
            )
        )

        assert len(values) == 4

        assert np.allclose(
            values,
            [100.0, 0.0, 120.0, 130.0],
        )

        assert observations_per_year == 4

        assert use_log is False

    def test_raises_when_fewer_than_two_valid_values(
        self,
    ):
        observations = [
            Observation(date(2020, 1, 1), 100.0),
        ]

        with pytest.raises(
            ValueError,
            match="al menos dos observaciones",
        ):
            CyclePreprocessor.prepare_series(
                observations
            )


class TestInferObservationsPerYear:

    def test_detects_annual_frequency(
        self,
    ):
        dates = pd.to_datetime(
            [
                "2020-01-01",
                "2021-01-01",
                "2022-01-01",
                "2023-01-01",
            ]
        )

        result = (
            CyclePreprocessor.infer_observations_per_year(
                dates
            )
        )

        assert result == 1

    def test_detects_quarterly_frequency(
        self,
    ):
        dates = pd.to_datetime(
            [
                "2020-01-01",
                "2020-04-01",
                "2020-07-01",
                "2020-10-01",
                "2021-01-01",
            ]
        )

        result = (
            CyclePreprocessor.infer_observations_per_year(
                dates
            )
        )

        assert result == 4

    def test_detects_monthly_frequency(
        self,
    ):
        dates = pd.to_datetime(
            [
                "2020-01-01",
                "2020-02-01",
                "2020-03-01",
                "2020-04-01",
                "2020-05-01",
            ]
        )

        result = (
            CyclePreprocessor.infer_observations_per_year(
                dates
            )
        )

        assert result == 12

    def test_raises_for_insufficient_dates(
        self,
    ):
        dates = pd.to_datetime(
            ["2020-01-01"]
        )

        with pytest.raises(
            ValueError,
            match="al menos dos fechas",
        ):
            CyclePreprocessor.infer_observations_per_year(
                dates
            )


class TestLogGrowth:

    def test_calculates_logarithmic_growth(
        self,
    ):
        values = np.array(
            [100.0, 110.0, 121.0]
        )

        result = CyclePreprocessor.log_growth(
            values
        )

        expected = np.diff(
            np.log(values)
        )

        assert np.allclose(
            result,
            expected,
        )

    def test_raises_for_non_positive_values(
        self,
    ):
        values = np.array(
            [100.0, 0.0, 120.0]
        )

        with pytest.raises(
            ValueError,
            match="valores positivos",
        ):
            CyclePreprocessor.log_growth(
                values
            )

    def test_raises_for_non_finite_values(
        self,
    ):
        values = np.array(
            [100.0, np.nan, 120.0]
        )

        with pytest.raises(
            ValueError,
            match="valores no finitos",
        ):
            CyclePreprocessor.log_growth(
                values
            )


class TestLinearDetrend:

    def test_returns_same_length_as_input(
        self,
    ):
        values = np.array(
            [100.0, 110.0, 121.0, 133.1, 146.41]
        )

        result = CyclePreprocessor.linear_detrend(
            values,
            use_log=False,
        )

        assert len(result) == len(values)

    def test_removes_linear_log_trend(
        self,
    ):
        values = np.exp(
            np.array(
                [1.0, 1.1, 1.2, 1.3, 1.4]
            )
        )

        result = CyclePreprocessor.linear_detrend(
            values,
            use_log=True,
        )

        assert np.allclose(
            result,
            0.0,
            atol=1e-10,
        )


class TestHPFilter:

    def test_returns_trend_cycle_and_resolved_lambda(
        self,
    ):
        values = np.array(
            [
                100.0,
                105.0,
                110.0,
                108.0,
                115.0,
                120.0,
            ]
        )

        trend, cycle, resolved_lambda = (
            CyclePreprocessor.hp_filter(
                values,
                observations_per_year=1,
            )
        )

        assert len(trend) == len(values)
        assert len(cycle) == len(values)
        assert resolved_lambda == 100.0

    def test_uses_default_lambda_for_quarterly_data(
        self,
    ):
        values = np.array(
            [
                100.0,
                105.0,
                110.0,
                108.0,
                115.0,
                120.0,
            ]
        )

        trend, cycle, resolved_lambda = (
            CyclePreprocessor.hp_filter(
                values,
                observations_per_year=4,
            )
        )

        assert resolved_lambda == 1600.0

    def test_uses_default_lambda_for_monthly_data(
        self,
    ):
        values = np.array(
            [
                100.0,
                101.0,
                102.0,
                103.0,
                104.0,
                105.0,
            ]
        )

        trend, cycle, resolved_lambda = (
            CyclePreprocessor.hp_filter(
                values,
                observations_per_year=12,
            )
        )

        assert resolved_lambda == 129600.0

    def test_preserves_explicit_lambda(
        self,
    ):
        values = np.array(
            [
                100.0,
                105.0,
                110.0,
                108.0,
                115.0,
                120.0,
            ]
        )

        trend, cycle, resolved_lambda = (
            CyclePreprocessor.hp_filter(
                values,
                lamb=250.0,
            )
        )

        assert resolved_lambda == 250.0

    def test_trend_plus_cycle_equals_log_values(
        self,
    ):
        values = np.array(
            [
                100.0,
                105.0,
                110.0,
                108.0,
                115.0,
                120.0,
            ]
        )

        trend, cycle, resolved_lambda = (
            CyclePreprocessor.hp_filter(
                values,
                observations_per_year=1,
            )
        )

        assert np.allclose(
            trend + cycle,
            np.log(values),
        )

    def test_raises_for_missing_lambda_and_frequency(
        self,
    ):
        values = np.array(
            [
                100.0,
                105.0,
                110.0,
                108.0,
                115.0,
                120.0,
            ]
        )

        with pytest.raises(
            ValueError,
            match="Debe indicarse `lamb` o `observations_per_year`",
        ):
            CyclePreprocessor.hp_filter(
                values
            )

    def test_raises_for_unsupported_frequency(
        self,
    ):
        values = np.array(
            [
                100.0,
                105.0,
                110.0,
                108.0,
                115.0,
                120.0,
            ]
        )

        with pytest.raises(
            ValueError,
            match="No existe un lambda HP estándar",
        ):
            CyclePreprocessor.hp_filter(
                values,
                observations_per_year=2,
            )

    def test_raises_for_too_short_series(
        self,
    ):
        values = np.array(
            [100.0, 105.0, 110.0]
        )

        with pytest.raises(
            ValueError,
            match="suficientes observaciones",
        ):
            CyclePreprocessor.hp_filter(
                values,
                observations_per_year=1,
            )