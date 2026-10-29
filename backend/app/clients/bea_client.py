import os
import requests


class BeaClient:
    BASE_URL = "https://apps.bea.gov/api/data"
    API_KEY = os.getenv("BEA_API_KEY")
    GDP_TABLE = "T10106"

    @staticmethod
    def get_gdp():
        if not BeaClient.API_KEY:
            raise RuntimeError("Falta la variable de entorno BEA_API_KEY.")

        params = {
            "UserID": BeaClient.API_KEY,
            "method": "GetData",
            "DataSetName": "NIPA",
            "TableName": BeaClient.GDP_TABLE,
            "Frequency": "Q",
            "Year": "ALL",
            "ResultFormat": "JSON",
        }

        try:
            response = requests.get(
                BeaClient.BASE_URL,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Error de conexión con el BEA: {exc}"
            ) from exc
        except requests.exceptions.JSONDecodeError as exc:
            raise RuntimeError(
                "El BEA no devolvió una respuesta JSON válida."
            ) from exc

        results = data.get("BEAAPI", {}).get("Results", {})

        if "Error" in results:
            raise RuntimeError(
                f"Error comunicado por el BEA: {results['Error']}"
            )

        rows = results.get("Data")
        if rows is None:
            raise ValueError(
                f"Respuesta inesperada del BEA: {data}"
            )

        observations = [
            row
            for row in rows
            if row.get("SeriesCode") == "A191RX"
            and row.get("LineNumber") == "1"
            and row.get("CL_UNIT") == "Level"
        ]

        if not observations:
            raise ValueError(
                "El BEA no devolvió observaciones del PIB real "
                "trimestral (A191RX)."
            )

        return observations