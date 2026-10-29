from __future__ import annotations

import sqlite3
from datetime import date
import pytest

from app.models.observation import Observation
from app.repositories.observation_repository import ObservationRepository
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.region_service import RegionService
from app.services.catalog.source_service import SourceService


@pytest.fixture
def test_db(monkeypatch):
    conn = sqlite3.connect(":memory:")

    # Monkeypatch get_connection to return this connection (keeping it open)
    # Since repository closes connections, we use a wrapper or connection provider
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
            pass  # Don't close memory db across calls

    monkeypatch.setattr(
        "app.repositories.observation_repository.get_connection",
        lambda: MockConnectionWrapper(conn),
    )

    ObservationRepository.create_table()
    yield conn
    conn.close()


class TestObservationRepository:

    def _sample_obs(self, region_code: str, indicator_code: str, date_str: str, value: float):
        return Observation(
            region=RegionService.get_region(region_code),
            indicator=IndicatorService.get_indicator(indicator_code),
            source=SourceService.get_by_code("FRED"),
            date=date.fromisoformat(date_str),
            value=value,
        )

    def test_create_table_and_indexes(self, test_db):
        cursor = test_db.cursor()
        cursor.execute("PRAGMA index_list(observations)")
        index_names = [row[1] for row in cursor.fetchall()]
        assert "idx_observations_indicator_region" in index_names
        assert "idx_observations_region_indicator" in index_names
        assert "idx_observations_indicator" in index_names

    def test_save_and_exists(self, test_db):
        obs1 = self._sample_obs("US", "GDP", "2020-01-01", 100.0)
        obs2 = self._sample_obs("US", "GDP", "2020-04-01", 102.0)

        assert not ObservationRepository.exists("GDP")
        assert not ObservationRepository.exists("GDP", "US")

        ObservationRepository.save_observations([obs1, obs2])

        assert ObservationRepository.exists("GDP")
        assert ObservationRepository.exists("gdp")  # Case insensitive
        assert ObservationRepository.exists("GDP", "US")
        assert ObservationRepository.exists("gdp", "us")
        assert not ObservationRepository.exists("GDP", "ES")

    def test_get_by_region_and_indicator(self, test_db):
        obs_us = self._sample_obs("US", "GDP", "2020-01-01", 100.0)
        obs_es = self._sample_obs("ES", "GDP", "2020-01-01", 50.0)
        ObservationRepository.save_observations([obs_us, obs_es])

        res_us = ObservationRepository.get_by_region_and_indicator("us", "gdp")
        assert len(res_us) == 1
        assert res_us[0].region.code == "US"
        assert res_us[0].value == 100.0

        res_es = ObservationRepository.get_by_region_and_indicator("ES", "GDP")
        assert len(res_es) == 1
        assert res_es[0].region.code == "ES"
        assert res_es[0].value == 50.0

    def test_replace_batch(self, test_db):
        obs_old = self._sample_obs("US", "GDP", "2020-01-01", 100.0)
        ObservationRepository.save_observations([obs_old])

        obs_new1 = self._sample_obs("US", "GDP", "2020-01-01", 105.0)
        obs_new2 = self._sample_obs("ES", "INFLATION", "2020-01-01", 2.5)

        batch = {
            ("US", "GDP", "FRED"): [obs_new1],
            ("ES", "INFLATION", "FRED"): [obs_new2],
        }

        ObservationRepository.replace_batch(batch)

        us_gdp = ObservationRepository.get_by_region_and_indicator("US", "GDP")
        assert len(us_gdp) == 1
        assert us_gdp[0].value == 105.0

        es_inf = ObservationRepository.get_by_region_and_indicator("ES", "INFLATION")
        assert len(es_inf) == 1
        assert es_inf[0].value == 2.5
