from __future__ import annotations

import sqlite3
from datetime import date
import pytest

from app.cache.query_cache import query_cache
from app.models.observation import Observation
from app.repositories.observation_repository import ObservationRepository
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.query_service import QueryService
from app.services.catalog.region_service import RegionService
from app.services.catalog.source_service import SourceService


@pytest.fixture(autouse=True)
def clean_cache():
    query_cache.clear()
    yield
    query_cache.clear()


@pytest.fixture
def mock_db(monkeypatch):
    conn = sqlite3.connect(":memory:")

    class MockConnectionWrapper:
        def __init__(self, real_conn):
            self.real_conn = real_conn

        def cursor(self):
            return self.real_conn.cursor()

        def commit(self):
            return self.real_conn.commit()

        def rollback(self):
            return self.real_conn.rollback()

        def close(self):
            pass

    monkeypatch.setattr(
        "app.repositories.observation_repository.get_connection",
        lambda: MockConnectionWrapper(conn),
    )

    ObservationRepository.create_table()
    yield conn
    conn.close()


def make_obs(region_code: str, indicator_code: str, date_str: str, value: float, source_code: str = "EUROSTAT"):
    return Observation(
        region=RegionService.get_region(region_code),
        indicator=IndicatorService.get_indicator(indicator_code),
        source=SourceService.get_by_code(source_code),
        date=date.fromisoformat(date_str),
        value=value,
    )


class TestQueryService:

    def test_compare_regions_preserves_eu27_gdp_value(self, mock_db):
        """
        Verifica que el PIB de EU27_2020 NO sea dividido arbitrariamente por 27,
        y que el objeto Observation conserve su valor íntegro.
        """
        obs_eu = make_obs("EU27_2020", "GDP", "2024-01-01", 3000.0)
        obs_de = make_obs("DE", "GDP", "2024-01-01", 900.0)

        ObservationRepository.save_observations([obs_eu, obs_de])

        result = QueryService.compare_regions("GDP", ["EU27_2020", "DE"])

        assert len(result) == 2

        eu_data = next(r for r in result if r.region.code == "EU27_2020")
        assert eu_data.indicators["GDP"][0].value == 3000.0  # NOT 3000 / 27 (111.11)

        de_data = next(r for r in result if r.region.code == "DE")
        assert de_data.indicators["GDP"][0].value == 900.0

    def test_cache_hit_and_clear_cache(self, mock_db):
        obs = make_obs("ES", "GDP", "2024-01-01", 350.0)
        ObservationRepository.save_observations([obs])

        res1 = QueryService.get_by_region_and_indicator("ES", "GDP")
        assert "region_indicator:ES:GDP" in query_cache
        res2 = QueryService.get_by_region_and_indicator("es", "gdp")
        assert res1 == res2

        QueryService.clear_cache()
        assert len(query_cache) == 0

    def test_compute_trade_observations_synthetic(self, monkeypatch):
        """
        Verifica el cálculo de TRADE = EXPORTS - IMPORTS
        """
        exp_obs = [
            make_obs("ES", "EXPORTS", "2024-01-01", 100.0),
            make_obs("ES", "EXPORTS", "2024-02-01", 110.0),
        ]
        imp_obs = [
            make_obs("ES", "IMPORTS", "2024-01-01", 80.0),
            make_obs("ES", "IMPORTS", "2024-02-01", 120.0),
        ]

        def fake_get_obs(indicator_code, region_code=None, refresh=False):
            if indicator_code == "EXPORTS":
                return exp_obs
            elif indicator_code == "IMPORTS":
                return imp_obs
            return []

        monkeypatch.setattr(
            "app.services.catalog.query_service.ObservationService.get_observations",
            fake_get_obs,
        )

        res = QueryService.get_by_region_and_indicator("ES", "TRADE")

        assert res.region.code == "ES"
        trade_points = res.indicators["TRADE"]
        assert len(trade_points) == 2
        assert trade_points[0].date == date(2024, 1, 1)
        assert trade_points[0].value == 20.0  # 100 - 80
        assert trade_points[1].date == date(2024, 2, 1)
        assert trade_points[1].value == -10.0  # 110 - 120

    def test_get_by_indicator_trade(self, monkeypatch):
        exp_obs = [make_obs("ES", "EXPORTS", "2024-01-01", 50.0)]
        imp_obs = [make_obs("ES", "IMPORTS", "2024-01-01", 40.0)]

        monkeypatch.setattr(
            "app.services.catalog.query_service.ObservationService.get_observations",
            lambda indicator_code, region_code=None, refresh=False: (
                exp_obs if indicator_code == "EXPORTS" else imp_obs
            ),
        )

        res = QueryService.get_by_indicator("TRADE")
        assert res.indicator.code == "TRADE"
        assert "ES" in res.regions
        assert res.regions["ES"][0].value == 10.0  # 50 - 40
