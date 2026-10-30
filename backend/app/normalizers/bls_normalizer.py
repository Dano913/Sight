from __future__ import annotations

from datetime import date
import math

from app.models.observation import Observation
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.region_service import RegionService
from app.services.catalog.source_service import SourceService


class BlsNormalizer:

    @staticmethod
    def to_observations(
        data: list[dict] | None,
        indicator_code: str,
        source_code: str,
    ) -> list[Observation]:
        """
        Convierte la respuesta mensual del BLS en una lista de Observation.
        """
        if not data:
            return []

        region = RegionService.get_region("US")
        indicator = IndicatorService.get_indicator(indicator_code)
        source = SourceService.get_by_code(source_code)

        observations: list[Observation] = []

        for row in data:
            if not isinstance(row, dict):
                continue

            value = row.get("value")

            if value in (None, "", "(NA)", "-", "."):
                continue

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue

            if not math.isfinite(numeric_value):
                continue

            period = str(row.get("period", ""))

            # Ignorar datos anuales (M13) y periodos no mensuales
            if not period.startswith("M"):
                continue

            try:
                month = int(period[1:])
                year = int(row.get("year"))  # type: ignore[arg-type]
            except (TypeError, ValueError):
                continue

            if not 1 <= month <= 12:
                continue

            try:
                obs_date = date(year, month, 1)
            except ValueError:
                continue

            observations.append(
                Observation(
                    region=region,
                    indicator=indicator,
                    source=source,
                    date=obs_date,
                    value=numeric_value,
                )
            )

        return observations
