# Informe de Auditoría y Corrección de Errores: `app/clients`

Este documento registra las incidencias de métodos faltantes en el registro de ingesta, evaluación prematura de variables de entorno, manejo de errores de red en llamadas HTTP y protección frente a DataFrames vacíos detectadas y corregidas en `backend/app/clients/`.

---

## 1. Resumen Ejecutivo de Hallazgos

| ID | Cliente Afectado | Error / Vulnerabilidad Detectada | Impacto en Producción | Estado |
|:---|:---|:---|:---|:---|
| **CLI-01** | [`BeaClient`](file:///home/dano/sight/backend/app/clients/bea_client.py), [`BlsClient`](file:///home/dano/sight/backend/app/clients/bls_client.py) | Métodos declarados en `ObservationService._FETCHER_REGISTRY` inexistentes en las clases (`BeaClient.get_exports`, `BeaClient.get_imports`, `BlsClient.get_interest_rate`, `BlsClient.get_industrial_production`, `BlsClient.get_retail_sales`). | Invocar `getattr(client_cls, method_name)` lanzaba `AttributeError` inmediato para 5 indicadores del catálogo. | **Corregido y verificado** |
| **CLI-02** | [`BeaClient`](file:///home/dano/sight/backend/app/clients/bea_client.py), [`BlsClient`](file:///home/dano/sight/backend/app/clients/bls_client.py) | Evaluación estática de `API_KEY = os.getenv(...)` únicamente en tiempo de importación de clase. | Si las variables de entorno se cargaban después de importar el módulo o se inyectaban en tests con `monkeypatch.setenv`, el cliente seguía viendo `API_KEY = None` y lanzaba `RuntimeError`. | **Corregido y verificado** |
| **CLI-03** | [`BlsClient`](file:///home/dano/sight/backend/app/clients/bls_client.py) | Llamadas `requests.post()` y `response.json()` sin bloques `try / except requests.RequestException` ni `ValueError` en `_get_series()`. | Un fallo de red, timeout o respuesta HTML del balanceador de BLS provocaba excepciones crudas de `requests` en lugar de un `RuntimeError` controlado. | **Corregido y verificado** |
| **CLI-04** | [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | Acceso directo a `df["stk_flow"]` y `df["indic_et"]` sin verificar si `eurostat.get_data_df()` devolvió `None` o un DataFrame vacío. | Caída con `TypeError: 'NoneType' object is not subscriptable` o `KeyError` cuando Eurostat devolvía un resultado vacío. | **Corregido y verificado** |
| **CLI-05** | [`tests/test_eurostat.py`](file:///home/dano/sight/backend/tests/test_eurostat.py) | Ejecución de `df = EurostatClient.get_trade()` en el ámbito global del módulo sin guarda `if __name__ == "__main__":`. | Cada ejecución de `pytest` realizaba una descarga real por internet contra Eurostat durante la fase de recolección de tests, añadiendo ~3 segundos de latencia y dependencia de red. | **Corregido y verificado** |

---

## 2. Detalle Técnico de las Soluciones

### CLI-01: Implementación de Series de Comercio Exterior en `BeaClient` y Métodos de Contrato en `BlsClient`
* **Problema**: `ObservationService._FETCHER_REGISTRY` registraba a `BeaClient` como proveedor de `EXPORTS` (`get_exports`) e `IMPORTS` (`get_imports`), pero `BeaClient` sólo implementaba `get_gdp()`. Asimismo, registraba a `BlsClient` en `INTEREST_RATE`, `INDUSTRIAL_PRODUCTION` y `RETAIL_SALES`.
* **Solución**:
  1. En [`BeaClient`](file:///home/dano/sight/backend/app/clients/bea_client.py), se refactorizó la extracción de la tabla NIPA `T10106` en `_fetch_nipa_series(series_code, line_number)` y se implementaron `get_exports()` (`SeriesCode="A020RX"`) y `get_imports()` (`SeriesCode="A021RX"`).
  2. En [`BlsClient`](file:///home/dano/sight/backend/app/clients/bls_client.py), se añadieron los métodos de contrato `get_interest_rate()`, `get_industrial_production()` y `get_retail_sales()` que lanzan un `ValueError` descriptivo compatible con el flujo de captura de `ObservationService`.

### CLI-02 y CLI-03: Resolución Dinámica de Credenciales y Blindaje HTTP
* **Solución**: Tanto [`BeaClient._get_api_key()`](file:///home/dano/sight/backend/app/clients/bea_client.py#L19-L23) como [`BlsClient._get_api_key()`](file:///home/dano/sight/backend/app/clients/bls_client.py#L28-L35) evalúan `cls.API_KEY or os.getenv(...)` en tiempo de ejecución, y `_get_series()` en `BlsClient` captura `requests.RequestException` y errores de decodificación JSON.
