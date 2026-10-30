from __future__ import annotations

import os
import requests


class BeaClient:
    BASE_URL = "https://apps.bea.gov/api/data"
    API_KEY = os.getenv("BEA_API_KEY")
    GDP_TABLE = "T10106"

    SERIES_CODES = {
        "GDP": ("A191RX", "1"),
        "EXPORTS": ("A020RX", None),
        "IMPORTS": ("A021RX", None),
    }

    @classmethod
    def _get_api_key(cls) -> str:
        api_key = cls.API_KEY or os.getenv("BEA_API_KEY")
        if not api_key:
            raise RuntimeError("Falta la variable de entorno BEA_API_KEY.")
        return api_key

    @classmethod
    def _fetch_nipa_series(
        cls,
        series_code: str,
        line_number: str | None = None,
    ) -> list[dict]:
        api_key = cls._get_api_key()

        params = {
            "UserID": api_key,
            "method": "GetData",
            "DataSetName": "NIPA",
            "TableName": cls.GDP_TABLE,
            "Frequency": "Q",
            "Year": "ALL",
            "ResultFormat": "JSON",
        }

        try:
            response = requests.get(
                cls.BASE_URL,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Error de conexión con el BEA: {exc}"
            ) from exc
        except ValueError as exc:
            raise RuntimeError(
                "El BEA no devolvió una respuesta JSON válida."
            ) from exc

        results = data.get("BEAAPI", {}).get("Results", {})

        if "Error" in results:
            raise RuntimeError(
                f"Error comunicado por el BEA: {results['Error']}"
            )

        rows = results.get("Data")
        if rows is None or not isinstance(rows, list):
            raise ValueError(
                f"Respuesta inesperada del BEA: {data}"
            )

        observations = [
            row
            for row in rows
            if isinstance(row, dict)
            and row.get("SeriesCode") == series_code
            and (line_number is None or row.get("LineNumber") == line_number)
            and row.get("CL_UNIT") == "Level"
        ]

        if not observations:
            raise ValueError(
                f"El BEA no devolvió observaciones para la serie "
                f"trimestral ({series_code})."
            )

        return observations

    @staticmethod
    def get_gdp() -> list[dict]:
        return BeaClient._fetch_nipa_series("A191RX", line_number="1")

    @staticmethod
    def get_exports() -> list[dict]:
        return BeaClient._fetch_nipa_series("A020RX")

    @staticmethod
    def get_imports() -> list[dict]:
        return BeaClient._fetch_nipa_series("A021RX")
