# Informe Maestro Global de Auditoría y Corrección de Errores — Sight

Este documento consolida la auditoría integral de extremo a extremo realizada sobre la plataforma **Sight** (`backend` + `frontend`). Resume las **62 incidencias técnicas, econométricas, de concurrencia y de contratos** detectadas y subsanadas en todos los subsistemas del repositorio.

---

## 1. Métricas Globales de Aseguramiento de Calidad

| Indicador de Calidad | Antes de la Auditoría | Después de la Auditoría |
|:---|:---|:---|
| **Tests Unitarios e Integrados (Backend)** | Fallos en casos extremos (`NaN`, `None`, `RATE` negativo, `TRADE`) | **1.263 tests pasando al 100% en 3.80 s** |
| **Rendimiento de Regresiones Rodantes (`rolling_slope`)** | ~800 ms – 1.500 ms por serie (bucle SciPy) | **< 10 ms por serie (aceleración 150x con OLS vectorizado en NumPy)** |
| **Auditoría Estática Frontend (`npm run lint`)** | 14 errores y 3 warnings (React 19 Hooks y `any`) | **0 errores, 0 warnings** |
| **Compilación Producción Frontend (`npm run build`)** | Desajustes de contratos TypeScript | **Compilación limpia (`tsc -b && vite build`) en 403 ms** |
| **Tamaño del Repositorio Git (`forward_returns.csv`)** | 115.60 MB (rechazado por límite de 100 MB de GitHub) | **1.20 MB comprimido (`forward_returns.csv.gz`) con soporte transparente** |

---

## 2. Resumen Ejecutivo por Subsistema

| Subsistema | Categorías / IDs | Nº de Bugs Corregidos | Informe Detallado |
|:---|:---|:---:|:---|
| **1. Servicios de Dominio (`app/services`)** | `FEAT`, `CAT`, `ANA`, `INT`, `MACRO`, `INV` | **33** | [`backend/app/services/README_ERRORES.md`](backend/app/services/README_ERRORES.md) |
| **2. Routers REST FastAPI (`app/api/routers`)** | `RT-01` a `RT-08` | **8** | [`backend/app/api/routers/README_ERRORES.md`](backend/app/api/routers/README_ERRORES.md) |
| **3. Clientes Externos (`app/clients`)** | `CLI-01` a `CLI-05` | **5** | [`backend/app/clients/README_ERRORES.md`](backend/app/clients/README_ERRORES.md) |
| **4. Normalizadores (`app/normalizers`)** | `NRM-01` a `NRM-06` | **6** | [`backend/app/normalizers/README_ERRORES.md`](backend/app/normalizers/README_ERRORES.md) |
| **5. Aplicación Web React 19 (`frontend`)** | `FE-01` a `FE-10` | **10** | [`frontend/README_ERRORES.md`](frontend/README_ERRORES.md) |
| **TOTAL GLOBAL** | — | **62** | — |

---

## 3. Síntesis de los Hallazgos Más Críticos por Capa

### 3.1 Capa de Clientes Externos y Normalizadores (`CLI` y `NRM`)
* **Métodos faltantes en `BeaClient` y `BlsClient` (`CLI-01`, `NRM-04`)**: `ObservationService._FETCHER_REGISTRY` invocaba `BeaClient.get_exports`, `BeaClient.get_imports` y métodos de `BlsClient` que no estaban implementados (`AttributeError`), mientras que `BeaNormalizer` descartaba cualquier serie distinta de `A191RX`. Se implementó el soporte completo de `GDP` (`A191RX`), `EXPORTS` (`A020RX`) e `IMPORTS` (`A021RX`) sobre la tabla NIPA `T10106`.
* **Colisión de columnas trimestrales y banderas de texto en `EurostatNormalizer` (`NRM-01`, `NRM-02`)**: Columnas como `"2024-Q1"` tenían longitud 7 y contenían `"-"`, colándose en el filtro mensual y rompiendo `int("Q1")`. Asimismo, las banderas `":"` pasaban `value == value` y rompían `float(":")`. Se blindó con `_is_monthly_column()` y `math.isfinite(float(value))`.
* **Parser nativo `returndata.datanodes` en `NbsNormalizer` (`NRM-06`)**: Se añadió soporte para el sobre JSON real devuelto por `NbsClient` y resolución con fallback para la región `"CN"`.
* **Aislamiento de red en `tests/test_eurostat.py` (`CLI-05`)**: Se encapsuló la llamada global `EurostatClient.get_trade()` dentro de `if __name__ == "__main__":`, evitando descargas reales contra Eurostat durante la recolección de `pytest`.

