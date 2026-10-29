"""
Cliente para la API no oficial de la NBS (National Bureau of Statistics of China).

Endpoint: https://data.stats.gov.cn/english/easyquery.htm

Notas importantes:
- Esta API no es oficial ni está documentada por la NBS para uso externo.
- La NBS puede restringir o limitar el acceso desde IPs fuera de China
  (rate limiting, timeouts o bloqueos del WAF). Este cliente incluye
  reintentos con backoff exponencial para mitigar (no eliminar) ese riesgo.
- Si el bloqueo persiste, considera usar como fallback datos de OCDE /
  Banco Mundial para China, ya integrados en el resto de la plataforma.
"""

import time
import random
import logging
from typing import Optional

import requests

logger = logging.getLogger("nbs_client")
logging.basicConfig(level=logging.INFO)


class NbsClientError(Exception):
    """Error genérico al consultar la API de la NBS."""


class NbsClient:

    HOME_URL = "https://data.stats.gov.cn/english/"
    BASE_URL = "https://data.stats.gov.cn/english/easyquery.htm"

    _session: Optional[requests.Session] = None

    # Códigos de indicador (zb) en la base de datos anual (hgnd)
    CPI_DATASET = "A0901"
    GDP_DATASET = "A0201"
    UNEMPLOYMENT_DATASET = "A0302"
    INFLATION_DATASET = "A0902"

    # Varios User-Agents para rotar en cada intento
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36",
    ]

    MAX_RETRIES = 4
    BASE_BACKOFF_SECONDS = 1.5
    REQUEST_TIMEOUT = 20
    MIN_DELAY_BETWEEN_CALLS = 1.5  # rate limiting básico entre llamadas

    _last_call_ts: float = 0.0

    @staticmethod
    def _timestamp_ms() -> str:
        return str(int(time.time() * 1000))

    @classmethod
    def _headers(cls) -> dict:
        return {
            "User-Agent": random.choice(cls.USER_AGENTS),
            "Accept": "application/json,text/javascript,*/*;q=0.01",
            "Referer": "https://data.stats.gov.cn/english/",
            "X-Requested-With": "XMLHttpRequest",
        }

    @classmethod
    def _respect_rate_limit(cls) -> None:
        elapsed = time.time() - cls._last_call_ts
        if elapsed < cls.MIN_DELAY_BETWEEN_CALLS:
            time.sleep(cls.MIN_DELAY_BETWEEN_CALLS - elapsed)

    @classmethod
    def _get_session(cls) -> requests.Session:
        """
        Crea (una sola vez) una sesión que primero visita la página HTML
        normal para obtener cookies, simulando el flujo de un navegador
        antes de llamar al endpoint de datos. Sin esto, el WAF de la NBS
        puede rechazar la petición directa a easyquery.htm con un 403
        (reason:UrlACL), independientemente de los headers usados.
        """
        if cls._session is not None:
            return cls._session

        session = requests.Session()
        try:
            session.get(
                cls.HOME_URL,
                headers=cls._headers(),
                timeout=cls.REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.warning("No se pudo precargar cookies desde %s: %s", cls.HOME_URL, exc)

        cls._session = session
        return session

    @classmethod
    def _query(cls, dataset_code: str, dbcode: str = "hgnd") -> dict:
        """
        Consulta un indicador en la NBS con reintentos y backoff exponencial.

        Lanza NbsClientError si tras todos los reintentos no se obtiene
        una respuesta JSON válida.
        """
        params = {
            "m": "QueryData",
            "dbcode": dbcode,
            "rowcode": "zb",
            "colcode": "sj",
            "wds": "[]",
            "dfwds": f'[{{"wdcode":"zb","valuecode":"{dataset_code}"}}]',
            "k1": cls._timestamp_ms(),
        }

        last_error: Optional[Exception] = None

        for attempt in range(1, cls.MAX_RETRIES + 1):
            cls._respect_rate_limit()
            cls._last_call_ts = time.time()

            try:
                session = cls._get_session()
                response = session.get(
                    cls.BASE_URL,
                    params=params,
                    headers=cls._headers(),
                    timeout=cls.REQUEST_TIMEOUT,
                )

                # Bloqueo / rate limiting explícito del servidor
                if response.status_code in (403, 429, 503):
                    raise NbsClientError(
                        f"Bloqueo del servidor (HTTP {response.status_code}): "
                        f"{response.text[:200]!r}"
                    )

                response.raise_for_status()

                # A veces el bloqueo devuelve HTML (WAF) en vez de JSON
                try:
                    data = response.json()
                except ValueError:
                    raise NbsClientError(
                        "Respuesta no es JSON válido (posible bloqueo del WAF "
                        "o página de restricción de acceso)"
                    )

                logger.info(
                    "NBS OK: dataset=%s intento=%d/%d",
                    dataset_code, attempt, cls.MAX_RETRIES,
                )
                return data

            except (requests.RequestException, NbsClientError) as exc:
                last_error = exc
                wait = cls.BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
                wait += random.uniform(0, 0.5)  # jitter
                logger.warning(
                    "NBS fallo (intento %d/%d) dataset=%s: %s. "
                    "Reintentando en %.1fs...",
                    attempt, cls.MAX_RETRIES, dataset_code, exc, wait,
                )
                if attempt < cls.MAX_RETRIES:
                    time.sleep(wait)

        raise NbsClientError(
            f"No se pudo obtener el dataset {dataset_code} tras "
            f"{cls.MAX_RETRIES} intentos. Último error: {last_error}"
        )

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------

    @classmethod
    def get_cpi(cls) -> dict:
        """Obtiene el CPI (índice de precios al consumo) de China."""
        return cls._query(cls.CPI_DATASET)

    @classmethod
    def get_gdp(cls) -> dict:
        """Obtiene el GDP (PIB) de China."""
        return cls._query(cls.GDP_DATASET)

    @classmethod
    def get_unemployment(cls) -> dict:
        """Obtiene la tasa de desempleo de China."""
        return cls._query(cls.UNEMPLOYMENT_DATASET)

    @classmethod
    def get_inflation(cls) -> dict:
        """Obtiene la inflación de China."""
        return cls._query(cls.INFLATION_DATASET)


if __name__ == "__main__":
    # Uso de ejemplo. Si la NBS bloquea la IP, verás NbsClientError
    # tras agotar los reintentos: en ese caso, usa un fallback (OCDE/Banco Mundial).
    for name, fn in [
        ("CPI", NbsClient.get_cpi),
        ("GDP", NbsClient.get_gdp),
        ("Unemployment", NbsClient.get_unemployment),
        ("Inflation", NbsClient.get_inflation),
    ]:
        try:
            result = fn()
            print(f"\n===== NBS CHINA {name.upper()} =====")
            print(result)
        except NbsClientError as e:
            print(f"\n===== NBS CHINA {name.upper()} FALLÓ =====")
            print(e)