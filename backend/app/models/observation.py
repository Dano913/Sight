from datetime import date

from pydantic import BaseModel

from .indicator import Indicator
from .region import Region
from .source import Source


class Observation(BaseModel):

    region: Region

    indicator: Indicator

    source: Source

    date: date

    value: float