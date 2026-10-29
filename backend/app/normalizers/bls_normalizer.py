from datetime import date

from app.models.observation import Observation

from app.services.catalog.region_service import RegionService
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.source_service import SourceService


class BlsNormalizer:

    @staticmethod
    def to_observations(
        data: list[dict],
        indicator_code: str,
        source_code: str,
    ) -> list[Observation]:
        """
        Convierte la respuesta del BLS en una lista de Observation.
        """

        region = RegionService.get_region("US")

        indicator = IndicatorService.get_indicator(
            indicator_code
        )

        source = SourceService.get_by_code(
            source_code
        )

        observations: list[Observation] = []

        for row in data:

            value = row.get("value")

            if value in (None, "", "(NA)"):
                continue

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue

            period = row["period"]

            # Ignorar datos anuales y periodos especiales
            if not period.startswith("M"):
                continue

            month = int(period[1:])

            if month > 12:
                continue

            observation = Observation(
                region=region,
                indicator=indicator,
                source=source,
                date=date(
                    int(row["year"]),
                    month,
                    1
                ),
                value=numeric_value
            )

            observations.append(observation)

        return observations