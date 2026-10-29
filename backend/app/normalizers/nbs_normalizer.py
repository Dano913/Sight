from datetime import date

from app.models.observation import Observation

from app.services.catalog.region_service import RegionService
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.source_service import SourceService


class NbsNormalizer:


    @staticmethod
    def to_observations(
        data,
        indicator_code: str,
        source_code: str
    ):

        """
        Convierte datos NBS China a Observation.
        """


        region = RegionService.get_region("CN")


        indicator = IndicatorService.get_indicator(
            indicator_code
        )


        source = SourceService.get_by_code(
            source_code
        )


        observations = []


        print("NORMALIZANDO NBS:", indicator_code)


        # ESTE BLOQUE LO AJUSTAMOS CUANDO VEAMOS EL JSON REAL

        for item in data:


            observation = Observation(

                region=region,

                indicator=indicator,

                source=source,

                date=date(
                    int(item["year"]),
                    1,
                    1
                ),

                value=float(
                    item["value"]
                )

            )


            observations.append(
                observation
            )


        print(
            f"NBS {indicator_code} NORMALIZADAS:",
            len(observations)
        )


        return observations