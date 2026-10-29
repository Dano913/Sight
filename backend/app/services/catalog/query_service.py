from __future__ import annotations

from app.cache.query_cache import query_cache
from app.mappers.observation_mapper import ObservationMapper
from app.models.observation import Observation
from app.repositories.observation_repository import ObservationRepository
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.observation_service import ObservationService


class QueryService:

    # ==========================================
    # INDICADORES DISPONIBLES DESDE FUENTES
    # ==========================================

    SOURCE_INDICATORS = {
        "GDP",
        "INFLATION",
        "UNEMPLOYMENT",
        "HOUSE_PRICE_INDEX",
        "CPI",
        "INTEREST_RATE",
        "INDUSTRIAL_PRODUCTION",
        "RETAIL_SALES",
        "EXPORTS",
        "IMPORTS",
        "EXPORTS_BY_COUNTRY",
        "IMPORTS_BY_COUNTRY",
        "TRADE_BALANCE_BY_COUNTRY",
    }

    # ==========================================
    # GESTIÓN DE CACHÉ
    # ==========================================

    @staticmethod
    def clear_cache() -> None:
        """Limpia toda la caché de consultas."""
        query_cache.clear()

    # ==========================================
    # CÁLCULO DE INDICADORES SINTÉTICOS (TRADE)
    # ==========================================

    @staticmethod
    def _compute_trade_observations(
        region_code: str | None = None,
    ) -> list[Observation]:
        """
        Calcula la serie sintética de TRADE = EXPORTS - IMPORTS
        para una región específica o para todas las regiones disponibles.
        """
        exports = ObservationService.get_observations(
            indicator_code="EXPORTS",
            region_code=region_code,
        )

        imports = ObservationService.get_observations(
            indicator_code="IMPORTS",
            region_code=region_code,
        )

        if not exports or not imports:
            target = f" en {region_code}" if region_code else ""
            raise ValueError(
                f"No existen datos suficientes para calcular TRADE{target}"
            )

        imports_by_date = {
            (obs.region.code, obs.source.code, obs.date): obs.value
            for obs in imports
        }

        trade_indicator = IndicatorService.get_indicator("TRADE")
        trade_observations = []

        for export in exports:
            import_value = imports_by_date.get(
                (export.region.code, export.source.code, export.date)
            )

            if import_value is None:
                continue

            trade_observations.append(
                Observation(
                    region=export.region,
                    indicator=trade_indicator,
                    source=export.source,
                    date=export.date,
                    value=float(export.value - import_value),
                )
            )

        if not trade_observations:
            target = f" para {region_code}" if region_code else ""
            raise ValueError(
                f"No se pudo calcular TRADE{target}"
            )

        return trade_observations

    # ==========================================
    # POR INDICADOR
    # ==========================================

    @staticmethod
    def get_by_indicator(indicator_code: str):
        indicator_code = indicator_code.strip().upper()
        key = f"indicator:{indicator_code}"

        if key in query_cache:
            return query_cache[key]

        if indicator_code == "TRADE":
            observations = QueryService._compute_trade_observations(
                region_code=None
            )
        elif indicator_code in QueryService.SOURCE_INDICATORS:
            observations = ObservationService.get_observations(
                indicator_code=indicator_code
            )
        else:
            observations = ObservationRepository.get_by_indicator(
                indicator_code
            )

        if not observations:
            raise ValueError(
                f"No existen observaciones para {indicator_code}"
            )

        result = ObservationMapper.to_indicator_response(observations)
        query_cache[key] = result
        return result

    # ==========================================
    # POR REGIÓN
    # ==========================================

    @staticmethod
    def get_by_region(region_code: str):
        region_code = region_code.strip().upper()
        key = f"region:{region_code}"

        if key in query_cache:
            return query_cache[key]

        observations = ObservationRepository.get_by_region(region_code)

        if not observations:
            raise ValueError(
                f"No existen observaciones para la región {region_code}"
            )

        result = ObservationMapper.to_region_response(observations)
        query_cache[key] = result
        return result

    # ==========================================
    # REGIÓN + INDICADOR
    # ==========================================

    @staticmethod
    def get_by_region_and_indicator(
        region_code: str,
        indicator_code: str,
    ):
        region_code = region_code.strip().upper()
        indicator_code = indicator_code.strip().upper()

        key = f"region_indicator:{region_code}:{indicator_code}"

        if key in query_cache:
            return query_cache[key]

        if indicator_code == "TRADE":
            observations = QueryService._compute_trade_observations(
                region_code=region_code
            )
        elif indicator_code in QueryService.SOURCE_INDICATORS:
            observations = ObservationService.get_observations(
                indicator_code=indicator_code,
                region_code=region_code,
            )
        else:
            observations = (
                ObservationRepository.get_by_region_and_indicator(
                    region_code,
                    indicator_code,
                )
            )

        if not observations:
            raise ValueError(
                f"No existen observaciones para {region_code} / {indicator_code}"
            )

        result = ObservationMapper.to_region_response(observations)
        query_cache[key] = result
        return result

    # ==========================================
    # COMPARAR REGIONES
    # ==========================================

    @staticmethod
    def compare_regions(
        indicator_code: str,
        region_codes: list[str],
    ):
        indicator_code = indicator_code.strip().upper()
        clean_regions = [
            r.strip().upper() for r in region_codes if r.strip()
        ]

        sorted_regions = ",".join(sorted(clean_regions))
        key = f"compare:{indicator_code}:{sorted_regions}"

        if key in query_cache:
            return query_cache[key]

        if indicator_code == "TRADE":
            all_trade = QueryService._compute_trade_observations(
                region_code=None
            )
            observations = [
                obs for obs in all_trade
                if obs.region.code in clean_regions
            ]
        else:
            observations = (
                ObservationRepository.get_by_regions_and_indicator(
                    clean_regions,
                    indicator_code,
                )
            )

        grouped = {}
        for observation in observations:
            region = observation.region.code
            if region not in grouped:
                grouped[region] = []
            grouped[region].append(observation)

        result = [
            ObservationMapper.to_region_response(region_observations)
            for region_observations in grouped.values()
        ]

        query_cache[key] = result
        return result
