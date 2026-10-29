# Informe de Robustez y Corrección por Comparaciones Múltiples · Sight

## 1. Resumen Ejecutivo
- **Total de combinaciones evaluadas originalmente:** 1,120
- **Combinaciones con tamaño muestral suficiente ($N \ge 30$):** 750 (67.0%)
- **Combinaciones descartadas por escasez de datos ($N < 30$):** 370
- **Resultados nominalmente significativos (CI 95% sin cero):** 37 (4.93%)
- **Falsos descubrimientos esperados por puro azar (5% de 750):** ~37.5
- **Resultados que sobreviven a Benjamini-Hochberg (FDR q=0.05):** **0**
- **Resultados que sobreviven a Bonferroni (FWER α=0.05):** **0**

## 2. Diagnóstico Estadístico Fundamental
> **Conclusión clave:** El 4.93% de resultados que excluyen el cero coincide de forma casi exacta con el 5% de falsos positivos que la teoría matemática predice por mero azar bajo un nivel de confianza del 95% ($\alpha = 0,05$).
> Al ajustar el rigor estadístico con el algoritmo de Benjamini-Hochberg o Bonferroni para penalizar el haber probado 750 hipótesis simultáneas, **ninguna relación sobrevive** como señal estadística demostrada.

## 3. Desglose por Periodos Históricos
| Periodo | Combinaciones analizadas | Excluyen el cero | % Significativo | Falsos positivos esperados |
| :--- | :---: | :---: | :---: | :---: |
| **1975–1995** | 390 | 25 | 6.41% | ~19.5 |
| **1996–2015** | 360 | 12 | 3.33% | ~18.0 |
| **Total** | 750 | 37 | 4.93% | ~37.5 |

## 4. Prueba de Consistencia Temporal Cruzada (1975–1995 vs 1996–2015)
De las 37 señales nominales:
- **34** solo aparecieron en un periodo y se desvanecieron en el otro.
- **3** excluyeron el cero en ambos periodos.
- **2** mantuvieron además el **mismo signo direccional** (alcista/bajista).

### Detalle de las combinaciones activas en ambos periodos:
| Activo | Indicador | Dimensión | Categoría | Dif. 75–95 | Dif. 96–15 | ¿Mismo signo? | Diagnóstico |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `BROAD_MARKET` | `INFLATION` | `direction` | `deteriorating` | +1.62% | +1.23% | ✅ SÍ | Persistente (Señal candidata) |
| `BROAD_MARKET` | `INFLATION` | `direction` | `improving` | -2.09% | -1.82% | ✅ SÍ | Persistente (Señal candidata) |
| `GOLD` | `GDP` | `regime` | `neutral` | -14.87% | +15.79% | ❌ NO (Invertido) | Inestable (Ruptura de régimen / Ruido) |

## 5. Recomendaciones Estratégicas para el Código de Sight
1. **No sobreajustar el algoritmo:** Modificar las reglas macroeconómicas para forzar que den p-valores más altos en esta muestra incurriría en *data snooping* (sesgo de minería de datos).
2. **Reducir la fragmentación de hipótesis:** Muchas categorías sufren de $N < 30$ debido a un exceso de granularidad en las dimensiones (`assessment`, `conviction`, `confidence`, etc.). Fusionar categorías redundantes o priorizar únicamente `direction` e `INFLATION` aumentará la potencia estadística.
3. **Mantener el enfoque de contexto, no de predicción directa:** Las lecturas macroeconómicas de Sight deben tratarse como información contextual de régimen y gestión de riesgo, no como señales alfa autónomas de timing de mercado.