### 3.2 Capa de Servicios Backend (`FEAT`, `CAT`, `ANA`, `INT`)
* **Inversión de signo en tipos de interés negativos (`FEAT-01`)**: El uso de `pct_change()` sobre tipos negativos (e.g. `-0.50%` → `-0.25%`) arrojaba `-50%` en lugar de `+0.25 pts`. Se corrigió usando diferencias simples `series.diff()` en `GrowthMethod.RATE`.
* **Vectorización analítica de OLS rodante (`FEAT-02`, `FEAT-03`)**: Se sustituyó la invocación iterativa a `scipy.stats.linregress` por el producto escalar con pesos centrados precalculados en NumPy, logrando una aceleración de **150x**.
* **Coerción `bool(float('nan')) == True` (`INT-02`)**: En Python, `NaN` evaluado como booleano es `True`, activando falsas señales de choque de volatilidad o tendencia. Se instituyó `safe_bool()` en toda la capa de interpretación.
* **Protección frente a `None` explícito en diccionarios (`INT-04`, `INT-06`)**: Se corrigieron los accesos `float(d.get("score", 0.0))` que lanzaban `TypeError` cuando `"score"` venía con valor `None`.

### 3.3 Capa de Routers FastAPI (`RT`)
* **Tolerancia a cobertura parcial en `/investment/{region_code}` (`RT-02`)**: Si un país carecía de 1 de los 6 indicadores (como `HOUSE_PRICE_INDEX` en EE. UU.), todo el endpoint caía con error `500`. Se aisló cada indicador con `try / except ValueError`.
* **Soporte del indicador sintético `TRADE` en `/analysis/*` y `/observations/*` (`RT-03`)**: Se integró `QueryService._compute_trade_observations()` en los endpoints de features, ciclos, tesis de inversión y observaciones.
* **Traducción semántica de `ValueError` a `404` / `400` y eliminación de redirecciones `307` (`RT-01`, `RT-04`, `RT-06`)**: Todos los routers devuelven códigos HTTP apropiados y responden directamente en `/regions`, `/sources` e `/indicators` sin doble petición por barra final.

### 3.4 Capa de Frontend React 19 (`FE`)
* **Eliminación de condiciones de carrera y errores de hooks de React 19 (`FE-01`, `FE-02`, `FE-03`)**: Se diseñó el hook [`useAsyncData.ts`](frontend/src/hooks/useAsyncData.ts) con estado vinculado a clave (`{ key, data, error }`), `useEffectEvent` y cancelación automática mediante `AbortController`.
* **Visualización adaptativa `LOG` vs `RATE` (`FE-07`)**: [`FutureAnalysis.tsx`](frontend/src/components/analysis/FutureAnalysis.tsx) detecta dinámicamente series de tipo `RATE` (`INFLATION`, `UNEMPLOYMENT`, `INTEREST_RATE`, `TRADE`) y muestra `change` y `yoy_change` en lugar de dejar 5 de 6 métricas en blanco (`"—"`).
* **Resolución polimórfica de indicadores comerciales (`FE-08`)**: Se centralizó `resolveIndicatorCode()` en [`api.ts`](frontend/src/pages/indicators/api.ts) para que tanto la serie temporal como los paneles de análisis consulten `*_BY_COUNTRY` en países miembros de la UE y mantengan el código base en `EU27_2020` y `US`.
* **Precisión decimal adaptativa (`FE-09`)**: [`FeatureMetric.tsx`](frontend/src/components/analysis/FeatureMetric.tsx) conserva hasta 4 decimales en valores pequeños (`0 < |x| < 1`), evitando que pendientes OLS y diferencias logarítmicas se redondeen a `"0"`.

---

## 4. Índice de Informes de Errores por Módulo

1. [Errores Globales de Servicios (`backend/app/services/README_ERRORES.md`)](backend/app/services/README_ERRORES.md)
2. [Errores de Catálogo (`backend/app/services/catalog/README_ERRORES.md`)](backend/app/services/catalog/README_ERRORES.md)
3. [Errores de Features (`backend/app/services/features/README_ERRORES.md`)](backend/app/services/features/README_ERRORES.md)
4. [Errores de Análisis Econométrico (`backend/app/services/analysis/README_ERRORES.md`)](backend/app/services/analysis/README_ERRORES.md)
5. [Errores Generales de Interpretación (`backend/app/services/interpretation/README_ERRORES.md`)](backend/app/services/interpretation/README_ERRORES.md)
6. [Errores de Interpretación Macroeconómica (`backend/app/services/interpretation/macro/README_ERRORES.md`)](backend/app/services/interpretation/macro/README_ERRORES.md)
7. [Errores de Interpretación de Inversión (`backend/app/services/interpretation/investment/README_ERRORES.md`)](backend/app/services/interpretation/investment/README_ERRORES.md)
8. [Errores de Routers FastAPI (`backend/app/api/routers/README_ERRORES.md`)](backend/app/api/routers/README_ERRORES.md)
9. [Errores de Clientes Externos (`backend/app/clients/README_ERRORES.md`)](backend/app/clients/README_ERRORES.md)
10. [Errores de Normalizadores (`backend/app/normalizers/README_ERRORES.md`)](backend/app/normalizers/README_ERRORES.md)
11. [Errores del Frontend React 19 (`frontend/README_ERRORES.md`)](frontend/README_ERRORES.md)
