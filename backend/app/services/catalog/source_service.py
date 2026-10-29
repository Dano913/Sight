from __future__ import annotations

from app.models.source import Source


class SourceService:

    _SOURCES: list[Source] = [
        Source(
            id=1,
            code="EUROSTAT",
            name="Eurostat",
            website="https://ec.europa.eu/eurostat",
        ),
        Source(
            id=2,
            code="ECB",
            name="European Central Bank",
            website="https://data.ecb.europa.eu",
        ),
        Source(
            id=3,
            code="OECD",
            name="OECD",
            website="https://data-explorer.oecd.org",
        ),
        Source(
            id=4,
            code="FRED",
            name="FRED",
            website="https://fred.stlouisfed.org",
        ),
        Source(
            id=5,
            code="BLS",
            name="Bureau of Labor Statistics",
            website="https://www.bls.gov",
        ),
        Source(
            id=6,
            code="BEA",
            name="Bureau of Economic Analysis",
            website="https://www.bea.gov",
        ),
        Source(
            id=7,
            code="NBS",
            name="National Bureau of Statistics of China",
            website="https://www.stats.gov.cn",
        ),
    ]

    _BY_CODE: dict[str, Source] = {
        source.code.upper(): source for source in _SOURCES
    }

    @classmethod
    def get_sources(cls) -> list[Source]:
        return list(cls._SOURCES)

    @classmethod
    def get_by_code(cls, code: str) -> Source:
        source = cls._BY_CODE.get(code.strip().upper())
        if source is not None:
            return source

        raise ValueError(f"Source '{code}' not found")
