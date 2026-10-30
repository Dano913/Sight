# Informe de Auditoría y Corrección de Errores: `app/normalizers`

Este documento detalla los errores de parseo de fechas, vulnerabilidades ante banderas no numéricas de Eurostat/BLS, rigidez de códigos de serie en BEA e incompatibilidades con el formato real de la API de NBS China detectados y corregidos en `backend/app/normalizers/`.

---

## 1. Resumen Ejecutivo de Hallazgos

| ID | Normalizador Afectado | Error / Vulnerabilidad Detectada | Impacto en Producción | Estado |
|:---|:---|:---|:---|:---|
| **NRM-01** | [`EurostatNormalizer`](file:///home/dano/sight/backend/app/normalizers/eurostat_normalizer.py) | Confusión de columnas trimestrales (`"2024-Q1"`) y anuales (`"2024"`) en indicadores mensuales dentro de `_get_time_columns()` y `_parse_date()`. | `"2024-Q1"` tiene longitud 7 y contiene `"-"`, por lo que pasaba el filtro mensual y hacía que `int("Q1")` lanzara `ValueError: invalid literal for int() with base 10: 'Q1'`. Asimismo, una columna `"2024"` en un indicador mensual lanzaba `ValueError: not enough values to unpack`. | **Corregido y verificado** |
| **NRM-02** | [`EurostatNormalizer`](file:///home/dano/sight/backend/app/normalizers/eurostat_normalizer.py) | `_is_valid_value(value)` sólo comprobaba `value == value`, dando por válidas cadenas de texto como `":"`, `"c"` o `"e"` (banderas de dato faltante/confidencial de Eurostat) e infinitos (`inf`). | Al ejecutar `float(value)` sobre `":"`, se lanzaba `ValueError: could not convert string to float: ':'`, abortando la normalización completa del indicador. | **Corregido y verificado** |
| **NRM-03** | [`EurostatNormalizer`](file:///home/dano/sight/backend/app/normalizers/eurostat_normalizer.py) | Acceso rígido a `row["geo\\TIME_PERIOD"]` y a columnas de filtro sin verificar su presencia en `df.columns`. | `KeyError` cuando un dataset de Eurostat utilizaba la cabecera `"geo"` o `"geo\\time"`, o cuando una columna opcional de filtro no estaba en el DataFrame. | **Corregido y verificado** |
| **NRM-04** | [`BeaNormalizer`](file:///home/dano/sight/backend/app/normalizers/bea_normalizer.py) | `to_observations()` filtraba exclusivamente `SeriesCode == "A191RX"` y `LineNumber == "1"`, ignorando el parámetro `indicator_code`. | Al normalizar `EXPORTS` (`A020RX`) o `IMPORTS` (`A021RX`) desde BEA, descartaba el 100% de las filas y devolvía una lista vacía `[]`. | **Corregido y verificado** |
| **NRM-05** | [`BlsNormalizer`](file:///home/dano/sight/backend/app/normalizers/bls_normalizer.py) | Acceso sin guarda a `row["period"]` y `row["year"]`, y validación incompleta de mes (`if month > 12:` sin comprobar `month < 1`). | `KeyError` ante filas incompletas y `ValueError: month must be in 1..12` si aparecía un período `M00`, además de aceptar valores `"nan"` o `"inf"`. | **Corregido y verificado** |
| **NRM-06** | [`NbsNormalizer`](file:///home/dano/sight/backend/app/normalizers/nbs_normalizer.py) | 1. Llamada a `RegionService.get_region("CN")` sin fallback cuando `"CN"` no está en las 16 regiones base.<br>2. Iteración `for item in data:` asumiendo una lista plana, incompatible con el diccionario `{"returndata": {"datanodes": [...]}}` devuelto por `NbsClient`. | Llamar a `NbsNormalizer.to_observations()` fallaba siempre en la primera línea con `ValueError: Region 'CN' not found` y, tras ello, con `TypeError: string indices must be integers`. | **Corregido y verificado** |

---

## 2. Detalle Técnico de las Soluciones

### NRM-01 y NRM-02: Parseo Seguro de Columnas Temporales y Valores en `EurostatNormalizer`
* **Problema**:
  ```python
  # ❌ ANTES: "2024-Q1" tiene len == 7 y "-" in col, colándose como columna mensual
  if ("-" in str(column) and len(str(column)) == 7) or str(column).isdigit():
  ```
  Y en `_is_valid_value`:
  ```python
  # ❌ ANTES: ":" == ":" es True en Python, rompiendo float(":") más abajo
  return value == value
  ```
* **Solución**:
  1. Se implementó [`_is_monthly_column()`](file:///home/dano/sight/backend/app/normalizers/eurostat_normalizer.py#L106-L116) que excluye explícitamente `"-Q"` y verifica que tanto el año como el mes sean dígitos con `1 <= month <= 12`.
  2. [`_parse_date()`](file:///home/dano/sight/backend/app/normalizers/eurostat_normalizer.py#L143-L176) inspecciona el formato real de la cadena (`"-Q"`, `"-"`, `isdigit()`) con manejo seguro de excepciones.
  3. [`_is_valid_value()`](file:///home/dano/sight/backend/app/normalizers/eurostat_normalizer.py#L187-L196) convierte mediante `float(value)` dentro de un bloque `try / except` y exige `math.isfinite(numeric)`.

---

### NRM-04: Mapeo Multi-Indicador en `BeaNormalizer`
* **Solución**: Se añadió el diccionario [`SERIES_BY_INDICATOR`](file:///home/dano/sight/backend/app/normalizers/bea_normalizer.py#L14-L18) que asocia `"GDP"` a `("A191RX", "1")`, `"EXPORTS"` a `("A020RX", None)` e `"IMPORTS"` a `("A021RX", None)`, permitiendo normalizar las tres series macroeconómicas trimestrales de EE. UU. con conversión a miles de millones de USD (`BILLION_USD`).

---

### NRM-06: Soporte del Sobre JSON Nativo `returndata.datanodes` en `NbsNormalizer`
* **Solución**: [`NbsNormalizer.to_observations()`](file:///home/dano/sight/backend/app/normalizers/nbs_normalizer.py#L64-L163) soporta ahora tanto el diccionario devuelto por `NbsClient` (extrayendo nodos con `data.hasdata == True` y dimensión temporal `wdcode == "sj"` en formatos anual `YYYY`, trimestral `YYYYA..D` y mensual `YYYYMM`) como listas planas de diccionarios, e incorpora `_get_china_region()` con fallback seguro para la región `"CN"`.
