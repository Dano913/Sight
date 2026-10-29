from pydantic import BaseModel

from .enums import RegionType


class Region(BaseModel):
    id: int
    code: str
    name: str
    region_type: RegionType