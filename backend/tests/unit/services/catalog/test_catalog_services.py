from __future__ import annotations

import pytest

from app.services.catalog.category_service import CategoryService
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.region_service import RegionService
from app.services.catalog.source_service import SourceService


class TestCategoryService:

    def test_get_categories(self):
        categories = CategoryService.get_categories()
        assert len(categories) >= 1
        names = [c.name for c in categories]
        assert "Economy" in names

    def test_get_category_exact_and_case_insensitive(self):
        cat1 = CategoryService.get_category("Economy")
        cat2 = CategoryService.get_category("economy")
        cat3 = CategoryService.get_category("  ECONOMY  ")

        assert cat1.name == "Economy"
        assert cat1.id == cat2.id == cat3.id

    def test_get_category_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Category 'NonExistent' not found"):
            CategoryService.get_category("NonExistent")


class TestRegionService:

    def test_get_regions(self):
        regions = RegionService.get_regions()
        assert len(regions) == 16
        codes = [r.code for r in regions]
        assert "ES" in codes
        assert "US" in codes
        assert "EU27_2020" in codes

    def test_get_region_case_insensitive(self):
        reg_es = RegionService.get_region("es")
        reg_us = RegionService.get_region("US")
        reg_eu = RegionService.get_region("eu27_2020")

        assert reg_es.code == "ES"
        assert reg_es.name == "Spain"
        assert reg_us.code == "US"
        assert reg_eu.code == "EU27_2020"

    def test_get_region_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Region 'XX' not found"):
            RegionService.get_region("XX")


class TestSourceService:

    def test_get_sources(self):
        sources = SourceService.get_sources()
        assert len(sources) == 7
        codes = [s.code for s in sources]
        assert "EUROSTAT" in codes
        assert "FRED" in codes
        assert "BEA" in codes
        assert "BLS" in codes

    def test_get_by_code_case_insensitive(self):
        src1 = SourceService.get_by_code("eurostat")
        src2 = SourceService.get_by_code("BLS")
        src3 = SourceService.get_by_code("  bea  ")

        assert src1.code == "EUROSTAT"
        assert src2.code == "BLS"
        assert src3.code == "BEA"

    def test_get_by_code_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Source 'UNKNOWN' not found"):
            SourceService.get_by_code("UNKNOWN")


class TestIndicatorService:

    def test_get_indicators(self):
        indicators = IndicatorService.get_indicators()
        assert len(indicators) == 14
        codes = [i.code for i in indicators]
        assert "GDP" in codes
        assert "INFLATION" in codes
        assert "UNEMPLOYMENT" in codes
        assert "TRADE" in codes

    def test_get_indicator_case_insensitive(self):
        ind_gdp = IndicatorService.get_indicator("gdp")
        ind_inf = IndicatorService.get_indicator("INFLATION")
        ind_trade = IndicatorService.get_indicator("trade")

        assert ind_gdp.code == "GDP"
        assert ind_inf.code == "INFLATION"
        assert ind_trade.code == "TRADE"

    def test_get_indicator_attributes(self):
        gdp = IndicatorService.get_indicator("GDP")
        assert gdp.frequency.value == "quarterly"
        assert gdp.growth_method.value == "log"
        assert gdp.category.name == "Economy"

    def test_get_indicator_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Indicator 'INVALID' not found"):
            IndicatorService.get_indicator("INVALID")
