from enum import Enum


class RegionType(str, Enum):
    COUNTRY = "country"
    UNION = "union"
    REGION = "region"


class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class Unit(str, Enum):
    PERCENT = "%"
    INDEX = "index"
    EUR = "EUR"
    USD = "USD"
    POINTS = "points"
    BILLION_USD = "billion_usd"
    MILLION_EUR = "million_eur"


class GrowthMethod(str, Enum):
    LOG = "log"
    RATE = "rate"