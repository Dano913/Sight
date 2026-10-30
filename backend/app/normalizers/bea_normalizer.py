from __future__ import annotations

from datetime import date
import math

from app.models.observation import Observation
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.region_service import RegionService
from app.services.catalog.source_service import SourceService


class BeaNormalizer:

    SERIES_BY_INDICATOR: dict[str, tuple[str, str | None]] = {
        "GDP": ("A191RX", "1"),
        "EXPORTS": ("A020RX", None),
        "IMPORTS": ("A021RX", None),
    }

    MONTH_MAP = {
        "Q1": 1,
        "Q2": 4,
        "Q3": 7,
        "Q4": 10,
    }

    @staticmethod
    def to_observations(
        data: list[dict] | None,
        indicator_code: str,
        source_code: str,
    ) -> list[Observation]:
        """
        Convierte la respuesta del BEA (tabla NIPA T10106) en observaciones
        trimestrales de Estados Unidos (GDP, EXPORTS, IMPORTS).

        Los valores originales en millones de dólares encadenados de 2017
        se convierten a miles de millones de USD (dividiendo por 1000).
        """
        if not data:
            return []

        clean_indicator = indicator_code.strip().upper()
        region = RegionService.get_region("US")
        indicator = IndicatorService.get_indicator(clean_indicator)
        source = SourceService.get_by_code(source_code)

        expected_series, expected_line = BeaNormalizer.SERIES_BY_INDICATOR.get(
            clean_indicator,
            ("A191RX", "1"),
        )

        observations: list[Observation] = []

        for row in data:
            if not isinstance(row, dict):
                continue

            if row.get("SeriesCode") != expected_series:
                continue

            if expected_line is not None and row.get("LineNumber") != expected_line:
                continue

            if row.get("CL_UNIT") != "Level":
                continue

            raw_value = row.get("DataValue")

            if raw_value in (None, "", "(NA)"):
                continue

            try:
                value = float(str(raw_value).replace(",", "")) / 1000.0
            except (AttributeError, TypeError, ValueError):
                continue

            if not math.isfinite(value):
                continue

            period = str(row.get("TimePeriod", ""))

            if len(period) != 6 or period[-2:] not in BeaNormalizer.MONTH_MAP:
                continue

            try:
                year = int(period[:4])
                obs_date = date(year, BeaNormalizer.MONTH_MAP[period[-2:]], 1)
            except ValueError:
                continue

            observations.append(
                Observation(
                    region=region,
                    indicator=indicator,
                    source=source,
                    date=obs_date,
                    value=value,
                )
            )

        return observations
