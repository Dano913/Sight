# Registro Técnico de Errores Corregidos: `app/services/analysis`

Este documento recopila de forma exhaustiva todos los fallos, lagunas econométricas, inconsistencias de contrato y problemas de orquestación identificados y subsanados en el bloque `app/services/analysis/` y sus diferentes subdirectorios durante las sesiones de auditoría y refactorización.

---

## Índice de Directorios Auditados

1. [`app/services/analysis/macro_regime/`](#1-subdirectorio-appservicesanalysismacro_regime)
   - [Error 1.1: Bug crítico de pesos silenciados (`weight`) en agregación de régimen](#error-11-bug-crítico-de-pesos-silenciados-weight-en-agregación-de-régimen)
   - [Error 1.2: Inconsistencia de clave en `ActivityRegimeAnalyzer` (`indicators` vs `indicator`)](#error-12-inconsistencia-de-clave-en-activityregimeanalyzer-indicators-vs-indicator)
   - [Error 1.3: Cálculo de confianza y empates en `RegimeConfidence`](#error-13-cálculo-de-confianza-y-empates-en-regimeconfidence)
2. [`app/services/analysis/cycle/`](#2-subdirectorio-appservicesanalysiscycle)
   - [Error 2.1: Supuesto de equiespaciamiento temporal y armónicos espurios en FFT](#error-21-supuesto-de-equiespaciamiento-temporal-y-armónicos-espurios-en-fft)
   - [Error 2.2: Desajuste del parámetro de suavizado $\lambda$ en filtro Hodrick-Prescott](#error-22-desajuste-del-parámetro-de-suavizado-lambda-en-filtro-hodrick-prescott)
3. [`app/services/analysis/investment/`](#3-subdirectorio-appservicesanalysisinvestment)
   - [Error 3.1: Redundancia y duplicación de campos en `OverallAssessmentBuilder`](#error-31-redundancia-y-duplicación-de-campos-en-overallassessmentbuilder)
   - [Error 3.2: Desconexión del subsistema cuantitativo de scoring de activos (`asset/`)](#error-32-desconexión-del-subsistema-cuantitativo-de-scoring-de-activos-asset)
4. [Raíz `app/services/analysis/` (`analysis_service.py`)](#4-orquestador-raíz-appservicesanalysisanalysis_servicepy)
   - [Error 4.1: Mezcla ciega de múltiples fuentes para un mismo indicador](#error-41-mezcla-ciega-de-múltiples-fuentes-para-un-mismo-indicador)
   - [Error 4.2: Ausencia de alineación temporal y sesgo de anticipación (*lookahead bias*)](#error-42-ausencia-de-alineación-temporal-y-sesgo-de-anticipación-lookahead-bias)
   - [Error 4.3: Orquestación rota de la síntesis de inversión delegada al transporte HTTP](#error-43-orquestación-rota-de-la-síntesis-de-inversión-delegada-al-transporte-http)

---

## 1. Subdirectorio: `app/services/analysis/macro_regime/`

### Error 1.1: Bug crítico de pesos silenciados (`weight`) en agregación de régimen
* **Severidad:** 🔴 **Crítica (Fallo Silencioso en Producción)**
* **Archivos afectados:**
  - [`app/services/analysis/macro_regime/macro_regime_service.py`](file:///home/dano/sight/backend/app/services/analysis/macro_regime/macro_regime_service.py)
  - [`app/services/analysis/macro_regime/regime_analyzers.py`](file:///home/dano/sight/backend/app/services/analysis/macro_regime/regime_analyzers.py)

#### Descripción del Fallo y Causa Raíz
En el método de agregación de evidencias `_aggregate_scores()` de `MacroRegimeService`, el cálculo de puntuaciones acumuladas exigía la presencia obligatoria de la clave `"weight"` en cada diccionario de evidencia:
```python
# Código original con error:
for item in evidence:
    regime = item["regime"]
    try:
        weight = float(item["weight"])
    except (KeyError, TypeError, ValueError):
        continue  # <-- ¡Silenciaba cualquier evidencia sin peso!
    scores[regime] = scores.get(regime, 0.0) + weight
```
Sin embargo, **ninguno de los cinco analizadores especializados** en `regime_analyzers.py` (`GrowthRegimeAnalyzer`, `ActivityRegimeAnalyzer`, `EmploymentRegimeAnalyzer`, `InflationRegimeAnalyzer`, `FinancialRegimeAnalyzer`) incluía la clave `"weight"` al construir los diccionarios de evidencia. Construían la evidencia únicamente con `{"family": ..., "indicator": ..., "regime": ..., "confidence": ..., "reason": ...}`.

#### Impacto Funcional
Cada una de las evidencias emitidas por todos los indicadores generaba un `KeyError`, que era capturado y descartado de forma transparente por el `continue`. Como consecuencia:
1. El diccionario acumulado `scores` quedaba siempre vacío: `{}`.
2. La condición `if not scores:` de `macro_regime_service.py` forzaba la ejecución de `_empty_result()`.
3. **El sistema devolvía SIEMPRE:**
   ```json
   {
       "regime": "neutral",
       "scores": {},
       "conditions": [],
       "confidence": "low"
   }
   ```
   Incluso ante un boom económico evidente con PIB acelerando al +5%, desempleo en mínimos y beneficios récord, la clasificación agregada devolvía siempre un régimen neutral con confianza baja.

#### ¿Por qué no lo detectaban los tests unitarios previos?
Los tests unitarios de `MacroRegimeService` utilizaban un mock (`patch.object(MacroRegimeService, "_collect_evidence", return_value=[{"regime": "expansion", "weight": 5.0, ...}])`). Como el test inyectaba manualmente diccionarios con `"weight"`, el test pasaba en verde al 100%, pero el código real en producción jamás aportaba dicho campo.

#### Solución Aplicada
1. En [`regime_analyzers.py`](file:///home/dano/sight/backend/app/services/analysis/macro_regime/regime_analyzers.py): Se parametrizó cada emisión de evidencia asignando un peso explícito ponderado según la relevancia econométrica del indicador:
   - Crecimiento de PIB real: `weight = 3.0` (o `2.0` si confianza media).
   - Producción Industrial y Actividad: `weight = 2.0`.
   - Desempleo y Nóminas: `weight = 3.0` / `2.0`.
   - Inflación y Condiciones Financieras: `weight = 2.0` / `1.5`.
2. En [`macro_regime_service.py`](file:///home/dano/sight/backend/app/services/analysis/macro_regime/macro_regime_service.py): Se programó defensa en profundidad en `_aggregate_scores()` implementando un peso por defecto (`item.get("weight", 1.0)`) para que cualquier evidencia futura sin peso ponderado específico compute al menos con peso unitario en lugar de ser descartada en silencio.

---

### Error 1.2: Inconsistencia de clave en `ActivityRegimeAnalyzer` (`indicators` vs `indicator`)
* **Severidad:** 🟡 **Media**
* **Archivos afectados:**
  - [`app/services/analysis/macro_regime/regime_analyzers.py`](file:///home/dano/sight/backend/app/services/analysis/macro_regime/regime_analyzers.py)
  - [`app/services/analysis/macro_regime/macro_regime_service.py`](file:///home/dano/sight/backend/app/services/analysis/macro_regime/macro_regime_service.py)

#### Descripción del Fallo y Causa Raíz
El analizador `ActivityRegimeAnalyzer` agrupaba internamente indicadores de actividad (p. ej., `INDUSTRIAL_PRODUCTION` y `RETAIL_SALES`) y emitía en su diccionario de evidencia la lista de indicadores bajo la clave `"indicators"` (en plural):
```python
evidence.append({
    "family": "activity",
    "indicators": ["INDUSTRIAL_PRODUCTION", "RETAIL_SALES"],
    "regime": regime,
    ...
})
```
Sin embargo, el método de penalización por conflicto en `MacroRegimeService._adjust_for_conflicting_activity()` consultaba:
```python
indicator = item.get("indicator")  # <-- Singular
```
Al recibir `None`, el sistema ignoraba la verificación de actividad y nunca detectaba si la producción industrial estaba entrando en conflicto con el crecimiento general.

#### Solución Aplicada
Se unificó el esquema de evidencias para garantizar compatibilidad con clave `"indicator"` como cadena principal, soportando adicionalmente la lista de origen en caso de agregaciones compuestas.

---

### Error 1.3: Cálculo de confianza y empates en `RegimeConfidence`
* **Severidad:** 🟡 **Media**
* **Archivos afectados:**
  - [`app/services/analysis/macro_regime/regime_confidence.py`](file:///home/dano/sight/backend/app/services/analysis/macro_regime/regime_confidence.py)

#### Descripción del Fallo y Causa Raíz
Cuando dos regímenes obtenían exactamente la misma puntuación máxima ponderada (por ejemplo, 6.0 puntos para `expansion` y 6.0 puntos para `inflation`), la selección dependía del orden aleatorio de iteración de claves del diccionario en Python, y la cuota relativa (`share = dominant_score / total_score`) caía bruscamente al 50%, arrojando confianza `"low"` de forma errática o eligiendo un régimen sin justificación de desempate.

#### Solución Aplicada
Se añadió una regla determinista de resolución de empates en `RegimeConfidence.calculate()` y `MacroRegimeService._aggregate_scores()`, priorizando regímenes de riesgo y estrés macroeconómico cuando hay igual puntuación, y calibrando la confianza en función de la cuota efectiva de soporte y el número de indicadores activos independientes.

---

## 2. Subdirectorio: `app/services/analysis/cycle/`

### Error 2.1: Supuesto de equiespaciamiento temporal y armónicos espurios en FFT
* **Severidad:** 🟠 **Alta (Econométrica / Matemática)**
* **Archivos afectados:**
  - [`app/services/analysis/cycle/cycle_preprocessor.py`](file:///home/dano/sight/backend/app/services/analysis/cycle/cycle_preprocessor.py)
  - [`app/services/analysis/cycle/cycle_signal_analyzer.py`](file:///home/dano/sight/backend/app/services/analysis/cycle/cycle_signal_analyzer.py)

#### Descripción del Fallo y Causa Raíz
La Transformada Rápida de Fourier (FFT) y el periodograma estándar aplicados por `CycleSignalAnalyzer` operan bajo la hipótesis estricta de que la señal muestreada está equiespaciada temporalmente a intervalos constantes $\Delta t$.
1. El código original ordenaba las observaciones por fecha pero descartaba el índice cronológico real, mapeando los valores directamente a un array de NumPy indexado por enteros ordinales $t \in [0, 1, 2, \dots, N-1]$.
2. Si la serie histórica contenía **lagunas temporales** (meses no publicados por huelga o festivos, series con suspensiones temporales o datos trimestrales con fechas intermedias faltantes), el colapso ordinal "pegaba" fechas no consecutivas como si fueran adyacentes.

#### Impacto Econométrico
El acortamiento artificial de los intervalos temporales distorsionaba la escala de frecuencias, introduciendo **armónicos espurios** (*aliasing* espectral) y provocando que el algoritmo `CycleDetector` detectara falsos ciclos de 2 a 3 años que en realidad eran artefactos creados por los huecos en la serie. Además, la tendencia lineal calculada en `linear_detrend` distorsionaba la pendiente secular al asumir que cada salto de índice equivalía a un paso uniforme de tiempo.

#### Solución Aplicada
1. **Detección de discontinuidades cronológicas:** Se implementó `check_regularity()` en `CyclePreprocessor`, calculando la diferencia de periodos $\Delta p_i$ esperados según la frecuencia formal. Si $\max(\Delta p_i) > 1$, la serie se marca con `is_regular = False`.
2. **Detrending en tiempo continuo real:** Se refactorizó `linear_detrend(series, dates=dates)` en `CyclePreprocessor` para utilizar el tiempo físico continuo transcurrido en años:
   $$t_i = \frac{d_i - d_0}{365.25}$$
   garantizando una eliminación de tendencia lineal geométricamente correcta sin importar la separación entre fechas.
3. **Periodograma de Lomb-Scargle para series irregulares:** En `CycleSignalAnalyzer`, se implementó el algoritmo `_periodogram_lombscargle()`, formulación espectral derivada de mínimos cuadrados generalizados específicamente diseñada para datos observacionales astronómicos y macroeconómicos desigualmente espaciados. Si `check_regularity()` detecta lagunas, `CycleAnalysisService` conmuta automáticamente a Lomb-Scargle preservando los armónicos físicos reales.

---

### Error 2.2: Desajuste del parámetro de suavizado $\lambda$ en filtro Hodrick-Prescott
* **Severidad:** 🟡 **Media**
* **Archivos afectados:**
  - [`app/services/analysis/cycle/cycle_preprocessor.py`](file:///home/dano/sight/backend/app/services/analysis/cycle/cycle_preprocessor.py)

#### Descripción del Fallo y Causa Raíz
El filtro Hodrick-Prescott (`hp_filter`) requiere el parámetro de penalización de curvatura $\lambda$. El código fijaba $\lambda = 1600$ de forma genérica o fallaba al inferir frecuencias cuando las observaciones anuales presentaban desfases de días.

#### Solución Aplicada
Se añadió `infer_observations_per_year()` para deducir la frecuencia empírica a partir de la mediana de diferencias de fechas y se calibró la función `default_hp_lambda()` según los consensos econométricos de Ravn & Uhlig:
* Anual: $\lambda = 6.25$ (o $100$).
* Trimestral: $\lambda = 1600$.
* Mensual: $\lambda = 14400$ (o $129600$).

---

## 3. Subdirectorio: `app/services/analysis/investment/`

### Error 3.1: Redundancia y duplicación de campos en `OverallAssessmentBuilder`
* **Severidad:** 🟢 **Baja (Arquitectura y Limpieza de Contrato)**
* **Archivos afectados:**
  - [`app/services/analysis/investment/overall_assessment_builder.py`](file:///home/dano/sight/backend/app/services/analysis/investment/overall_assessment_builder.py)
  - [`app/services/analysis/investment/investment_analysis_service.py`](file:///home/dano/sight/backend/app/services/analysis/investment/investment_analysis_service.py)

#### Descripción del Fallo y Causa Raíz
En `overall_assessment_builder.py`, el método de construcción del resumen ejecutivo se limitaba a clonar las claves ya generadas previamente por `MacroBiasAnalyzer`:
```python
# Código redundante original:
return {
    "assessment": macro_bias.get("state", "unknown"),
    "direction": macro_bias.get("direction", "unknown"),
    "strength": macro_bias.get("strength", "unknown"),
}
```
Esto creaba una redundancia circular en el JSON de salida (`investment_analysis["macro_bias"]["state"]` era idéntico a `investment_analysis["overall"]["assessment"]`), sin aportar síntesis real sobre los riesgos de volatilidad (`alerts`), las perspectivas por plazo (`horizon`) ni la solidez estadística (`conviction`).

#### Solución Aplicada
Se delimitó la jerarquía de responsabilidades:
* `MacroBiasAnalyzer` determina la dirección y sesgo estructural.
* `HorizonAnalyzer` calibra el impacto diferenciado en el corto, medio y largo plazo.
* `AlertAnalyzer` extrae condiciones de estrés, drawdown o volatilidad extrema.
* `ConvictionAnalyzer` computa la solidez cuantitativa del consenso.
* `OverallAssessmentBuilder` sintetiza la tesis unificada integrando sesgo, convicción y alertas en un veredicto de inversión holístico.

---

### Error 3.2: Desconexión del subsistema cuantitativo de scoring de activos (`asset/`)
* **Severidad:** 🟠 **Alta (Integración y Funcionalidad Incompleta)**
* **Archivos afectados:**
  - [`app/services/analysis/investment/asset/macro_factor_scorer.py`](file:///home/dano/sight/backend/app/services/analysis/investment/asset/macro_factor_scorer.py)
  - [`app/services/analysis/investment/asset/asset_scorer.py`](file:///home/dano/sight/backend/app/services/analysis/investment/asset/asset_scorer.py)
  - [`app/services/analysis/investment/asset/asset_registry.py`](file:///home/dano/sight/backend/app/services/analysis/investment/asset/asset_registry.py)
  - [`app/services/analysis/analysis_service.py`](file:///home/dano/sight/backend/app/services/analysis/analysis_service.py)

#### Descripción del Fallo y Causa Raíz
El directorio `investment/asset/` contenía excelentes algoritmos cuantitativos para traducir interpretaciones económicas a factores estandarizados de mercado (`Growth`, `Inflation`, `Financial Conditions`) y calificar cestas de activos (Renta Variable, Bonos Soberanos, Oro, Materias Primas, Crédito Corporativo, etc.). Sin embargo, **estos componentes no estaban integrados en el pipeline de ejecución de `AnalysisService`**. Los endpoints de FastAPI no podían ofrecer el ranking de activos de manera nativa sin duplicar lógica de negocio externa.

#### Solución Aplicada
Se orquestó el flujo completo dentro de `AnalysisService.analyze_multiple()`:
1. Las interpretaciones activas se envían a `MacroFactorScorer.score()`.
2. Se consulta el catálogo oficial de activos mediante `AssetRegistry.get_all()`.
3. `AssetScorer.score_all()` aplica la matriz de sensibilidad factorial a cada clase de activo.
4. El ranking ponderado resultante se incluye directamente en la respuesta bajo la clave `"asset_ranking"`.

---

## 4. Orquestador Raíz: `app/services/analysis/` (`analysis_service.py`)

### Error 4.1: Mezcla ciega de múltiples fuentes para un mismo indicador
* **Severidad:** 🟠 **Alta (Integridad de Datos)**
* **Archivos afectados:**
  - [`app/services/analysis/analysis_service.py`](file:///home/dano/sight/backend/app/services/analysis/analysis_service.py)

#### Descripción del Fallo y Causa Raíz
En Sight, un indicador en una misma región puede recopilarse desde múltiples proveedores (por ejemplo, `GDP` en EE.UU. disponible a través de `BEA` y de `OECD`).
En la versión original de `AnalysisService.analyze()`, las observaciones entrantes se ordenaban simplemente por fecha:
```python
ordered_observations = sorted(observations, key=lambda o: o.date)
```
Si la base de datos contenía datos de ambas fuentes, el método las mezclaba en una única serie. Al coexistir dos observaciones para el mismo trimestre con valores ligeramente distintos (revisiones estadísticas o metodologías BEA vs OECD), el índice temporal de Pandas contenía **fechas duplicadas**, lo que rompía el cálculo de diferencias logarítmicas, retornos y correlaciones móviles.

#### Solución Aplicada
Se implementó `_build_series_by_source()` y se incorporó el parámetro `source_code: str | None = None`:
* El servicio agrupa y separa las observaciones por proveedor (`source.code`).
* Si el llamante especifica `source_code`, se selecciona exclusivamente dicha fuente.
* Si no se especifica y existe un único proveedor presente, se utiliza de forma unívoca.
* Si existen múltiples proveedores y no se desambigua, el sistema selecciona de manera determinista la fuente canónica con mayor cobertura y previene la intercalación de datos heterogéneos.

---

### Error 4.2: Ausencia de alineación temporal y sesgo de anticipación (*lookahead bias*)
* **Severidad:** 🟠 **Alta (Econométrica y Metodológica)**
* **Archivos afectados:**
  - [`app/services/analysis/analysis_service.py`](file:///home/dano/sight/backend/app/services/analysis/analysis_service.py)

#### Descripción del Fallo y Causa Raíz
Al invocar `AnalysisService.analyze_multiple()`, el sistema recibía observaciones de diversos indicadores sin verificar su sincronía temporal ni su actualidad:
1. **Series descontinuadas o congeladas (*stale data*):** Si la base de datos contenía datos de un indicador cuya serie se interrumpió en 2021 mientras los demás indicadores estaban actualizados a 2024, el clasificador de régimen `MacroRegimeService` promediaba observaciones separadas por tres años en el tiempo real.
2. **Imposibilidad de backtesting sin sesgo de anticipación:** No existía forma de ejecutar un análisis retrospectivo simulando lo que el sistema "sabía" en una fecha pasada específica (análisis *point-in-time*), ya que siempre se procesaban todos los registros disponibles en la base de datos.

#### Solución Aplicada
Se rediseñó `AnalysisService.analyze_multiple()` implementando dos nuevos controles temporales:
1. **Parámetro `as_of_date: str | date | datetime | None = None`:**
   Permite fijar una fecha de corte retrospectiva. Cualquier observación posterior a `as_of_date` es descartada antes de iniciar el cálculo de features o ciclos, garantizando backtesting realista sin sesgo de anticipación.
2. **Detección de rezagos y aislamiento de series obsoletas (`max_lag_days = 180`):**
   - El servicio determina la fecha de referencia global $D_{\text{ref}}$ (la fecha más reciente entre todos los indicadores analizados).
   - Para cada indicador $k$, calcula su rezago en días: $\text{lag\_days}_k = D_{\text{ref}} - D_{k, \text{latest}}$.
   - Si $\text{lag\_days}_k > \text{max\_lag\_days}$, el indicador se clasifica como `stale` y se aísla en `stale_indicators`.
   - **Regla de oro:** Los indicadores `stale` se conservan en la respuesta individual para diagnóstico, pero **se excluyen estrictamente de la votación de `MacroRegimeService` y del scoring de factores de `MacroFactorScorer`**, impidiendo que datos antiguos desvirtúen el diagnóstico macroeconómico contemporáneo.
   - La respuesta del servicio expone la sección estructurada `temporal_alignment`:
     ```json
     "temporal_alignment": {
         "as_of_date": "2024-03-31",
         "reference_date": "2024-03-31",
         "max_lag_days": 180,
         "active_indicators": ["GDP", "CPI", "UNEMPLOYMENT"],
         "stale_indicators": ["OLD_METRIC"],
         "indicator_lags": {
             "GDP": 0,
             "CPI": 0,
             "UNEMPLOYMENT": 0,
             "OLD_METRIC": 840
         }
     }
     ```

---

### Error 4.3: Orquestación rota de la síntesis de inversión delegada al transporte HTTP
* **Severidad:** 🟡 **Media (Arquitectura de Servicios)**
* **Archivos afectados:**
  - [`app/services/analysis/analysis_service.py`](file:///home/dano/sight/backend/app/services/analysis/analysis_service.py)
  - [`app/api/routers/analysis.py`](file:///home/dano/sight/backend/app/api/routers/analysis.py)

#### Descripción del Fallo y Causa Raíz
En el diseño original, `AnalysisService.analyze()` no invocaba a `InvestmentAnalysisService.analyze()`. El orquestador principal omitía este paso, obligando a que el controlador HTTP (`app/api/routers/analysis.py`) tuviera que instanciar manualmente el servicio de inversión, extraer diccionarios de la respuesta y volver a empaquetar el JSON resultante. Si otro servicio o un proceso por lotes (script cron o worker) llamaba a `AnalysisService.analyze()`, no obtenía la tesis de inversión.

#### Solución Aplicada
Se integró de forma síncrona `InvestmentAnalysisService.analyze()` en el retorno canónico de `AnalysisService.analyze()`, asegurando que cualquier consumidor de la capa de servicio reciba el análisis completo estructurado sin depender del framework web.

---

## 5. Resumen de Pruebas y Verificación del Bloque

Tras corregir todos los errores enumerados, se crearon suites de tests de regresión específicas para blindar las soluciones:
* [`tests/unit/services/analysis/macro/macro_regime/test_macro_regime_service.py`](file:///home/dano/sight/backend/tests/unit/services/analysis/macro/macro_regime/test_macro_regime_service.py): Verifica que la evidencia incluya `"weight"`, que los analizadores generen pesos válidos y que el régimen agregado compute valores distintos de `neutral` con datos reales.
* [`tests/unit/services/analysis/test_analysis_service_temporal_alignment.py`](file:///home/dano/sight/backend/tests/unit/services/analysis/test_analysis_service_temporal_alignment.py): Comprueba el filtrado *point-in-time* por `as_of_date` y el aislamiento de series `stale` según `max_lag_days`.
* [`tests/unit/services/analysis/macro/cycle/test_cycle_temporal_gaps.py`](file:///home/dano/sight/backend/tests/unit/services/analysis/macro/cycle/test_cycle_temporal_gaps.py): Valida la regularidad temporal, el detrending con tiempo físico continuo y la activación de Lomb-Scargle ante lagunas de datos.
* [`tests/unit/services/analysis/investment/test_investment_analysis_service.py`](file:///home/dano/sight/backend/tests/unit/services/analysis/investment/test_investment_analysis_service.py): Asegura la orquestación integral de la tesis de inversión cualitativa y cuantitativa.

La totalidad del conjunto de pruebas pasa al 100%:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/
# 1,228 passed in 4.03s
```
