from datetime import date

from app.models.observation import Observation
from app.services.catalog.region_service import RegionService
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.source_service import SourceService


class BeaNormalizer:

    @staticmethod
    def to_observations(
        data: list[dict],
        indicator_code: str,
        source_code: str,
    ) -> list[Observation]:
        """
        Convierte la respuesta del BEA en observaciones del PIB real
        trimestral de Estados Unidos.

        A191RX representa el nivel del PIB real en millones de dólares
        encadenados de 2017. Se convierte a miles de millones de USD.
        """

        region = RegionService.get_region("US")
        indicator = IndicatorService.get_indicator(indicator_code)
        source = SourceService.get_by_code(source_code)

        observations: list[Observation] = []

        month_map = {
            "Q1": 1,
            "Q2": 4,
            "Q3": 7,
            "Q4": 10,
        }

        for row in data:
            if row.get("SeriesCode") != "A191RX":
                continue

            if row.get("LineNumber") != "1":
                continue

            if row.get("CL_UNIT") != "Level":
                continue

            raw_value = row.get("DataValue")

            if raw_value in (None, "", "(NA)"):
                continue

            try:
                value = float(raw_value.replace(",", "")) / 1000
            except (AttributeError, ValueError):
                continue

            period = row.get("TimePeriod", "")

            if len(period) != 6 or period[-2:] not in month_map:
                continue

            try:
                year = int(period[:4])
            except ValueError:
                continue

            observation = Observation(
                region=region,
                indicator=indicator,
                source=source,
                date=date(year, month_map[period[-2:]], 1),
                value=value,
            )

            observations.append(observation)

        print("BEA normalizadas:", len(observations))

        return observations