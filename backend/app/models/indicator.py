from pydantic import BaseModel

from .category import Category
from .enums import Frequency,  GrowthMethod, Unit


class Indicator(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None

    category: Category

    frequency: Frequency

    growth_method: GrowthMethod

    unit: Unit