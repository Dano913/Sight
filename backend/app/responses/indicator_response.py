from app.models.indicator import Indicator
from app.responses.observation_response import ObservationResponse

from pydantic import BaseModel


class IndicatorResponse(BaseModel):

    indicator: Indicator

    regions: dict[str, list[ObservationResponse]]