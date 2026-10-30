from __future__ import annotations

from datetime import date
import math
from typing import Any

from app.models.enums import RegionType
from app.models.observation import Observation
from app.models.region import Region
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.region_service import RegionService
from app.services.catalog.source_service import SourceService


class NbsNormalizer:

    QUARTER_MONTH = {
        "A": 1,
        "B": 4,
        "C": 7,
        "D": 10,
    }

    @staticmethod
    def _get_china_region() -> Region:
        try:
            return RegionService.get_region("CN")
        except ValueError:
            return Region(
                id=17,
                code="CN",
                name="China",
                region_type=RegionType.COUNTRY,
            )

    @staticmethod
    def _parse_nbs_period(period_code: str) -> date | None:
        code = str(period_code).strip()
        if not code:
            return None

        try:
            # Anual: "2024"
            if len(code) == 4 and code.isdigit():
                return date(int(code), 1, 1)

            # Trimestral NBS: "2024A", "2024B", "2024C", "2024D"
            if (
                len(code) == 5
                and code[:4].isdigit()
                and code[4].upper() in NbsNormalizer.QUARTER_MONTH
            ):
                return date(
                    int(code[:4]),
                    NbsNormalizer.QUARTER_MONTH[code[4].upper()],
                    1,
                )

            # Mensual NBS: "202401" .. "202412"
            if len(code) == 6 and code.isdigit():
                year = int(code[:4])
                month = int(code[4:])
                if 1 <= month <= 12:
                    return date(year, month, 1)
        except ValueError:
            return None

        return None

    @staticmethod
    def to_observations(
        data: dict[str, Any] | list[dict[str, Any]] | None,
        indicator_code: str,
        source_code: str,
    ) -> list[Observation]:
        """
        Convierte datos de la NBS de China a objetos Observation.
        Soporta tanto el sobre JSON nativo de easyquery.htm
        (`returndata.datanodes`) como listas planas de diccionarios
        (`[{"year": "2024", "value": 102.5}]`).
        """
        if not data:
            return []

        region = NbsNormalizer._get_china_region()
        indicator = IndicatorService.get_indicator(indicator_code)
        source = SourceService.get_by_code(source_code)

        observations: list[Observation] = []

        # Caso 1: Estructura JSON nativa de NBS (returndata -> datanodes)
        if isinstance(data, dict):
            datanodes = (
                data.get("returndata", {}).get("datanodes", [])
                if isinstance(data.get("returndata"), dict)
                else []
            )

            for node in datanodes:
                if not isinstance(node, dict):
                    continue

                data_obj = node.get("data", {})
                if not isinstance(data_obj, dict) or not data_obj.get("hasdata"):
                    continue

                raw_val = data_obj.get("data", data_obj.get("strdata"))
                try:
                    numeric_val = float(raw_val)
                except (TypeError, ValueError):
                    continue

                if not math.isfinite(numeric_val):
                    continue

                wds = node.get("wds", [])
                period_code = None
                if isinstance(wds, list):
                    for wd in wds:
                        if isinstance(wd, dict) and wd.get("wdcode") == "sj":
                            period_code = wd.get("valuecode")
                            break

                obs_date = (
                    NbsNormalizer._parse_nbs_period(str(period_code))
                    if period_code is not None
                    else None
                )
                if obs_date is None:
                    continue

                observations.append(
                    Observation(
                        region=region,
                        indicator=indicator,
                        source=source,
                        date=obs_date,
                        value=numeric_val,
                    )
                )

            return observations

        # Caso 2: Lista plana de diccionarios
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue

                raw_val = item.get("value")
                if raw_val in (None, "", "(NA)"):
                    continue

                try:
                    numeric_val = float(raw_val)
                except (TypeError, ValueError):
                    continue

                if not math.isfinite(numeric_val):
                    continue

                period_str = str(item.get("period") or item.get("year") or "")
                obs_date = NbsNormalizer._parse_nbs_period(period_str)
                if obs_date is None:
                    continue

                observations.append(
                    Observation(
                        region=region,
                        indicator=indicator,
                        source=source,
                        date=obs_date,
                        value=numeric_val,
                    )
                )

        return observations
