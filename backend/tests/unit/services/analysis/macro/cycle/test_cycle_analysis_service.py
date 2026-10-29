from __future__ import annotations

from datetime import date

from app.services.analysis.cycle.cycle_analysis_service import (
    CycleAnalysisService,
)


def make_observation(year, value):
    return type(
        "Observation",
        (),
        {
            "date": date(year, 1, 1),
            "value": value,
        },
    )()


class TestCycleAnalysisService:

    def test_analyze_returns_expected_structure(
        self,
    ):
        observations = [
            make_observation(
                year,
                100 + year - 2000,
            )
            for year in range(2000, 2015)
        ]

        result = CycleAnalysisService.analyze(
            observations
        )

        assert result["observations"] == 15
        assert result["growth_observations"] == 14
        assert "growth" in result
        assert "linear_detrend" in result
        assert "hp" in result
        assert "robust_cycles" in result

    def test_returns_date_range(
        self,
    ):
        observations = [
            make_observation(
                year,
                100 + year - 2000,
            )
            for year in range(2000, 2010)
        ]

        result = CycleAnalysisService.analyze(
            observations
        )

        assert result["start_date"] == "2000-01-01"
        assert result["end_date"] == "2009-01-01"

    def test_respects_top_n(
        self,
    ):
        observations = [
            make_observation(
                year,
                100 + year - 2000,
            )
            for year in range(1980, 2025)
        ]

        result = CycleAnalysisService.analyze(
            observations,
            top_n=2,
        )

        assert len(
            result["growth"]["dominant_periods"]
        ) <= 2

        assert len(
            result["linear_detrend"]["dominant_periods"]
        ) <= 2

        assert len(
            result["hp"]["dominant_periods"]
        ) <= 2

    def test_hp_lambda_is_preserved(
        self,
    ):
        observations = [
            make_observation(
                year,
                100 + year - 2000,
            )
            for year in range(2000, 2015)
        ]

        result = CycleAnalysisService.analyze(
            observations,
            hp_lambda=250.0,
        )

        assert result["hp"]["lambda"] == 250.0

    def test_hp_lambda_uses_default_for_annual_data(
        self,
    ):
        observations = [
            make_observation(
                year,
                100 + year - 2000,
            )
            for year in range(2000, 2015)
        ]

        result = CycleAnalysisService.analyze(
            observations
        )

        assert result["observations_per_year"] == 1
        assert result["hp"]["lambda"] == 100.0