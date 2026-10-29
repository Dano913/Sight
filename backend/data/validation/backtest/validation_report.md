# Informe de validación histórica — Sight

**Estado:** validación parcial  
**Periodo evaluado:** enero de 1975 – diciembre de 2015  
**Frecuencia:** mensual  
**Horizontes:** 3, 6, 12 y 24 meses

## 1. Objetivo

Evaluar la calidad metodológica y la estabilidad de los resultados del backtest histórico de Sight, distinguiendo entre el comportamiento histórico de los activos y la capacidad del sistema para relacionarlo con los regímenes macroeconómicos.

## 2. Metodología

El backtest utiliza observaciones mensuales y calcula rentabilidades futuras para cuatro horizontes temporales. La validación estadística incluye análisis por subperiodos, estimación de incertidumbre mediante bootstrap circular por bloques y análisis de sensibilidad a distintas longitudes de bloque.

Se han utilizado 2.000 réplicas de bootstrap, semilla fija 42 y longitudes de bloque de 6, 12 y 24 meses para el análisis de robustez.

## 3. Resultados

### 3.1. Suficiencia de la muestra

Se dispone de 492 observaciones mensuales por activo y horizonte en los resultados analizados. Sin embargo, las rentabilidades futuras de distintos meses se solapan, por lo que las observaciones no pueden considerarse independientes.

### 3.2. Estabilidad temporal

El análisis divide el periodo histórico en cuatro subperiodos: 1975–1984, 1985–1994, 1995–2004 y 2005–2015.

Las rentabilidades medias varían entre subperiodos. En el activo BROAD_MARKET se observa una reducción de las medias entre periodos, mientras que la dispersión aumenta con horizontes más largos. Los percentiles inferiores también muestran que pueden producirse rentabilidades negativas pese a una media positiva.

### 3.3. Incertidumbre estadística

Para BROAD_MARKET, los resultados del bootstrap con bloques de 12 meses son:

| Horizonte | Rentabilidad media | Intervalo del 95 % |
|---|---:|---:|
| 3 meses | 3,11 % | 1,91 % a 4,20 % |
| 6 meses | 6,26 % | 3,90 % a 8,32 % |
| 12 meses | 12,93 % | 8,52 % a 16,86 % |
| 24 meses | 27,14 % | 20,58 % a 33,51 % |

En estos cuatro casos, los intervalos estimados excluyen el cero. Esto describe la incertidumbre de las rentabilidades medias históricas bajo el procedimiento empleado; no demuestra capacidad predictiva del modelo macroeconómico.

### 3.4. Robustez

Se compararon longitudes de bloque de 6, 12 y 24 meses. En 36 de las 40 combinaciones de activo y horizonte, los intervalos excluyen el cero en las tres configuraciones. Cuatro combinaciones no mantienen esa conclusión en todos los escenarios.

Los resultados dependen parcialmente de la longitud de bloque elegida, especialmente en horizontes largos. Además, el análisis de 40 combinaciones implica un problema potencial de comparaciones múltiples que debe tenerse en cuenta al interpretar los intervalos.

### 3.5. Coherencia de los regímenes macroeconómicos

La distribución actual de `signals_by_month.csv` contiene 492 observaciones clasificadas como `neutral`, todas con `signal_status = no_cyclical_evidence`.

Por tanto, la fase de validación de regímenes macroeconómicos permanece pendiente. En su estado actual, el backtest no permite determinar si las distintas fases del ciclo económico se asocian con diferencias sistemáticas en las rentabilidades futuras.

## 4. Limitaciones metodológicas

- No se incorpora la disponibilidad histórica real de los datos en la fecha de cada señal; no se controla el momento de publicación ni la información revisada posteriormente.
- La selección de fuentes se basa en la cobertura del periodo completo.
- Para calcular la rentabilidad futura, se utiliza la primera observación de mercado disponible en la fecha objetivo o después de ella.
- Las rentabilidades futuras solapadas no son independientes.
- La sensibilidad del bootstrap se ha evaluado con tres longitudes de bloque, pero esto no garantiza robustez frente a todas las especificaciones posibles.
- La clasificación macroeconómica no diferencia actualmente las fases del ciclo en las señales del backtest.

## 5. Conclusiones

La validación ha permitido caracterizar la estabilidad temporal de las rentabilidades históricas y estudiar su incertidumbre mediante bootstrap y análisis de sensibilidad.

Los resultados positivos de algunos activos y horizontes no deben interpretarse como evidencia de que Sight prediga rentabilidades o identifique oportunidades de inversión. Para sostener esa conclusión sería necesario demostrar que las señales macroeconómicas distinguen regímenes coherentes y que esa diferenciación aporta información útil sobre resultados futuros.

La validación temporal también presenta limitaciones relacionadas con la disponibilidad histórica de los datos y la selección de fuentes.

## 6. Trabajo pendiente

1. Resolver y validar la clasificación de regímenes macroeconómicos.
2. Repetir el análisis de coherencia una vez que el clasificador produzca resultados diferenciados y económicamente interpretables.
3. Evaluar si las diferencias entre regímenes son estadísticamente estables y económicamente relevantes.
4. Abordar las limitaciones de disponibilidad temporal de los datos antes de extraer conclusiones predictivas.
5. Consolidar los resultados y las limitaciones en una versión final del informe.

**Conclusión general:** la validación estadística descriptiva está avanzada, pero la capacidad predictiva macroeconómica de Sight todavía no ha quedado demostrada.