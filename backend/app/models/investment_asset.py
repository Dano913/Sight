from enum import Enum

from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    EQUITIES = "equities"
    BONDS = "bonds"
    REAL_ESTATE = "real_estate"
    COMMODITIES = "commodities"
    FX = "fx"


class AssetType(str, Enum):
    BROAD_MARKET = "broad_market"
    FINANCIALS = "financials"
    INDUSTRIALS = "industrials"
    CONSUMER = "consumer"
    TECHNOLOGY = "technology"
    ENERGY = "energy"
    UTILITIES = "utilities"

    GOVERNMENT = "government"
    INVESTMENT_GRADE = "investment_grade"
    HIGH_YIELD = "high_yield"

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    REITS = "reits"

    OIL = "oil"
    GOLD = "gold"
    INDUSTRIAL_COMMODITIES = "industrial_commodities"

    LOCAL_CURRENCY = "local_currency"


class MacroFactor(str, Enum):
    GROWTH = "growth"
    ACTIVITY = "activity"
    EMPLOYMENT = "employment"
    INFLATION = "inflation"
    INTEREST_RATES = "interest_rates"
    FINANCIAL_CONDITIONS = "financial_conditions"
    CREDIT = "credit"
    HOUSING = "housing"
    TRADE = "trade"
    COMMODITIES = "commodities"
    CURRENCY = "currency"


class InvestmentAsset(BaseModel):
    code: str
    name: str

    asset_class: AssetClass
    asset_type: AssetType

    region: str | None = None

    sensitivities: dict[MacroFactor, float] = Field(default_factory=dict)