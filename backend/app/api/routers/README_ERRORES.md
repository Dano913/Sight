# Informe de Auditoría y Corrección de Errores: `app/api/routers`

Este documento detalla las vulnerabilidades de manejo de excepciones HTTP, fallos en cascada ante cobertura parcial de indicadores, incompatibilidades con indicadores sintéticos (`TRADE`), redirecciones `307 Temporary Redirect` innecesarias y errores SQLite detectados y corregidos en la capa de routers de FastAPI (`backend/app/api/routers/`).

---

## 1. Resumen Ejecutivo de Hallazgos

| ID | Router / Componente | Error / Vulnerabilidad Detectada | Impacto en Producción | Estado |
|:---|:---|:---|:---|:---|
| **RT-01** | [`query.py`](file:///home/dano/sight/backend/app/api/routers/query.py) | Ausencia total de captura de `ValueError` en los 4 endpoints de `/query`, más error de sintaxis SQLite `IN ()` en `ObservationRepository.get_by_regions_and_indicator()` cuando `regions` estaba vacío. | Cualquier consulta de una región o indicador sin datos lanzaba un `500 Internal Server Error` no controlado en lugar de `404 Not Found` (o `400 Bad Request`). | **Corregido y verificado** |
| **RT-02** | [`investment.py`](file:///home/dano/sight/backend/app/api/routers/investment.py) | Bucle sobre `INVESTMENT_INDICATORS` sin `try / except ValueError` por indicador ni validación de lista vacía. | Si un país carecía de uno solo de los 6 indicadores (e.g. `HOUSE_PRICE_INDEX` en `US`), todo el endpoint `GET /investment/{region_code}` caía con `500 Internal Server Error`, rompiendo el componente `AssetRanking` del frontend. | **Corregido y verificado** |
| **RT-03** | [`analysis.py`](file:///home/dano/sight/backend/app/api/routers/analysis.py), [`observations.py`](file:///home/dano/sight/backend/app/api/routers/observations.py) | Llamada directa a `ObservationService.get_observations()` sin soporte para el indicador sintético `TRADE`. | Al consultar `/analysis/features/TRADE/EU27_2020`, `/analysis/cycle/TRADE/EU27_2020` o `/analysis/investment/TRADE/EU27_2020`, el servidor devolvía error `500` (`ValueError: Indicador no soportado: TRADE`). | **Corregido y verificado** |
| **RT-04** | [`analysis.py`](file:///home/dano/sight/backend/app/api/routers/analysis.py) | Conversión de `ValueError` de `IndicatorService` / `ObservationService` en `500 Internal Server Error` dentro de `get_cycle_analysis` y `get_feature_analysis`. | Indicadores o regiones inexistentes devolvían `500` con traza de pila en consola en vez de `404 Not Found`; errores de validación devolvían `500` en vez de `400 Bad Request`. | **Corregido y verificado** |
| **RT-05** | [`analysis.py`](file:///home/dano/sight/backend/app/api/routers/analysis.py) (`get_feature_analysis`) | Construcción de `pd.Series` sin desduplicar marcas temporales (`.groupby(level=0).last()`). | Si existían observaciones de múltiples fuentes para la misma fecha, el índice temporal contenía fechas duplicadas al entrar en `FeatureEngine.compute()`. | **Corregido y verificado** |
| **RT-06** | [`regions.py`](file:///home/dano/sight/backend/app/api/routers/regions.py), [`sources.py`](file:///home/dano/sight/backend/app/api/routers/sources.py), [`indicators.py`](file:///home/dano/sight/backend/app/api/routers/indicators.py) | Inconsistencia en rutas raíz (`@router.get("/")` en `regions.py` y `sources.py` frente a `@router.get("")` en `indicators.py`). | Cada petición del frontend a `GET /regions` provocaba un `307 Temporary Redirect` hacia `/regions/`, duplicando la latencia de red al cargar el Dashboard y el detalle de indicadores. | **Corregido y verificado** |
| **RT-07** | [`bea.py`](file:///home/dano/sight/backend/app/api/routers/bea.py), [`bls.py`](file:///home/dano/sight/backend/app/api/routers/bls.py), [`nbs.py`](file:///home/dano/sight/backend/app/api/routers/nbs.py) | Invocación de clientes HTTP externos sin manejo de errores. | La falta de una API key o un timeout del proveedor externo generaba una excepción no controlada en vez de `400 Bad Request` o `502 Bad Gateway`. | **Corregido y verificado** |
| **RT-08** | [`observations.py`](file:///home/dano/sight/backend/app/api/routers/observations.py), [`query.py`](file:///home/dano/sight/backend/app/api/routers/query.py), [`analysis.py`](file:///home/dano/sight/backend/app/api/routers/analysis.py), [`api/__init__.py`](file:///home/dano/sight/backend/app/api/__init__.py) | Trazas `print()` y `traceback.print_exc()` en producción y archivos `__init__.py` vacíos. | Contaminación de la salida estándar del servidor y ausencia de contratos de exportación en el paquete `app.api`. | **Corregido y verificado** |

---

## 2. Detalle Técnico de las Soluciones

### RT-02: Resiliencia Multi-Indicador en `GET /investment/{region_code}`
* **Problema**: En [`investment.py`](file:///home/dano/sight/backend/app/api/routers/investment.py), el endpoint iteraba sobre `INVESTMENT_INDICATORS` sin capturar `ValueError`:
  ```python
  # ❌ ANTES: Si falta 1 indicador en la región, falla todo el endpoint con 500
  for indicator_code in INVESTMENT_INDICATORS:
      observations.extend(
          ObservationService.get_observations(
              indicator_code=indicator_code,
              region_code=region_code.upper(),
          )
      )
  ```
* **Solución**: Se alineó con el patrón tolerante a fallos de `get_macro_regime`, capturando `ValueError` individualmente por cada indicador y lanzando `404 Not Found` únicamente cuando ningún indicador de la cesta tiene datos para la región solicitada.

---

### RT-03 y RT-04: Helper Unificado `_get_observations_for_analysis` en `analysis.py`
* **Problema**: `get_cycle_analysis`, `get_feature_analysis` y `get_investment_analysis` duplicaban la lógica de carga de observaciones, omitían el soporte para el indicador sintético `TRADE` y capturaban los `ValueError` de `IndicatorService.get_indicator()` dentro de `except Exception`, devolviendo `500 Internal Server Error` cuando se solicitaba un indicador inexistente.
* **Solución**: Se creó [`_get_observations_for_analysis(indicator_code, region_code)`](file:///home/dano/sight/backend/app/api/routers/analysis.py#L29-L73) que:
  1. Valida primero la existencia del indicador en `IndicatorService.get_indicator()`, devolviendo `404 Not Found` inmediato si no existe.
  2. Si `clean_indicator == "TRADE"`, delega en `QueryService._compute_trade_observations(region_code=clean_region)`.
  3. En caso contrario, invoca `ObservationService.get_observations()`, traduciendo cualquier ausencia de datos a `404 Not Found`.

---

### RT-01: Blindaje de `/query` y `ObservationRepository.get_by_regions_and_indicator`
* **Problema**:
  1. En [`query.py`](file:///home/dano/sight/backend/app/api/routers/query.py), las excepciones `ValueError` lanzadas por `QueryService` no se interceptaban.
  2. En `GET /query/compare?indicator=GDP&regions=`, pasar una cadena vacía o de sólo comas generaba una lista vacía `region_codes = []` y ejecutaba `WHERE indicator_code = ? AND region_code IN ()`, provocando `sqlite3.OperationalError: near ")": syntax error`.
* **Solución**:
  1. Se añadió guarda temprana `if not region_codes: return []` en [`ObservationRepository.get_by_regions_and_indicator`](file:///home/dano/sight/backend/app/repositories/observation_repository.py#L266-L273).
  2. Se validó en [`compare()`](file:///home/dano/sight/backend/app/api/routers/query.py#L72-L102) que tanto `indicator` como `region_list` no estén vacíos (`400 Bad Request`) y se tradujeron los `ValueError` de `QueryService` a `404 Not Found`.

---

### RT-06: Eliminación de Redirecciones `307 Temporary Redirect` en `/regions` y `/sources`
* **Problema**: FastAPI distingue entre `@router.get("")` (`/regions`) y `@router.get("/")` (`/regions/`). Como el frontend invoca `client.get("/regions")`, FastAPI respondía con un `307 Temporary Redirect` hacia `http://localhost:8000/regions/`, obligando al navegador a realizar dos peticiones HTTP seguidas.
* **Solución**: En [`regions.py`](file:///home/dano/sight/backend/app/api/routers/regions.py), [`sources.py`](file:///home/dano/sight/backend/app/api/routers/sources.py) e [`indicators.py`](file:///home/dano/sight/backend/app/api/routers/indicators.py), se registraron ambos decoradores (`@router.get("")` como ruta canónica y `@router.get("/", include_in_schema=False)` como alias compatible), respondiendo directamente con `200 OK` en una sola petición.

---

## 3. Verificación Automatizada

Se creó la suite de pruebas [`tests/unit/api/test_routers.py`](file:///home/dano/sight/backend/tests/unit/api/test_routers.py) con `fastapi.testclient.TestClient`, verificando:
- Respuestas directas `200 OK` sin redirecciones `307` en `/regions`, `/sources` e `/indicators`.
- Respuestas `404 Not Found` y `400 Bad Request` en `/query/*`, `/observations/*`, `/analysis/*` e `/investment/*`.
- Soporte completo del indicador sintético `TRADE` en `/observations/TRADE`, `/analysis/features/TRADE/EU27_2020`, `/analysis/cycle/TRADE/EU27_2020` y `/analysis/investment/TRADE/EU27_2020`.
- Resiliencia de `/investment/{region_code}` cuando sólo un subconjunto de indicadores está disponible para el país consultado.
