from __future__ import annotations

from typing import Any

from app.clients.bea_client import BeaClient
from app.clients.bls_client import BlsClient
from app.clients.eurostat_client import EurostatClient
from app.normalizers.bea_normalizer import BeaNormalizer
from app.normalizers.bls_normalizer import BlsNormalizer
from app.normalizers.eurostat_normalizer import EurostatNormalizer
from app.repositories.observation_repository import ObservationRepository
from app.cache.query_cache import query_cache
from app.models.observation import Observation


class ObservationService:
    """
    Servicio de obtención, normalización y sincronización de observaciones.
    """

    _FETCHER_REGISTRY: dict[str, list[tuple[str, Any, str, Any]]] = {
        "GDP": [
            ("EUROSTAT", EurostatClient, "get_gdp", EurostatNormalizer),
            ("BEA", BeaClient, "get_gdp", BeaNormalizer),
        ],
        "INFLATION": [
            ("EUROSTAT", EurostatClient, "get_inflation", EurostatNormalizer),
            ("BLS", BlsClient, "get_inflation", BlsNormalizer),
        ],
        "UNEMPLOYMENT": [
            ("EUROSTAT", EurostatClient, "get_unemployment", EurostatNormalizer),
            ("BLS", BlsClient, "get_unemployment", BlsNormalizer),
        ],
        "HOUSE_PRICE_INDEX": [
            ("EUROSTAT", EurostatClient, "get_house_price_index", EurostatNormalizer),
        ],
        "CPI": [
            ("EUROSTAT", EurostatClient, "get_cpi", EurostatNormalizer),
            ("BLS", BlsClient, "get_cpi", BlsNormalizer),
        ],
        "INTEREST_RATE": [
            ("EUROSTAT", EurostatClient, "get_interest_rate", EurostatNormalizer),
            ("BLS", BlsClient, "get_interest_rate", BlsNormalizer),
        ],
        "INDUSTRIAL_PRODUCTION": [
            ("EUROSTAT", EurostatClient, "get_industrial_production", EurostatNormalizer),
            ("BLS", BlsClient, "get_industrial_production", BlsNormalizer),
        ],
        "RETAIL_SALES": [
            ("EUROSTAT", EurostatClient, "get_retail_sales", EurostatNormalizer),
            ("BLS", BlsClient, "get_retail_sales", BlsNormalizer),
        ],
        "EXPORTS": [
            ("EUROSTAT", EurostatClient, "get_exports", EurostatNormalizer),
            ("BEA", BeaClient, "get_exports", BeaNormalizer),
        ],
        "IMPORTS": [
            ("EUROSTAT", EurostatClient, "get_imports", EurostatNormalizer),
            ("BEA", BeaClient, "get_imports", BeaNormalizer),
        ],
        "EXPORTS_BY_COUNTRY": [
            ("EUROSTAT", EurostatClient, "get_exports_by_country", EurostatNormalizer),
        ],
        "IMPORTS_BY_COUNTRY": [
            ("EUROSTAT", EurostatClient, "get_imports_by_country", EurostatNormalizer),
        ],
        "TRADE_BALANCE_BY_COUNTRY": [
            ("EUROSTAT", EurostatClient, "get_trade_balance_by_country", EurostatNormalizer),
        ],
    }

    @classmethod
    def get_observations(
        cls,
        indicator_code: str,
        region_code: str | None = None,
        refresh: bool = False,
    ) -> list[Observation]:
        """
        Obtiene observaciones para un indicador, consultando la caché SQLite
        o descargando desde fuentes oficiales externas.
        """

        indicator_code = indicator_code.strip().upper()

        if region_code:
            region_code = region_code.strip().upper()

        # ==================================================
        # 1. CACHÉ SQLITE
        # ==================================================

        if not refresh and ObservationRepository.exists(indicator_code, region_code):
            print(f">>> SQLITE CACHE: {indicator_code} {region_code or 'ALL'}")

            if region_code is not None:
                cached_observations = (
                    ObservationRepository.get_by_region_and_indicator(
                        region_code=region_code,
                        indicator_code=indicator_code,
                    )
                )
            else:
                cached_observations = (
                    ObservationRepository.get_by_indicator(
                        indicator_code
                    )
                )

            print(f"OBSERVACIONES DEVUELTAS: {len(cached_observations)}")
            return cached_observations

        print(f"\n==============================")
        print(f"GET OBSERVATIONS: {indicator_code} (REGION: {region_code})")

        # ==================================================
        # 2. DESCARGA Y NORMALIZACIÓN DESDE PROVEEDORES
        # ==================================================

        if indicator_code not in cls._FETCHER_REGISTRY:
            raise ValueError(f"Indicador no soportado: {indicator_code}")

        observations: list[Observation] = []

        for source_code, client_cls, method_name, normalizer_cls in cls._FETCHER_REGISTRY[indicator_code]:
            try:
                fetcher = getattr(client_cls, method_name)
                raw_data = fetcher()

                # Normalización estándar (data, indicator_code, source_code)
                obs = normalizer_cls.to_observations(
                    raw_data,
                    indicator_code=indicator_code,
                    source_code=source_code,
                )

                print(f"{source_code} {indicator_code}: {len(obs)}")
                observations.extend(obs)

            except Exception as e:
                print(f"[{source_code} {indicator_code}] Error: {e}")

        print(f"TOTAL OBSERVACIONES: {len(observations)}")

        if not observations:
            raise ValueError(
                f"No se pudieron obtener datos para {indicator_code}"
            )

        # ==================================================
        # 3. DEDUPLICACIÓN
        # ==================================================

        unique_observations: list[Observation] = []
        seen = set()

        for observation in observations:
            key = (
                observation.region.code,
                observation.indicator.code,
                observation.source.code,
                observation.date,
            )

            if key in seen:
                continue

            seen.add(key)
            unique_observations.append(observation)

        print(f"OBSERVACIONES ÚNICAS: {len(unique_observations)}")

        # ==================================================
        # 4. ACTUALIZACIÓN EN SQLITE Y LIMPIEZA DE CACHÉ
        # ==================================================

        print(f">>> ACTUALIZANDO SQLITE: {indicator_code}")

        grouped_observations: dict[tuple[str, str, str], list[Observation]] = {}

        for observation in unique_observations:
            key = (
                observation.region.code,
                observation.indicator.code,
                observation.source.code,
            )
            grouped_observations.setdefault(key, []).append(observation)

        total_saved = 0

        for (
            observation_region,
            observation_indicator,
            observation_source,
        ), source_observations in grouped_observations.items():
            ObservationRepository.replace_by_region_indicator_source(
                region_code=observation_region,
                indicator_code=observation_indicator,
                source_code=observation_source,
                observations=source_observations,
            )
            total_saved += len(source_observations)

        print(f"GUARDADAS EN SQLITE: {total_saved}")
        query_cache.clear()

        # ==================================================
        # 5. FILTRADO REGIONAL SI SE ESPECIFICÓ
        # ==================================================

        if region_code is not None:
            unique_observations = [
                observation
                for observation in unique_observations
                if observation.region.code == region_code
            ]

        print(f"OBSERVACIONES DEVUELTAS: {len(unique_observations)}")
        return unique_observations
