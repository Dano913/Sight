from __future__ import annotations

from app.models.enums import Frequency, GrowthMethod, Unit
from app.models.indicator import Indicator
from app.services.catalog.category_service import CategoryService


class IndicatorService:

    _economy = CategoryService.get_category("Economy")

    _INDICATORS: list[Indicator] = [

        Indicator(
            id=1,
            code="GDP",
            name="Gross Domestic Product",
            description="Gross Domestic Product",
            category=_economy,
            frequency=Frequency.QUARTERLY,
            unit=Unit.BILLION_USD,
            growth_method=GrowthMethod.LOG,
        ),

        Indicator(
            id=2,
            code="INFLATION",
            name="Inflation",
            description="Inflation Rate",
            category=_economy,
            frequency=Frequency.MONTHLY,
            unit=Unit.PERCENT,
            growth_method=GrowthMethod.RATE,
        ),

        Indicator(
            id=3,
            code="UNEMPLOYMENT",
            name="Unemployment",
            description="Unemployment Rate",
            category=_economy,
            frequency=Frequency.MONTHLY,
            unit=Unit.PERCENT,
            growth_method=GrowthMethod.RATE,
        ),

        Indicator(
            id=4,
            code="HOUSE_PRICE_INDEX",
            name="House Price Index",
            description="House Price Index",
            category=_economy,
            frequency=Frequency.QUARTERLY,
            unit=Unit.INDEX,
            growth_method=GrowthMethod.LOG,
        ),

        Indicator(
            id=5,
            code="CPI",
            name="Consumer Price Index",
            description="Consumer Price Index",
            category=_economy,
            frequency=Frequency.MONTHLY,
            unit=Unit.INDEX,
            growth_method=GrowthMethod.LOG,
        ),

        Indicator(
            id=6,
            code="INTEREST_RATE",
            name="Interest Rate",
            description="Central Bank Interest Rate",
            category=_economy,
            frequency=Frequency.MONTHLY,
            unit=Unit.PERCENT,
            growth_method=GrowthMethod.RATE,
        ),

        Indicator(
            id=7,
            code="INDUSTRIAL_PRODUCTION",
            name="Industrial Production",
            description="Industrial Production Index",
            category=_economy,
            frequency=Frequency.MONTHLY,
            unit=Unit.INDEX,
            growth_method=GrowthMethod.LOG,
        ),

        Indicator(
            id=8,
            code="RETAIL_SALES",
            name="Retail Sales",
            description="Retail Sales Index",
            category=_economy,
            frequency=Frequency.MONTHLY,
            unit=Unit.INDEX,
            growth_method=GrowthMethod.LOG,
        ),

        Indicator(
            id=9,
            code="EXPORTS",
            name="Exports",
            description="Exports of Goods and Services",
            category=_economy,
            frequency=Frequency.MONTHLY,
            unit=Unit.BILLION_USD,
            growth_method=GrowthMethod.LOG,
        ),

        Indicator(
            id=10,
            code="IMPORTS",
            name="Imports",
            description="Imports of Goods and Services",
            category=_economy,
            frequency=Frequency.MONTHLY,
            unit=Unit.BILLION_USD,
            growth_method=GrowthMethod.LOG,
        ),

        Indicator(
            id=11,
            code="TRADE",
            name="Trade Balance",
            description="Exports minus Imports",
            category=_economy,
            frequency=Frequency.MONTHLY,
            unit=Unit.BILLION_USD,
            growth_method=GrowthMethod.RATE,
        ),

        Indicator(
            id=12,
            code="EXPORTS_BY_COUNTRY",
            name="Exports by Country",
            description="Exports of Goods (per EU member state, world partner)",
            category=_economy,
            frequency=Frequency.ANNUAL,
            unit=Unit.MILLION_EUR,
            growth_method=GrowthMethod.LOG,
        ),

        Indicator(
            id=13,
            code="IMPORTS_BY_COUNTRY",
            name="Imports by Country",
            description="Imports of Goods (per EU member state, world partner)",
            category=_economy,
            frequency=Frequency.ANNUAL,
            unit=Unit.MILLION_EUR,
            growth_method=GrowthMethod.LOG,
        ),

        Indicator(
            id=14,
            code="TRADE_BALANCE_BY_COUNTRY",
            name="Trade Balance by Country",
            description="Exports minus Imports (per EU member state, world partner)",
            category=_economy,
            frequency=Frequency.ANNUAL,
            unit=Unit.MILLION_EUR,
            growth_method=GrowthMethod.RATE,
        ),
    ]

    _BY_CODE: dict[str, Indicator] = {
        indicator.code.upper(): indicator for indicator in _INDICATORS
    }

    @classmethod
    def get_indicators(cls) -> list[Indicator]:
        return list(cls._INDICATORS)

    @classmethod
    def get_indicator(cls, code: str) -> Indicator:
        indicator = cls._BY_CODE.get(code.strip().upper())
        if indicator is not None:
            return indicator

        raise ValueError(f"Indicator '{code}' not found")