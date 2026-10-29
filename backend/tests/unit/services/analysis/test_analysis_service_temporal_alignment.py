from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest

from app.models.enums import Frequency, GrowthMethod
from app.services.analysis.analysis_service import AnalysisService


def make_obs(
    indicator_code: str,
    obs_date: date,
    value: float,
    region_code: str = "US",
    source_code: str = "FRED",
):
    return SimpleNamespace(
        indicator=SimpleNamespace(
            id=indicator_code,
            code=indicator_code,
            frequency=Frequency.MONTHLY,
            growth_method=GrowthMethod.RATE,
        ),
        region=SimpleNamespace(code=region_code),
        source=SimpleNamespace(code=source_code),
        date=obs_date,
        value=value,
    )


class TestAnalysisServiceTemporalAlignment:

    def test_basic_temporal_alignment(self):
        gdp_obs = [
            make_obs("GDP", date(2020 + (i // 12), 1 + (i % 12), 1), 100.0 + i)
            for i in range(25)
        ]
        unemp_obs = [
            make_obs("UNEMPLOYMENT", date(2020 + (i // 12), 1 + (i % 12), 1), 5.0 - (i * 0.1))
            for i in range(25)
        ]

        result = AnalysisService.analyze_multiple(gdp_obs + unemp_obs)

        alignment = result["temporal_alignment"]
        assert alignment["reference_date"] == "2022-01-01"
        assert alignment["as_of_date"] is None
        assert alignment["max_lag_days"] == 180
        assert alignment["active_indicators"] == ["GDP", "UNEMPLOYMENT"]
        assert alignment["stale_indicators"] == []
        assert alignment["indicator_lags_days"]["GDP"] == 0
        assert alignment["indicator_lags_days"]["UNEMPLOYMENT"] == 0
        assert result["indicators_active"] == ["GDP", "UNEMPLOYMENT"]

    def test_stale_indicator_is_segregated_and_excluded_from_voting(self):
        # GDP termina en 2020-01-01 (hace más de 700 días)
        gdp_obs = [
            make_obs("GDP", date(2018 + (i // 12), 1 + (i % 12), 1), 100.0 + i)
            for i in range(25)
        ]
        # UNEMPLOYMENT termina en 2022-01-01 (fecha de referencia)
        unemp_obs = [
            make_obs("UNEMPLOYMENT", date(2020 + (i // 12), 1 + (i % 12), 1), 5.0 - (i * 0.1))
            for i in range(25)
        ]

        result = AnalysisService.analyze_multiple(
            gdp_obs + unemp_obs,
            max_lag_days=180,
        )

        alignment = result["temporal_alignment"]
        assert alignment["reference_date"] == "2022-01-01"
        assert "GDP" in alignment["stale_indicators"]
        assert alignment["active_indicators"] == ["UNEMPLOYMENT"]
        assert alignment["indicator_lags_days"]["GDP"] > 180
        assert alignment["indicator_lags_days"]["UNEMPLOYMENT"] == 0

        # GDP sigue presente en "indicators" para diagnóstico, pero no vota
        assert "GDP" in result["indicators"]
        assert result["indicators_active"] == ["UNEMPLOYMENT"]
        # En el régimen macro sólo se usó UNEMPLOYMENT
        assert result["macro_regime"]["indicators_used"] == ["UNEMPLOYMENT"]

    def test_as_of_date_point_in_time_filtering(self):
        obs = [
            make_obs("UNEMPLOYMENT", date(2020 + (i // 12), 1 + (i % 12), 1), 5.0 - (i * 0.1))
            for i in range(36)
        ]

        result = AnalysisService.analyze_multiple(
            obs,
            as_of_date="2021-06-01",
        )

        alignment = result["temporal_alignment"]
        assert alignment["as_of_date"] == "2021-06-01"
        assert alignment["reference_date"] == "2021-06-01"
        assert result["date"] == "2021-06-01"

    def test_as_of_date_before_any_observation_raises_error(self):
        obs = [
            make_obs("GDP", date(2020 + (i // 12), 1 + (i % 12), 1), 100.0 + i)
            for i in range(25)
        ]

        with pytest.raises(ValueError, match="No hay observaciones disponibles"):
            AnalysisService.analyze_multiple(obs, as_of_date="1990-01-01")

    def test_multiple_regions_raises_error(self):
        obs_us = [
            make_obs("GDP", date(2020, 1, 1), 100.0, region_code="US"),
            make_obs("GDP", date(2020, 2, 1), 101.0, region_code="US"),
        ]
        obs_eu = [
            make_obs("GDP", date(2020, 1, 1), 100.0, region_code="EU"),
            make_obs("GDP", date(2020, 2, 1), 101.0, region_code="EU"),
        ]

        with pytest.raises(ValueError, match="misma región"):
            AnalysisService.analyze_multiple(obs_us + obs_eu)

    def test_max_lag_days_none_disables_staleness_filter(self):
        gdp_obs = [
            make_obs("GDP", date(2018 + (i // 12), 1 + (i % 12), 1), 100.0 + i)
            for i in range(25)
        ]
        unemp_obs = [
            make_obs("UNEMPLOYMENT", date(2020 + (i // 12), 1 + (i % 12), 1), 5.0 - (i * 0.1))
            for i in range(25)
        ]

        result = AnalysisService.analyze_multiple(
            gdp_obs + unemp_obs,
            max_lag_days=None,
        )

        alignment = result["temporal_alignment"]
        assert alignment["max_lag_days"] is None
        assert alignment["stale_indicators"] == []
        assert set(alignment["active_indicators"]) == {"GDP", "UNEMPLOYMENT"}

    def test_analyze_includes_investment_analysis_synthesis(self):
        gdp_obs = [
            make_obs("GDP", date(2020 + (i // 12), 1 + (i % 12), 1), 100.0 + i)
            for i in range(25)
        ]

        result = AnalysisService.analyze(gdp_obs)

        assert "investment_interpretation" in result
        assert "investment_analysis" in result
        thesis = result["investment_analysis"]
        assert "macro_bias" in thesis
        assert "conviction" in thesis
        assert "horizon" in thesis
        assert "alerts" in thesis
        assert "overall" in thesis
        assert "assessment" in thesis["overall"]
        assert "direction" in thesis["overall"]
