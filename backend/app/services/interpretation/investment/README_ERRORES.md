# Registro Técnico de Errores Corregidos: `app/services/interpretation/investment`

Este documento recopila las inconsistencias de contrato, fallos de propagación de tipos `None`, deficiencias de empaquetado y desajustes de señales identificados y corregidos en el submódulo [`app/services/interpretation/investment/`](file:///home/dano/sight/backend/app/services/interpretation/investment/).

---

## Índice de Errores Corregidos

1. [Error 1: Inconsistencia y anulación de banderas booleanas por valores `None` explícitos en `SignalGenerator`](#error-1-inconsistencia-y-anulación-de-banderas-booleanas-por-valores-none-explícitos-en-signalgenerator)
2. [Error 2: Propagación de valores `None` en contratos de salida hacia la API](#error-2-propagación-de-valores-none-en-contratos-de-salida-hacia-la-api)
3. [Error 3: Archivo `__init__.py` vacío y falta de exportación pública de la interfaz](#error-3-archivo-__init__py-vacío-y-falta-de-exportación-pública-de-la-interfaz)
4. [Error 4: Ambigüedad en la delimitación de responsabilidades frente a `analysis/investment/`](#error-4-ambigüedad-en-la-delimitación-de-responsabilidades-frente-a-analysisinvestment)

---

### Error 1: Inconsistencia y anulación de banderas booleanas por valores `None` explícitos en `SignalGenerator`
* **Severidad:** 🟡 **Media (Integridad de Señales / Comportamiento Inconsistente)**
* **Archivo afectado:** [`app/services/interpretation/investment/signal_generator.py`](file:///home/dano/sight/backend/app/services/interpretation/investment/signal_generator.py)

#### Descripción del Fallo y Causa Raíz
En Python, el método de acceso a diccionarios `dict.get(key, default)` **únicamente aplica el valor por defecto si la clave no existe**. Si la clave está presente con valor explícito `None` (caso muy común cuando el detector de ciclos o regímenes emite `{"detected": False, "direction": None, "state": None}`):
```python
# Código original con error:
direction = transition.get("direction", "unknown")
state = transition.get("state", "none")
```
Al recibir `{"direction": None}`, `direction` tomaba el valor `None`.
A continuación, el diccionario de señales evaluaba:
```python
"unknown": direction == "unknown",
"none": state == "none",
```
Dado que `None == "unknown"` es `False` y `None == "none"` es `False`:
* Todas las banderas direccionales (`toward_slowdown`, `toward_contraction`, `toward_recovery`, etc.) eran `False`.
* **¡La bandera `"unknown"` TAMBIÉN era `False`!**
* **¡La bandera `"none"` TAMBIÉN era `False`!**

#### Impacto Funcional
Se producía una inconsistencia de contrato: un diccionario vacío `{}` producía `"unknown": True` y `"none": True`, pero un diccionario con `{"direction": None}` producía `"unknown": False` y `"none": False`. El consumidor de señales (como un motor de alertas o la UI de React) recibía un estado donde ninguna dirección era cierta, pero tampoco se marcaba como desconocida.

Similarmente ocurría en `_growth_signals`, `_trend_signals`, `_momentum_signals`, `_volatility_signals` y `_position_signals` si los analizadores previos emitían campos con valor `None`.

#### Solución Aplicada
Se implementó un patrón defensivo que garantiza que los valores nulos o vacíos se normalicen a sus cadenas canónicas:
```python
direction = transition.get("direction") or "unknown"
state = transition.get("state") or "none"
```
Si el campo es `None`, `""` o ausente, se asigna con certeza `"unknown"` y `"none"`, garantizando que `"unknown": True` se active de forma homogénea.

---

### Error 2: Propagación de valores `None` en contratos de salida hacia la API
* **Severidad:** 🟡 **Media (Uniformidad de Esquemas Pydantic / TypeScript)**
* **Archivos afectados:**
  - [`app/services/interpretation/investment/environment_interpreter.py`](file:///home/dano/sight/backend/app/services/interpretation/investment/environment_interpreter.py)
  - [`app/services/interpretation/investment/opportunity_interpreter.py`](file:///home/dano/sight/backend/app/services/interpretation/investment/opportunity_interpreter.py)
  - [`app/services/interpretation/investment/risk_interpreter.py`](file:///home/dano/sight/backend/app/services/interpretation/investment/risk_interpreter.py)
  - [`app/services/interpretation/investment/confidence_estimator.py`](file:///home/dano/sight/backend/app/services/interpretation/investment/confidence_estimator.py)

#### Descripción del Fallo y Causa Raíz
Cada uno de estos cuatro evaluadores expone en su diccionario de retorno un bloque `"transition"` o `"context"` para que los consumidores aguas abajo (`InvestmentAnalysisService` y los endpoints de FastAPI) conozcan la dinámica de fondo.
Originalmente hacían:
```python
"transition": {
    "detected": transition_detected,
    "direction": transition.get("direction", "unknown"),
    "state": transition.get("state", "none"),
    "confidence": transition.get("confidence", "low"),
}
```
Si la entrada contenía `None` explícito en esas claves, la salida propagaba `{"direction": None, "state": None, "confidence": None}` hacia los routers de la API.
En el frontend (TypeScript), las interfaces esperan cadenas (`type TransitionDirection = "toward_slowdown" | ... | "unknown"`), provocando errores de tipado o lecturas `null` inesperadas en los componentes visuales.

#### Solución Aplicada
Se normalizó la asignación en los cuatro intérpretes:
```python
"direction": transition.get("direction") or "unknown",
"state": transition.get("state") or "none",
"confidence": transition.get("confidence") or "low",
```
Asegurando que la estructura JSON resultante garantice tipos `string` invariantes.

---

### Error 3: Archivo `__init__.py` vacío y falta de exportación pública de la interfaz
* **Severidad:** 🟢 **Baja (Arquitectura y Empaquetado Python)**
* **Archivo afectado:** [`app/services/interpretation/investment/__init__.py`](file:///home/dano/sight/backend/app/services/interpretation/investment/__init__.py)

#### Descripción del Fallo
El archivo `__init__.py` del paquete se encontraba completamente en blanco (0 bytes). Cualquier servicio externo que necesitara consumir los intérpretes debía realizar importaciones profundas acopladas al nombre de cada archivo físico (`from app.services.interpretation.investment.environment_interpreter import EnvironmentInterpreter`).

#### Solución Aplicada
Se expuso la API pública canónica del paquete en `__init__.py`:
```python
from __future__ import annotations

from .confidence_estimator import ConfidenceEstimator
from .environment_interpreter import EnvironmentInterpreter
from .investment_interpretation_service import (
    InvestmentInterpretationService,
)
from .opportunity_interpreter import OpportunityInterpreter
from .risk_interpreter import RiskInterpreter
from .signal_generator import SignalGenerator

__all__ = [
    "ConfidenceEstimator",
    "EnvironmentInterpreter",
    "InvestmentInterpretationService",
    "OpportunityInterpreter",
    "RiskInterpreter",
    "SignalGenerator",
]
```

---

### Error 4: Ambigüedad en la delimitación de responsabilidades frente a `analysis/investment/`
* **Severidad:** 🟢 **Baja (Claridad Arquitectónica y Deuda Técnica)**
* **Componentes:** `interpretation/investment/` vs `analysis/investment/`

#### Descripción y Riesgo
Existía el riesgo de que desarrolladores confundieran componentes homónimos o complementarios:
* `interpretation/investment`: Opera a nivel de **un solo indicador**, traduciendo la economía pura a las dimensiones de inversión (`environment`, `opportunity`, `risk`, `signals`, `confidence`).
* `analysis/investment`: Opera como la **capa superior de síntesis y asignación**, generando la tesis ejecutiva (`macro_bias`, `horizon`, `alerts`, `conviction`, `overall`) y orquestando el ranking cuantitativo multi-activo (`MacroFactorScorer`, `AssetRegistry`, `AssetScorer`).
* En particular, la diferencia entre:
  * `ConfidenceEstimator`: Mide la coherencia y solidez interna de las evidencias macroeconómicas del indicador.
  * `ConvictionAnalyzer`: Mide la convicción de la tesis final de inversión integrando sesgo, horizonte y alertas.

#### Solución Aplicada
Se formalizó la separación en [`README.md`](file:///home/dano/sight/backend/app/services/interpretation/investment/README.md) y en los docstrings de los servicios, garantizando contratos de datos unidireccionales y sin dependencias circulares.

---

## Verificación y Pruebas Unitarias de Regresión

Se agregaron pruebas unitarias dedicadas en:
* [`tests/unit/services/interpretation/investment/test_signal_generator.py`](file:///home/dano/sight/backend/tests/unit/services/interpretation/investment/test_signal_generator.py):
  * `test_generate_handles_explicit_none_values_gracefully`: Verifica que diccionarios con valores `None` explícitos en `transition` y otros bloques activen `"unknown": True` y `"none": True` sin fallos.
* [`tests/unit/services/interpretation/investment/test_investment_interpretation_service.py`](file:///home/dano/sight/backend/tests/unit/services/interpretation/investment/test_investment_interpretation_service.py):
  * `test_transition_with_none_values_normalizes_to_canonical_strings`: Comprueba que `environment`, `opportunity`, `risk` y `confidence` emitan siempre cadenas canónicas y no valores `None`.

```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/unit/services/interpretation/investment/
# 256 passed in 0.26s
```
Suite global del backend:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/
# 1,230 passed in 4.66s
```
