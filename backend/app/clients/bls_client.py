from __future__ import annotations

import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# Cargar el .env situado en la raíz de backend/
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)


class BlsClient:

    BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    API_KEY = os.getenv("BLS_API_KEY")

    CPI_SERIES = "CUUR0000SA0"
    UNEMPLOYMENT_SERIES = "LNS14000000"

    START_YEAR = 1947
    END_YEAR = 2026
    MAX_YEARS_PER_REQUEST = 10

    @classmethod
    def _get_api_key(cls) -> str:
        api_key = cls.API_KEY or os.getenv("BLS_API_KEY")
        if not api_key:
            raise RuntimeError(
                "BLS_API_KEY no está definida. "
                "Comprueba la configuración del archivo .env."
            )
        return api_key

    @staticmethod
    def _get_series(series_id: str) -> list[dict]:
        api_key = BlsClient._get_api_key()

        all_observations: list[dict] = []
        start = BlsClient.START_YEAR

        while start <= BlsClient.END_YEAR:
            end = min(
                start + BlsClient.MAX_YEARS_PER_REQUEST - 1,
                BlsClient.END_YEAR,
            )

            try:
                response = requests.post(
                    BlsClient.BASE_URL,
                    json={
                        "seriesid": [series_id],
                        "startyear": str(start),
                        "endyear": str(end),
                        "registrationkey": api_key,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as exc:
                raise RuntimeError(
                    f"Error de conexión con BLS para {series_id}: {exc}"
                ) from exc
            except ValueError as exc:
                raise RuntimeError(
                    f"BLS no devolvió una respuesta JSON válida para {series_id}."
                ) from exc

            if data.get("status") != "REQUEST_SUCCEEDED":
                raise ValueError(
                    f"Error de BLS para {series_id}, "
                    f"{start}-{end}: {data.get('message', data)}"
                )

            series = data.get("Results", {}).get("series", [])

            if not series or "data" not in series[0]:
                raise ValueError(
                    f"Respuesta inesperada de BLS para "
                    f"{series_id}, {start}-{end}: {data}"
                )

            all_observations.extend(series[0]["data"])
            start = end + 1

        unique = {
            (row["year"], row["period"]): row
            for row in all_observations
            if isinstance(row, dict) and "year" in row and "period" in row
        }

        return sorted(
            unique.values(),
            key=lambda row: (row["year"], row["period"]),
        )

    @staticmethod
    def get_cpi() -> list[dict]:
        """Obtiene el CPI-U All Items de Estados Unidos."""
        return BlsClient._get_series(BlsClient.CPI_SERIES)

    @staticmethod
    def get_inflation() -> list[dict]:
        """Calcula la inflación interanual mensual a partir del CPI-U."""
        cpi_data = BlsClient.get_cpi()

        cpi_by_period = {}

        for row in cpi_data:
            if not isinstance(row, dict):
                continue

            period = str(row.get("period", ""))

            if not period.startswith("M") or period == "M13":
                continue

            try:
                year = int(row["year"])
                month = int(period[1:])
                value = float(row["value"])
            except (KeyError, TypeError, ValueError):
                continue

            if not 1 <= month <= 12:
                continue

            cpi_by_period[(year, month)] = value

        inflation_data = []

        for (year, month), current_value in sorted(cpi_by_period.items()):
            previous_value = cpi_by_period.get((year - 1, month))

            if previous_value is None or previous_value == 0:
                continue

            inflation_rate = (
                (current_value / previous_value) - 1
            ) * 100

            inflation_data.append({
                "year": str(year),
                "period": f"M{month:02d}",
                "value": f"{inflation_rate:.3f}",
            })

        return inflation_data

    @staticmethod
    def get_unemployment() -> list[dict]:
        """Obtiene la tasa de desempleo de Estados Unidos."""
        return BlsClient._get_series(BlsClient.UNEMPLOYMENT_SERIES)

    @staticmethod
    def get_interest_rate() -> list[dict]:
        """
        Stub compatible con ObservationService._FETCHER_REGISTRY.
        Los tipos de interés de EE. UU. no son publicados por BLS.
        """
        raise ValueError(
            "INTEREST_RATE no está disponible en BLS."
        )

    @staticmethod
    def get_industrial_production() -> list[dict]:
        """
        Stub compatible con ObservationService._FETCHER_REGISTRY.
        La producción industrial de EE. UU. no es publicada por BLS.
        """
        raise ValueError(
            "INDUSTRIAL_PRODUCTION no está disponible en BLS."
        )

    @staticmethod
    def get_retail_sales() -> list[dict]:
        """
        Stub compatible con ObservationService._FETCHER_REGISTRY.
        Las ventas minoristas de EE. UU. no son publicadas por BLS.
        """
        raise ValueError(
            "RETAIL_SALES no está disponible en BLS."
        )
