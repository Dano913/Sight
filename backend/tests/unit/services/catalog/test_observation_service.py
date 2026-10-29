from __future__ import annotations

import pytest

from app.models.observation import Observation
from app.services.catalog.observation_service import ObservationService


class TestObservationService:

    def test_unsupported_indicator_raises_value_error(self):
        with pytest.raises(ValueError, match="Indicador no soportado: UNKNOWN_IND"):
            ObservationService.get_observations("UNKNOWN_IND")

    def test_cached_read_delegates_to_repository(self, monkeypatch):
        called = {}

        monkeypatch.setattr(
            "app.services.catalog.observation_service.ObservationRepository.exists",
            lambda indicator_code, region_code: True,
        )

        def fake_get_by_region_and_indicator(region_code, indicator_code):
            called["region"] = region_code
            called["indicator"] = indicator_code
            return ["fake_obs"]

        monkeypatch.setattr(
            "app.services.catalog.observation_service.ObservationRepository.get_by_region_and_indicator",
            fake_get_by_region_and_indicator,
        )

        result = ObservationService.get_observations("GDP", region_code="US")

        assert result == ["fake_obs"]
        assert called["region"] == "US"
        assert called["indicator"] == "GDP"
