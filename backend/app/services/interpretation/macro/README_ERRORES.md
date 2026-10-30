# Informe de Auditoría y Corrección de Errores: `interpretation/macro`

Este documento detalla todas las anomalías, vulnerabilidades ante excepciones no controladas y fallos sutiles de tipo identificados y subsanados en el submódulo `app/services/interpretation/macro` y sus módulos de soporte.

---

## 1. Resumen Ejecutivo de Hallazgos

| ID | Componente Afectado | Tipo de Error | Impacto | Estado |
|:---|:---|:---|:---|:---|
| **MACRO-01** | `growth_interpreter.py` | `KeyError` no capturado | Crash al evaluar series que carecen de columna de variación explícita o con data parcial. | **Corregido y verificado** |
| **MACRO-02** | `utils.py`, `economic_interpretation_service.py` | Coerción errónea en Python (`bool(np.nan) == True`) | Señales ausentes o nulas (`NaN`) se evaluaban como señales activas (`True`). | **Corregido y verificado** |
| **MACRO-03** | `trend_interpreter.py`, `momentum_interpreter.py`, `volatility_interpreter.py`, `position_interpreter.py` | Indexación estricta de diccionarios / Series | `KeyError` cuando se analizan series temporales con métricas parciales o ventanas incompletas. | **Corregido y verificado** |
| **MACRO-04** | `cycle_interpretation_service.py` | `TypeError` en conversión `float(None)` | Fallo catastrófico al procesar ciclos detectados con valores nulos en `score`, `period_years` o `confidence`. | **Corregido y verificado** |
| **MACRO-05** | `transition_detector.py`, `regime_classifier.py`, `assessment_builder.py` | `AttributeError` por argumentos `None` | Crash del pipeline si un intérprete anterior falla o devuelve un contexto nulo. | **Corregido y verificado** |
| **MACRO-06** | `interpretation/`, `interpretation/macro/` | Ausencia de inicialización de paquete (`__init__.py`) | Dificultad de importación limpia, tipado estático deficiente y ausencia de contrato `__all__`. | **Corregido y verificado** |
| **MACRO-07** | `test_growth_interpreter.py` | Rama de ejecución no cubierta | Rama `is_rate=True` y `growth_rate_state="not_applicable"` sin tests unitarios. | **Corregido y verificado** |

---

## 2. Detalle de Errores y Soluciones Técnicas

### MACRO-01: Excepción `KeyError: 'percentage_change'` en `GrowthInterpreter`
* **Causa**: `REQUIRED_FEATURES` no exige de forma obligatoria `percentage_change` porque las series tipo `RATE` generan `change`. La lógica evaluaba:
  ```python
  is_rate = ("percentage_change" not in features.index and "change" in features.index)
  if is_rate:
      variation = safe_float(features["change"])
  else:
      variation = safe_float(features["percentage_change"])  # <-- KeyError si ninguna está presente
  ```
* **Solución**: Se sustituyó el acceso estricto por `features.get("change")` y `features.get("percentage_change")`. Si ninguna columna de variación está presente, `variation` evalúa limpiamente a `None` y `growth_rate_state` a `"unknown"` sin romper el servicio.

---

### MACRO-02: Coerción Booleana de `NaN` en Python (`safe_bool`)
* **Causa**: En Python estándar, `bool(float('nan'))` evalúa a `True`. Cuando un indicador temporal contenía valores nulos en alguna columna de señales generadas (`latest_signals[column] = np.nan`), el generador de respuestas serializaba esa señal como activa (`True`), generando falsos positivos en regímenes y alertas de riesgo.
* **Solución**: Se implementó la función auxiliar [`safe_bool`](file:///home/dano/sight/backend/app/services/interpretation/utils.py):
  ```python
  def safe_bool(value: Any) -> bool:
      if value is None:
          return False
      try:
          if pd.isna(value):
              return False
      except (TypeError, ValueError):
          pass
      return bool(value)
  ```
  Se aplicó en `EconomicInterpretationService` y en todas las extracciones de señales de los intérpretes estructurales.

---

### MACRO-03: Indexación Estricta en Intérpretes Estructurales
* **Causa**: `TrendInterpreter`, `MomentumInterpreter`, `VolatilityInterpreter` y `PositionInterpreter` accedían a los atributos de la serie mediante `features["rolling_slope_short"]` o `features["rolling_volatility"]`. Ante series con horizontes temporales reducidos o inicializaciones parciales, se levantaban excepciones `KeyError`.
* **Solución**: Se generalizó el uso de `.get()` con fallback seguro a `None` (filtrado posteriormente por `safe_float()`) y `safe_bool()` para flags de señales.

---

### MACRO-04: Excepción `TypeError` en Conversión `float(None)` en `CycleInterpretationService`
* **Causa**: En Python, `dict.get("key", default)` solo aplica el valor por defecto si la clave **no existe**, pero si la clave existe con valor `None`, devuelve `None`:
  ```python
  score = float(cycle.get("score", 0.0))  # Si cycle = {"score": None} -> float(None) -> TypeError!
  ```
* **Solución**: Se blindó la extracción mediante el patrón `cycle.get("score") or 0.0`:
  ```python
  score = float(cycle.get("score") or 0.0)
  confidence = cycle.get("confidence") or "BAJA"
  period = float(cycle.get("period_years") or 0.0)
  cycles_observable = float(cycle.get("cycles_observable") or 0.0)
  method_count = int(cycle.get("method_count") or 0)
  ```
  Adicionalmente se añadió validación de tipo en `best_cycle` para retornar de inmediato `_no_cycle_interpretation` si no es un diccionario válido.

---

### MACRO-05: Excepción `AttributeError` por Argumentos `None`
* **Causa**: Si `TransitionDetector.detect()`, `RegimeClassifier.classify()` o `AssessmentBuilder.build()` recibían `growth=None` o `transition=None` ante un fallo preliminar de un submódulo, la invocación de `growth.get(...)` levantaba `AttributeError: 'NoneType' object has no attribute 'get'`.
* **Solución**: Se implementó una inicialización defensiva al comienzo de cada método:
  ```python
  growth = growth or {}
  trend = trend or {}
  momentum = momentum or {}
  volatility = volatility or {}
  position = position or {}
  transition = transition or {}
  ```

---

### MACRO-06: Creación de Archivos de Paquete `__init__.py`
* **Causa**: Ni `app/services/interpretation` ni `app/services/interpretation/macro` contaban con `__init__.py`.
* **Solución**: Se crearon ambos archivos exportando con `__all__` los servicios, intérpretes y utilidades principales.

---

### MACRO-07: Pruebas Unitarias para Cobertura al 100%
* **Causa**: La lógica de tipos de interés `is_rate=True` y la ausencia de columnas de variación carecían de tests dedicados en `test_growth_interpreter.py`.
* **Solución**: Se añadieron `test_rate_series_interpretation_with_change_column` y `test_missing_variation_columns_does_not_crash`, alcanzando el 100% de cobertura en `growth_interpreter.py`. Se añadieron igualmente pruebas de resiliencia ante `None` en `test_utils.py`, `test_cycle_interpretation_service.py`, `test_transition_detector.py`, `test_regime_classifier.py` y `test_assessment_builder.py`.
