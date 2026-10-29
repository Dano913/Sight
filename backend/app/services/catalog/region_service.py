from __future__ import annotations

from app.models.enums import RegionType
from app.models.region import Region


class RegionService:

    _REGIONS: list[Region] = [
        Region(id=1, code="EU27_2020", name="European Union", region_type=RegionType.UNION),
        Region(id=2, code="DE", name="Germany", region_type=RegionType.COUNTRY),
        Region(id=3, code="FR", name="France", region_type=RegionType.COUNTRY),
        Region(id=4, code="IT", name="Italy", region_type=RegionType.COUNTRY),
        Region(id=5, code="ES", name="Spain", region_type=RegionType.COUNTRY),
        Region(id=6, code="NL", name="Netherlands", region_type=RegionType.COUNTRY),
        Region(id=7, code="PL", name="Poland", region_type=RegionType.COUNTRY),
        Region(id=8, code="BE", name="Belgium", region_type=RegionType.COUNTRY),
        Region(id=9, code="SE", name="Sweden", region_type=RegionType.COUNTRY),
        Region(id=10, code="AT", name="Austria", region_type=RegionType.COUNTRY),
        Region(id=11, code="IE", name="Ireland", region_type=RegionType.COUNTRY),
        Region(id=12, code="DK", name="Denmark", region_type=RegionType.COUNTRY),
        Region(id=13, code="FI", name="Finland", region_type=RegionType.COUNTRY),
        Region(id=14, code="CZ", name="Czechia", region_type=RegionType.COUNTRY),
        Region(id=15, code="PT", name="Portugal", region_type=RegionType.COUNTRY),
        Region(id=16, code="US", name="United States", region_type=RegionType.COUNTRY),
    ]

    _BY_CODE: dict[str, Region] = {
        region.code.upper(): region for region in _REGIONS
    }

    @classmethod
    def get_regions(cls) -> list[Region]:
        return list(cls._REGIONS)

    @classmethod
    def get_region(cls, code: str) -> Region:
        region = cls._BY_CODE.get(code.strip().upper())
        if region is not None:
            return region

        raise ValueError(f"Region '{code}' not found")
    