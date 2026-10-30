# Informe Maestro de Auditoría y Corrección de Errores: `frontend`

Este documento consolida la auditoría técnica exhaustiva realizada sobre la aplicación frontend de **Sight** (`frontend/`). Sintetiza los errores de reglas de hooks de **React 19**, vulnerabilidades de concurrencia (*race conditions*), desajustes de contratos TypeScript frente a los modelos Pydantic del backend, bugs de visualización en series econométricas de tipo `RATE` y problemas de precisión numérica corregidos y verificados.

---

## 1. Métricas Globales de la Auditoría

* **Módulos Auditados**: 6 capas (`api/`, `hooks/`, `services/`, `layout/`, `components/`, `pages/`).
* **Incidencias Totales Subsanadas**: **10 categorías de errores críticos y moderados** (incluyendo las **14 violaciones de ESLint** y **3 advertencias de hooks**).
* **Estado de ESLint (`npm run lint`)**: **0 errores, 0 warnings** (frente a 14 errores y 3 warnings iniciales).
* **Compilación TypeScript + Vite (`npm run build`)**: **100% limpia (`tsc -b && vite build`)** en **466 ms**.

---

## 2. Matriz Consolidada de Errores por Categoría

| ID | Componente / Archivo | Error / Vulnerabilidad Detectada | Consecuencia en Producción | Solución Aplicada |
|:---|:---|:---|:---|:---|
| **FE-01** | [`IndicatorDetailPage.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/IndicatorDetailPage.tsx), [`TimelineView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/TimelineView.tsx) | Violación de `react-hooks/set-state-in-effect` (5 errores) al invocar `setState(null)` síncronamente al inicio de `useEffect`. | Renders en cascada innecesarios y parpadeos visuales al cambiar de indicador o país. | Derivación pura del estado de carga y limpieza de datos mediante clave determinista en [`useAsyncData.ts`](file:///home/dano/sight/frontend/src/hooks/useAsyncData.ts). |
| **FE-02** | [`IndicatorDetailPage.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/IndicatorDetailPage.tsx), [`CompareView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/CompareView.tsx), [`TimelineView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/TimelineView.tsx) | Violación de `react-hooks/immutability` y `exhaustive-deps` (10 incidencias): funciones `async` declaradas después del `useEffect` que las invocaba y omitidas de sus dependencias. | Captura de cierres (*closures*) obsoletos e incumplimiento del modelo de análisis estático del compilador de React 19. | Uso de `useEffectEvent` de React 19 dentro de [`useAsyncData`](file:///home/dano/sight/frontend/src/hooks/useAsyncData.ts) para estabilizar la función `fetcher`. |
| **FE-03** | [`Dashboard.tsx`](file:///home/dano/sight/frontend/src/pages/Dashboard.tsx), [`IndicatorDetailPage.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/IndicatorDetailPage.tsx), [`TimelineView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/TimelineView.tsx), [`CompareView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/CompareView.tsx) | Ausencia de `AbortController` en peticiones HTTP concurrentes. | Condición de carrera: al cambiar rápidamente de región (`EU27_2020` → `DE` → `US`), una respuesta lenta anterior podía sobrescribir los datos de la región activa. | Propagación de `AbortSignal` en [`queryService.ts`](file:///home/dano/sight/frontend/src/services/queryService.ts) y [`api.ts`](file:///home/dano/sight/frontend/src/pages/indicators/api.ts) con cancelación automática al desmontar o cambiar `key`. |
| **FE-04** | [`Dashboard.tsx`](file:///home/dano/sight/frontend/src/pages/Dashboard.tsx), [`CompareView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/CompareView.tsx) | Uso de `@typescript-eslint/no-explicit-any` (`useState<any>(null)` y `(r: { region: { code: any } })`). | Pérdida total de verificación estática de tipos en el panel de régimen macroeconómico y en la comparativa de regiones. | Exportación de [`MacroRegimeData`](file:///home/dano/sight/frontend/src/components/analysis/MacroRegime.tsx#L9-L26), creación de [`getMacroRegime()`](file:///home/dano/sight/frontend/src/services/queryService.ts#L55-L64) tipado y retorno explícito `Promise<RegionResponse[]>`. |
| **FE-05** | [`CompareView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/CompareView.tsx) | Acceso sin guarda a `data[0].indicators` tras recibir la respuesta de `/query/compare`. | `TypeError: Cannot read properties of undefined (reading 'indicators')` si el backend devolvía una lista vacía `[]`. | Eliminación del acceso inseguro a `data[0]` y manejo defensivo de listas vacías. |
| **FE-06** | [`TimelineView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/TimelineView.tsx), [`TimelineChart.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/timeline/TimelineChart.tsx), [`TimelineTable.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/timeline/TimelineTable.tsx) | Desajuste de contrato TypeScript: uso de `Observation[]` (que exige `region: Region`) en lugar de `ObservationResponse[]` (`{ date, value, source }`). | Discrepancia entre el tipo declarado en compilación y el JSON real devuelto por `GET /query/region/{r}/indicator/{i}`. | Unificación del contrato en [`ObservationResponse`](file:///home/dano/sight/frontend/src/pages/indicators/types.ts#L35-L39) a lo largo de toda la vista Timeline. |
| **FE-07** | [`FutureAnalysis.tsx`](file:///home/dano/sight/frontend/src/components/analysis/FutureAnalysis.tsx), [`types.ts`](file:///home/dano/sight/frontend/src/pages/indicators/types.ts) | El grupo **Crecimiento** sólo leía claves de `GrowthMethod.LOG` (`percentage_change`, `log_difference`, `yoy_growth`), ignorando `change` y `yoy_change`. | Para indicadores de tipo `RATE` (`INFLATION`, `UNEMPLOYMENT`, `INTEREST_RATE`, `TRADE`), la interfaz mostraba `"—"` en 5 de las 6 métricas de crecimiento. | Detección dinámica `isRateSeries` en [`FutureAnalysis.tsx`](file:///home/dano/sight/frontend/src/components/analysis/FutureAnalysis.tsx#L18-L48) e inclusión de `change` y `yoy_change` en [`FeatureValues`](file:///home/dano/sight/frontend/src/pages/indicators/types.ts#L79-L118). |
| **FE-08** | [`IndicatorDetailPage.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/IndicatorDetailPage.tsx), [`TimelineView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/TimelineView.tsx), [`api.ts`](file:///home/dano/sight/frontend/src/pages/indicators/api.ts) | Desalineación en la resolución de códigos de indicadores comerciales (`EXPORTS`, `IMPORTS`, `TRADE`) por país. | Mientras `TimelineView` resolvía `EXPORTS_BY_COUNTRY` para países de la UE, `IndicatorDetailPage` pedía `/analysis/features/EXPORTS/DE` y además traducía erróneamente `US` a `*_BY_COUNTRY` (provocando errores 404). | Centralización de [`resolveIndicatorCode(baseCode, regionCode)`](file:///home/dano/sight/frontend/src/pages/indicators/api.ts#L21-L30) en `api.ts`, preservando `EU27_2020` y `US` y compartiéndola con todos los endpoints de análisis. |
| **FE-09** | [`FeatureMetric.tsx`](file:///home/dano/sight/frontend/src/components/analysis/FeatureMetric.tsx) | Formateo numérico con `maximumFractionDigits: 2` fijo y sin guarda `Number.isFinite(value)`. | Valores decimales pequeños como `log_difference` (`0.0042`) o pendientes OLS (`0.0018`) se redondeaban a `"0"`, perdiendo toda precisión analítica. | Guarda `!Number.isFinite(value)` y precisión adaptativa de hasta **4 decimales** cuando `0 < |value| < 1`. |
| **FE-10** | [`FeatureGroup.tsx`](file:///home/dano/sight/frontend/src/components/analysis/FeatureGroup.tsx), [`CompareView.tsx`](file:///home/dano/sight/frontend/src/pages/indicators/views/CompareView.tsx), [`queryService.ts`](file:///home/dano/sight/frontend/src/services/queryService.ts) | Trazas `console.log` masivas ejecutadas en cada ciclo de renderizado. | Degradación del rendimiento del hilo principal del navegador y ruido en la consola de producción. | Eliminación completa de trazas de depuración en componentes y servicios. |

---

## 3. Análisis en Profundidad de los Bugs Sistémicos Más Críticos

### Caso 1: Condiciones de Carrera y Violaciones de Hooks en React 19 (`FE-01`, `FE-02`, `FE-03`)
* **Naturaleza del Fallo**: En la implementación original de `IndicatorDetailPage.tsx` y `TimelineView.tsx`, cada petición asíncrona utilizaba tres `useState` separados (`data`, `loading`, `error`) y llamaba a `setState(null)` de forma síncrona dentro de `useEffect` antes de disparar una función declarada más abajo en el componente:
  ```tsx
  // ❌ ANTES: Violación de set-state-in-effect, immutability y condición de carrera
  useEffect(() => {
    if (!code || !selectedRegion) {
      setFeatureAnalysis(null);
      return;
    }
    loadFeatureAnalysis(code, selectedRegion);
  }, [code, selectedRegion]);
  ```
* **Impacto Real**:
  1. React 19 ejecuta un render con los datos del país anterior, dispara el efecto y fuerza un segundo render inmediato al hacer `setState(null)`.
  2. Si el usuario cambiaba de `EU27_2020` a `DE` y luego a `ES`, las tres peticiones quedaban en vuelo sin `AbortController`; si la respuesta de `DE` tardaba más que la de `ES`, la pantalla terminaba mostrando los datos de Alemania bajo el selector de España.
* **Solución**: Se creó [`useAsyncData.ts`](file:///home/dano/sight/frontend/src/hooks/useAsyncData.ts), donde cada respuesta queda sellada con su `key` de origen y cada cambio de `key` aborta la petición previa:
  ```tsx
  // ✅ DESPUÉS: Derivación sin setState síncrono + cancelación por AbortSignal
  const isCurrentKey = key !== null && state.key === key;
  const data = isCurrentKey ? state.data : null;
  const loading = key !== null && state.key !== key;
  ```

---

### Caso 2: Omisión de Métricas de Crecimiento en Series `GrowthMethod.RATE` (`FE-07`)
* **Naturaleza del Fallo**: Como parte del blindaje econométrico del backend (`FEAT-01`), los indicadores expresados en tasas o saldos (`INFLATION`, `UNEMPLOYMENT`, `INTEREST_RATE`, `TRADE`) utilizan `GrowthMethod.RATE`, produciendo `change` (diferencia simple $X_t - X_{t-1}$), `yoy_change` ($X_t - X_{t-P}$) y `momentum`. Sin embargo, [`FutureAnalysis.tsx`](file:///home/dano/sight/frontend/src/components/analysis/FutureAnalysis.tsx) tenía codificadas de forma rígida únicamente las columnas de `GrowthMethod.LOG` (`percentage_change`, `log_difference`, `yoy_growth`, `yoy_log_growth`, `cumulative_growth`).
* **Impacto Real**: Al abrir cualquier indicador de tipos de interés o desempleo, el panel de **Crecimiento** aparecía prácticamente vacío (`"—"` en 5 de 6 casillas), ocultando las variaciones periódicas e interanuales calculadas por el backend.
* **Solución**: [`FutureAnalysis.tsx`](file:///home/dano/sight/frontend/src/components/analysis/FutureAnalysis.tsx#L18-L48) detecta ahora si el conjunto de features corresponde a una serie `RATE` y conmuta automáticamente las tarjetas del grupo **Crecimiento** para mostrar `Variación del periodo (change)`, `Variación interanual (yoy_change)` y `Momentum`.

---

### Caso 3: Desalineación de Códigos Comerciales en `IndicatorDetailPage` (`FE-08`)
* **Naturaleza del Fallo**: En el catálogo de Sight, las tarjetas de comercio exterior navegan a `/indicators/EXPORTS`, `/indicators/IMPORTS` y `/indicators/TRADE`. Para los Estados miembros de la UE (`DE`, `FR`, `ES`, etc.), Eurostat almacena las series desagregadas bajo `EXPORTS_BY_COUNTRY`, `IMPORTS_BY_COUNTRY` y `TRADE_BALANCE_BY_COUNTRY`.
* **Impacto Real**:
  1. `TimelineView.tsx` traducía el código localmente, pero `IndicatorDetailPage.tsx` seguía enviando `EXPORTS`, `IMPORTS` y `TRADE` sin traducir a `/analysis/features`, `/analysis/cycle` y `/analysis/investment`, recibiendo errores `404 Not Found` para todos los países europeos.
  2. Además, para Estados Unidos (`US`), cuyos datos provienen de BEA bajo `EXPORTS` e `IMPORTS`, `TimelineView.tsx` intentaba pedir `EXPORTS_BY_COUNTRY`, fallando también con 404.
* **Solución**: Se extrajo [`resolveIndicatorCode(baseCode, regionCode)`](file:///home/dano/sight/frontend/src/pages/indicators/api.ts#L21-L30) a `api.ts`, manteniendo el código base para `EU27_2020` y `US` y aplicando la traducción `*_BY_COUNTRY` tanto en `TimelineView.tsx` como en los tres hooks de análisis de `IndicatorDetailPage.tsx`.

---

### Caso 4: Truncamiento a `"0"` de Pendientes OLS y Diferencias Logarítmicas (`FE-09`)
* **Naturaleza del Fallo**: [`FeatureMetric.tsx`](file:///home/dano/sight/frontend/src/components/analysis/FeatureMetric.tsx) formateaba todas las métricas no porcentuales mediante `Intl.NumberFormat("es-ES", { maximumFractionDigits: 2 })`.
* **Impacto Real**: Métricas como `log_difference` (típicamente entre `0.0010` y `0.0090` en series mensuales de IPC o PIB) o pendientes OLS (`rolling_slope_short`, `rolling_slope_medium`, `rolling_slope_long`, `slope_change`) en series de desempleo y tipos se redondeaban sistemáticamente a `"0"`, impidiendo distinguir una tendencia alcista suave de un estancamiento.
* **Solución**: Se añadió precisión adaptativa (`maximumFractionDigits: Math.abs(value) > 0 && Math.abs(value) < 1 ? 4 : 2`) y validación `Number.isFinite(value)`.

---

## 4. Patrones de Diseño Defensivo Instituidos en el Frontend

1. **Prohibición de `setState` Síncrono en Efectos**:
   Todo estado derivado de props o de respuestas de red se calcula durante el renderizado o a través de [`useAsyncData`](file:///home/dano/sight/frontend/src/hooks/useAsyncData.ts).
2. **Reinicio Declarativo mediante `key`**:
   Los componentes con estado de selección interna dependiente del indicador (como [`CompareView`](file:///home/dano/sight/frontend/src/pages/indicators/views/CompareView.tsx)) se montan con `key={code}` desde su contenedor padre para reiniciar limpiamente su estado sin efectos secundarios.
3. **Cancelación Obligatoria con `AbortSignal`**:
   Ninguna función de [`api.ts`](file:///home/dano/sight/frontend/src/pages/indicators/api.ts) ni de [`queryService.ts`](file:///home/dano/sight/frontend/src/services/queryService.ts) se invoca desde un efecto sin pasar el `signal` del `AbortController` activo.
4. **Cero Tolerancia a `any` y Verificación en CI**:
   `npm run lint` y `npm run build` (`tsc -b`) se ejecutan sin errores ni advertencias como requisito previo a cada commit.
