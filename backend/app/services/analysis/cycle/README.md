# Submódulo de Análisis Espectral y Ciclos Económicos: `app/services/analysis/cycle`

El submódulo `app/services/analysis/cycle` es el motor de procesamiento de señales y econometría espectral de **Sight**. Su objetivo es descomponer series temporales macroeconómicas, eliminar tendencias seculares en tiempo físico real, aislar fluctuaciones periódicas mediante filtrado Hodrick-Prescott y detectar ciclos económicos dominantes y robustos combinando el dominio de la frecuencia (periodograma) y el dominio del tiempo (autocorrelación).

---

## 1. Mapa Global de Flujo y Conexiones

```mermaid
flowchart TD
    %% Entrada
    OBS[("Observaciones Temporales")] --> CAS["CycleAnalysisService.analyze()"]
    
    %% Preprocesamiento
    subgraph Preprocesamiento ["1. Preprocesamiento & Descomposición (CyclePreprocessor)"]
        CAS --> CPR_PS["prepare_series()"]
        CPR_PS --> CPR_INF["infer_observations_per_year(dates)"]
        CPR_PS --> CPR_REG["check_regularity(dates, obs_per_year)"]
        
        CAS --> CPR_GW["growth(series)"]
        CAS --> CPR_LD["linear_detrend(series, dates=dates)"]
        CAS --> CPR_HP["hp_filter(series, hp_lambda)"]
        CPR_HP --> CPR_LMB["default_hp_lambda(obs_per_year)"]
    end
    
    %% Análisis Espectral
    subgraph Analisis_Espectral ["2. Análisis de Señal (CycleSignalAnalyzer)"]
        CAS --> CSA_PER["periodogram(detrended, obs_per_year, dates=dates)"]
        CSA_PER -.->|Si is_regular == True| CSA_FFT["FFT / Periodograma Estándar"]
        CSA_PER -.->|Si is_regular == False (lagunas)| CSA_LS["_periodogram_lombscargle()"]
        CAS --> CSA_ACF["autocorrelation(detrended, max_lag)"]
    end
    
    %% Detección y Clustering
    subgraph Deteccion_Ciclos ["3. Detección & Clustering de Ciclos (CycleDetector)"]
        CAS --> CD_VAL["get_valid_periods(candidates, obs_per_year)"]
        CAS --> CD_ROB["detect_robust_cycles(periodogram_cycles, acf_lags)"]
        CD_ROB --> CD_CLU["cluster_periods()"]
        CD_CLU --> CD_CLS["periods_are_close(p1, p2, tolerance=0.15)"]
        CD_ROB --> CD_SCR["score_cluster()"]
    end
    
    %% Diagnóstico y Salida
    subgraph Diagnostico ["4. Diagnóstico de Calidad (CycleDiagnostics)"]
        CAS --> CDG_EV["evaluate(cycles, series_length, regularity)"]
    end
    
    CDG_EV --> RES[("Resultado Consolidado de Ciclos\ndominant_periods, dominant_period_years,\ncycle_power, components, is_regular")]
```

---

## 2. Componentes Especializados

### 2.1. Orquestador: `CycleAnalysisService`
Archivo: [`cycle_analysis_service.py`](cycle_analysis_service.py)

Coordina el pipeline de análisis de ciclos para un indicador individual:
1. Valida la longitud mínima de observaciones requeridas para análisis armónico significativo ($N \ge 16$).
2. Delega en `CyclePreprocessor` para ordenar, comprobar regularidad y desestacionalizar/detrendear la serie.
3. Extrae frecuencias candidatas vía espectro de potencia y picos de correlación temporal.
4. Identifica clusters de periodicidad donde el espectro de frecuencias coincide con los desfases de la función de autocorrelación (ACF).
5. Calcula diagnósticos de fiabilidad y retorna la estructura serializable en JSON con componentes cíclicos aislados.

---

### 2.2. Preprocesador y Filtrado: `CyclePreprocessor`
Archivo: [`cycle_preprocessor.py`](cycle_preprocessor.py)

* **`prepare_series(observations)`**:
  Ordena las observaciones por fecha, extrae arrays NumPy de valores continuos y el `pd.DatetimeIndex`, e infiere las observaciones por año.
