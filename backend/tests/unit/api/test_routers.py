from __future__ import annotations

from datetime import date
import pytest
from fastapi import HTTPException

from app.main import app
from app.api.routers import (
    analysis,
    bea,
    bls,
    health,
    indicators,
    investment,
    nbs,
    observations,
    query,
    regions,
    sources,
)
from app.models.observation import Observation
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.region_service import RegionService
from app.services.catalog.source_service import SourceService


def _make_monthly_observations(
    indicator_code: str = "INFLATION",
    region_code: str = "DE",
    source_code: str = "EUROSTAT",
    n: int = 36,
) -> list[Observation]:
    indicator = IndicatorService.get_indicator(indicator_code)
    region = RegionService.get_region(region_code)
    source = SourceService.get_by_code(source_code)

    obs_list = []
    for i in range(n):
        year = 2021 + (i // 12)
        month = (i % 12) + 1
        obs_list.append(
            Observation(
                region=region,
                indicator=indicator,
                source=source,
                date=date(year, month, 1),
                value=100.0 + (i * 0.5) + ((i % 4) * 0.2),
            )
        )
    return obs_list


class TestCatalogAndHealthRouters:

    def test_health(self):
        assert health.health() == {"status": "ok"}

    def test_registered_routes_include_both_slash_and_no_slash(self):
        region_paths = {getattr(r, "path", None) for r in regions.router.routes}
        source_paths = {getattr(r, "path", None) for r in sources.router.routes}
        indicator_paths = {getattr(r, "path", None) for r in indicators.router.routes}

        assert "/regions" in region_paths
        assert "/regions/" in region_paths
        assert "/sources" in source_paths
        assert "/sources/" in source_paths
        assert "/indicators" in indicator_paths
        assert "/indicators/" in indicator_paths

    def test_regions_endpoints(self):
        all_regions = regions.get_regions()
        assert len(all_regions) >= 16

        de = regions.get_region("DE")
        assert de.code == "DE"

        with pytest.raises(HTTPException) as exc:
            regions.get_region("UNKNOWN_REGION")
        assert exc.value.status_code == 404

    def test_sources_endpoints(self):
        all_sources = sources.get_sources()
        assert len(all_sources) >= 5

        eurostat = sources.get_source("EUROSTAT")
        assert eurostat.code == "EUROSTAT"

        with pytest.raises(HTTPException) as exc:
            sources.get_source("UNKNOWN_SOURCE")
        assert exc.value.status_code == 404

    def test_indicators_endpoints(self):
        all_indicators = indicators.get_indicators()
        assert len(all_indicators) >= 11

        gdp = indicators.get_indicator("GDP")
        assert gdp.code == "GDP"

        with pytest.raises(HTTPException) as exc:
            indicators.get_indicator("INVALID_IND")
        assert exc.value.status_code == 404


class TestQueryAndObservationsRouters:

    def test_query_endpoints_return_404_on_value_error(self, monkeypatch):
        def raise_not_found(*args, **kwargs):
            raise ValueError("No existen observaciones")

        monkeypatch.setattr(
            "app.api.routers.query.QueryService.get_by_region",
            raise_not_found,
        )
        monkeypatch.setattr(
            "app.api.routers.query.QueryService.get_by_indicator",
            raise_not_found,
        )
        monkeypatch.setattr(
            "app.api.routers.query.QueryService.get_by_region_and_indicator",
            raise_not_found,
        )

        with pytest.raises(HTTPException) as exc1:
            query.get_by_region("UNKNOWN")
        assert exc1.value.status_code == 404

        with pytest.raises(HTTPException) as exc2:
            query.get_by_indicator("UNKNOWN")
        assert exc2.value.status_code == 404

        with pytest.raises(HTTPException) as exc3:
            query.get_by_region_and_indicator("DE", "UNKNOWN")
        assert exc3.value.status_code == 404

    def test_query_compare_validates_empty_params(self):
        with pytest.raises(HTTPException) as exc:
            query.compare(indicator="GDP", regions=" , ")
        assert exc.value.status_code == 400

    def test_observations_router_supports_trade_and_404(self, monkeypatch):
        trade_obs = _make_monthly_observations("TRADE", "EU27_2020", n=12)
        monkeypatch.setattr(
            "app.api.routers.observations.QueryService._compute_trade_observations",
            lambda region_code=None: trade_obs,
        )

        res = observations.get_observations("TRADE", region="EU27_2020")
        assert len(res) == 12

        monkeypatch.setattr(
            "app.api.routers.observations.ObservationService.get_observations",
            lambda indicator_code, region=None: (_ for _ in ()).throw(
                ValueError("Indicador no soportado")
            ),
        )
        with pytest.raises(HTTPException) as exc:
            observations.get_observations("INVALID")
        assert exc.value.status_code == 404


class TestAnalysisAndInvestmentRouters:

    def test_analysis_features_cycle_and_investment_support_trade(
        self, monkeypatch
    ):
        trade_obs = _make_monthly_observations("TRADE", "EU27_2020", n=36)
        monkeypatch.setattr(
            "app.api.routers.analysis.QueryService._compute_trade_observations",
            lambda region_code=None: trade_obs,
        )

        feat_body = analysis.get_feature_analysis("TRADE", "EU27_2020")
        assert feat_body["indicator_code"] == "TRADE"
        assert len(feat_body["observations"]) == 36

        inv_body = analysis.get_investment_analysis("TRADE", "EU27_2020")
        assert "overall" in inv_body

        cyc_body = analysis.get_cycle_analysis("TRADE", "EU27_2020")
        assert cyc_body["observations"] == 36

    def test_analysis_returns_404_for_unknown_indicator(self):
        with pytest.raises(HTTPException) as exc1:
            analysis.get_feature_analysis("NON_EXISTENT", "DE")
        assert exc1.value.status_code == 404

        with pytest.raises(HTTPException) as exc2:
            analysis.get_cycle_analysis("NON_EXISTENT", "DE")
        assert exc2.value.status_code == 404

        with pytest.raises(HTTPException) as exc3:
            analysis.get_investment_analysis("NON_EXISTENT", "DE")
        assert exc3.value.status_code == 404

    def test_investment_router_tolerates_missing_individual_indicators(
        self, monkeypatch
    ):
        gdp_obs = _make_monthly_observations("GDP", "US", "BEA", n=36)
        inf_obs = _make_monthly_observations("INFLATION", "US", "BLS", n=36)

        def fake_get_obs(indicator_code: str, region_code: str | None = None):
            if indicator_code == "GDP":
                return gdp_obs
            if indicator_code == "INFLATION":
                return inf_obs
            raise ValueError(f"No disponible: {indicator_code}")

        monkeypatch.setattr(
            "app.api.routers.investment.ObservationService.get_observations",
            fake_get_obs,
        )

        data = investment.get_investment_analysis("US", max_lag_days=3650)
        assert "asset_scores" in data

    def test_investment_and_regime_return_404_when_all_indicators_missing(
        self, monkeypatch
    ):
        def always_missing(indicator_code: str, region_code: str | None = None):
            raise ValueError("Sin datos")

        monkeypatch.setattr(
            "app.api.routers.investment.ObservationService.get_observations",
            always_missing,
        )
        monkeypatch.setattr(
            "app.api.routers.analysis.ObservationService.get_observations",
            always_missing,
        )

        with pytest.raises(HTTPException) as exc1:
            investment.get_investment_analysis("UNKNOWN")
        assert exc1.value.status_code == 404

        with pytest.raises(HTTPException) as exc2:
            analysis.get_macro_regime("UNKNOWN")
        assert exc2.value.status_code == 404

    def test_provider_routers_error_handling(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.routers.bea.BeaClient.get_gdp",
            lambda: (_ for _ in ()).throw(RuntimeError("BEA timeout")),
        )
        with pytest.raises(HTTPException) as exc_bea:
            bea.get_gdp()
        assert exc_bea.value.status_code == 502

        monkeypatch.setattr(
            "app.api.routers.bls.BlsClient.get_inflation",
            lambda: (_ for _ in ()).throw(ValueError("Invalid BLS series")),
        )
        with pytest.raises(HTTPException) as exc_bls:
            bls.get_inflation()
        assert exc_bls.value.status_code == 400

        monkeypatch.setattr(
            "app.api.routers.nbs.NbsClient.get_cpi",
            lambda: (_ for _ in ()).throw(RuntimeError("NBS down")),
        )
        with pytest.raises(HTTPException) as exc_nbs:
            nbs.get_cpi()
        assert exc_nbs.value.status_code == 502
