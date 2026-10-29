from pydantic import BaseModel

from app.models.region import Region
from app.responses.observation_response import ObservationResponse


class RegionResponse(BaseModel):

    region: Region

    indicators: dict[
        str,
        list[ObservationResponse]
    ]