* **`infer_observations_per_year(dates)`**:
  Calcula la mediana de días transcurridos entre fechas consecutivas:
  * $\le 45$ días $\rightarrow 12$ obs/año (mensual).
  * $46 - 120$ días $\rightarrow 4$ obs/año (trimestral).
  * $> 120$ días $\rightarrow 1$ obs/año (anual).
* **`check_regularity(dates, obs_per_year)`**:
  Calcula la diferencia de periodos esperados $\Delta p_i$ entre observaciones contiguas. Si existe alguna laguna temporal ($\Delta p_i > 1$), marca `is_regular = False`.
* **`linear_detrend(series, dates=dates)`**:
  Ajusta una regresión lineal $X_t = \alpha + \beta t + \epsilon_t$. **Utiliza el tiempo físico real transcurrido en años:**
  $$t_i = \frac{d_i - d_0}{365.25}$$
  evitando que las lagunas temporales distorsionen la pendiente de la tendencia secular.
* **`hp_filter(series, hp_lambda)`**:
  Aplica el filtro Hodrick-Prescott mediante minimización cuadrática penalizada:
  $$\min_{\tau} \sum_{t=1}^T (X_t - \tau_t)^2 + \lambda \sum_{t=2}^{T-1} [(\tau_{t+1} - \tau_t) - (\tau_t - \tau_{t-1})]^2$$
  aislando la tendencia $\tau_t$ del ciclo $c_t = X_t - \tau_t$.
* **`default_hp_lambda(obs_per_year)`**:
  Calibra el factor $\lambda$ de acuerdo con la literatura econométrica estándar:
  * Mensual ($12$): $\lambda = 14.400$ (o $129.600$).
  * Trimestral ($4$): $\lambda = 1.600$.
  * Anual ($1$): $\lambda = 6.25$ (o $100$).

---

### 2.3. Analizador de Señal: `CycleSignalAnalyzer`
Archivo: [`cycle_signal_analyzer.py`](cycle_signal_analyzer.py)

* **Periodograma Estándar (FFT)**:
  Para series regulares sin lagunas, calcula la densidad espectral de potencia mediante la Transformada Rápida de Fourier discreta:
  $$P(f) = \frac{1}{N} \left\vert \sum_{t=0}^{N-1} X_t e^{-i 2\pi f t} \right\vert^2$$
* **Periodograma de Lomb-Scargle (`_periodogram_lombscargle`)**:
  Se activa automáticamente cuando `check_regularity()` detecta lagunas temporales. Ajusta funciones armónicas $\sin(2\pi f t)$ y $\cos(2\pi f t)$ con desfase invariante por mínimos cuadrados sobre los tiempos reales de observación $t_i$. Elimina el fenómeno de *aliasing* y previene picos espurios inducidos por huecos de fechas.
* **Autocorrelación Muestral (`autocorrelation`)**:
  Calcula los coeficientes de correlación serial normalizada $\rho(k)$ para cada retardo temporal $k \in [1, \dots, \text{max\_lag}]$:
  $$\rho(k) = \frac{\sum_{t=k+1}^N (X_t - \bar{X})(X_{t-k} - \bar{X})}{\sum_{t=1}^N (X_t - \bar{X})^2}$$

---

### 2.4. Detector de Ciclos Robustos: `CycleDetector`
Archivo: [`cycle_detector.py`](cycle_detector.py)

* **Filtrado de periodicidades admisibles (`get_valid_periods`)**:
  Filtra los periodos candidatos dentro del rango económico admisible (ciclos de Juglar y Kitchin típicamente entre $1.5$ y $12$ años), descartando armónicos de alta frecuencia (ruido estacional $< 1$ año) o de ultralargo plazo ($> 15$ años) no contrastables con la muestra disponible.
* **Clustering y Validación Cruzada (`detect_robust_cycles`)**:
  Cruza los picos de máxima potencia del periodograma con los máximos locales de la función de autocorrelación:
  * `periods_are_close(p1, p2, tolerance=0.15)`: Considera que dos estimaciones de periodo representan el mismo ciclo si discrepan en menos del $15\%$.
  * `score_cluster(cluster)`: Asigna una puntuación de convicción ponderando la potencia espectral relativa, la prominencia del pico y el soporte empírico en el dominio temporal.

