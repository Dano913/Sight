from __future__ import annotations

import numpy as np

from app.services.analysis.cycle.cycle_signal_analyzer import (
    CycleSignalAnalyzer,
)


class TestAutocorrelation:

    def test_returns_empty_for_short_series(self):
        result = CycleSignalAnalyzer.autocorrelation(
            np.array([1.0, 2.0])
        )

        assert result == []

    def test_returns_empty_for_constant_series(self):
        result = CycleSignalAnalyzer.autocorrelation(
            np.array([5.0, 5.0, 5.0, 5.0])
        )

        assert result == []

    def test_returns_all_available_lags(self):
        series = np.array(
            [1.0, 2.0, 3.0, 4.0, 5.0]
        )

        result = CycleSignalAnalyzer.autocorrelation(
            series
        )

        assert len(result) == len(series) - 1

    def test_first_lag_is_correct(self):
        series = np.array(
            [1.0, 2.0, 3.0, 4.0]
        )

        result = CycleSignalAnalyzer.autocorrelation(
            series
        )

        centered = series - np.mean(series)

        expected = np.dot(
            centered[:-1],
            centered[1:],
        ) / np.dot(
            centered,
            centered,
        )

        assert result[0]["lag"] == 1

        assert np.isclose(
            result[0]["autocorrelation"],
            expected,
        )


class TestPeriodogram:

    def test_returns_empty_for_short_series(self):
        result = CycleSignalAnalyzer.periodogram(
            np.array([1.0, 2.0, 3.0]),
            observations_per_year=1,
        )

        assert result == []

    def test_excludes_zero_frequency(self):
        series = np.sin(
            np.linspace(
                0,
                10 * np.pi,
                100,
            )
        )

        result = CycleSignalAnalyzer.periodogram(
            series,
            observations_per_year=1,
        )

        assert all(
            item["frequency"] > 0
            for item in result
        )

    def test_returns_frequency_period_and_power(self):
        series = np.sin(
            np.linspace(
                0,
                10 * np.pi,
                100,
            )
        )

        result = CycleSignalAnalyzer.periodogram(
            series,
            observations_per_year=1,
        )

        assert result

        for item in result:
            assert "frequency" in item
            assert "period_years" in item
            assert "power" in item
            assert "relative_power" in item

    def test_period_is_inverse_of_frequency(self):
        series = np.sin(
            np.linspace(
                0,
                10 * np.pi,
                100,
            )
        )

        result = CycleSignalAnalyzer.periodogram(
            series,
            observations_per_year=1,
        )

        for item in result:
            assert np.isclose(
                item["period_years"],
                1.0 / item["frequency"],
            )