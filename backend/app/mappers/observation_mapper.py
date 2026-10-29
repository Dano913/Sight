from app.models.observation import Observation

from app.responses.observation_response import (
    ObservationResponse,
)

from app.responses.region_response import (
    RegionResponse,
)

from app.responses.indicator_response import (
    IndicatorResponse,
)


class ObservationMapper:

    @staticmethod
    def to_region_response(
        observations: list[Observation]
    ) -> RegionResponse:
        """
        Convierte una lista de Observation en un RegionResponse.
        """

        if not observations:
            raise ValueError(
                "La lista de observaciones está vacía."
            )

        first = observations[0]

        indicators = {}

        for observation in observations:

            indicator = observation.indicator.code

            if indicator not in indicators:
                indicators[indicator] = []

            indicators[indicator].append(

                ObservationResponse(
                    date=observation.date,
                    value=observation.value,
                    source=observation.source.code,
                )

            )

        return RegionResponse(

            region=first.region,

            indicators=indicators,

        )


    @staticmethod
    def to_indicator_response(
        observations: list[Observation]
    ) -> IndicatorResponse:
        """
        Convierte una lista de Observation en un IndicatorResponse.
        """

        if not observations:
            raise ValueError(
                "La lista de observaciones está vacía."
            )

        first = observations[0]

        regions = {}

        for observation in observations:

            region = observation.region.code

            if region not in regions:
                regions[region] = []

            regions[region].append(

                ObservationResponse(
                    date=observation.date,
                    value=observation.value,
                    source=observation.source.code,
                )

            )

        return IndicatorResponse(

            indicator=first.indicator,

            regions=regions,

        )