---

### 2.5. Diagnóstico de Calidad: `CycleDiagnostics`
Archivo: [`cycle_diagnostics.py`](cycle_diagnostics.py)

Evalúa la significancia estadística y la solidez del ciclo detectado:
* Comprueba si el número de ciclos completos observados en la serie histórica es suficiente ($\ge 2$ o $3$ ciclos completos).
* Modula la puntuación si la serie requirió estimación por Lomb-Scargle o si la potencia espectral está excesivamente concentrada en frecuencias límite.

---

## 3. Matriz de Conexiones entre Métodos

| Método Emisor | Método Receptor | Parámetros Enviados | Salida Obtenida |
| :--- | :--- | :--- | :--- |
| `AnalysisService.analyze` | `CycleAnalysisService.analyze` | `observations`, `top_n`, `hp_lambda` | Diccionario con periodos dominantes, potencia y diagnóstico. |
| `CycleAnalysisService.analyze` | `CyclePreprocessor.prepare_series` | `observations` | `(dates, values, obs_per_year, is_regular)` |
| `CyclePreprocessor.prepare_series` | `CyclePreprocessor.infer_observations_per_year` | `dates` | Entero con la frecuencia inferida (12, 4, 1). |
| `CyclePreprocessor.prepare_series` | `CyclePreprocessor.check_regularity` | `dates`, `obs_per_year` | Booleano `is_regular`. |
| `CycleAnalysisService.analyze` | `CyclePreprocessor.linear_detrend` | `series`, `dates=dates` | Serie con tendencia lineal eliminada. |
| `CycleAnalysisService.analyze` | `CyclePreprocessor.hp_filter` | `series`, `hp_lambda` | `(trend, cycle)` separados por filtro HP. |
| `CycleAnalysisService.analyze` | `CycleSignalAnalyzer.periodogram` | `series`, `obs_per_year`, `dates` | Lista de armónicos candidatos con frecuencias y potencias. |
| `CycleSignalAnalyzer.periodogram` | `CycleSignalAnalyzer._periodogram_lombscargle` | `series`, `dates`, `obs_per_year` | Espectro Lomb-Scargle para series no uniformes. |
| `CycleAnalysisService.analyze` | `CycleSignalAnalyzer.autocorrelation` | `series`, `max_lag` | Lista de coeficientes de correlación serial. |
| `CycleAnalysisService.analyze` | `CycleDetector.detect_robust_cycles` | `candidates`, `acf_lags` | Lista ordenada de ciclos robustos confirmados. |
| `CycleAnalysisService.analyze` | `CycleDiagnostics.evaluate` | `cycles`, `series_length`, `is_regular` | Diagnóstico de fiabilidad y calidad del ciclo. |

---

## 4. Batería de Pruebas Asociadas

El módulo cuenta con suites de pruebas unitarias específicas:
* [`tests/unit/services/analysis/macro/cycle/test_cycle_analysis_service.py`](file:///home/dano/sight/backend/tests/unit/services/analysis/macro/cycle/test_cycle_analysis_service.py): Integración del ciclo de extremo a extremo.
* [`tests/unit/services/analysis/macro/cycle/test_cycle_preprocessor.py`](file:///home/dano/sight/backend/tests/unit/services/analysis/macro/cycle/test_cycle_preprocessor.py): Inferencia de frecuencias, cálculo de regularidad y filtro HP.
* [`tests/unit/services/analysis/macro/cycle/test_cycle_signal_analyzer.py`](file:///home/dano/sight/backend/tests/unit/services/analysis/macro/cycle/test_cycle_signal_analyzer.py): FFT y periodograma de Lomb-Scargle.
* [`tests/unit/services/analysis/macro/cycle/test_cycle_detector.py`](file:///home/dano/sight/backend/tests/unit/services/analysis/macro/cycle/test_cycle_detector.py): Algoritmo de clustering y puntuación de ciclos.
* [`tests/unit/services/analysis/macro/cycle/test_cycle_temporal_gaps.py`](file:///home/dano/sight/backend/tests/unit/services/analysis/macro/cycle/test_cycle_temporal_gaps.py): Resiliencia ante lagunas cronológicas y datos no uniformemente espaciados.
