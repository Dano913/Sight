# Registro Técnico de Errores Corregidos: `app/services/catalog`

Este documento recopila de forma detallada todos los fallos críticos, mutaciones de datos en memoria, cuellos de botella de rendimiento, lagunas de cálculo sintético e inconsistencias de caché detectados y corregidos en el bloque `app/services/catalog/` y su capa de persistencia (`app/repositories/` y SQLite).

---

## Índice de Errores Corregidos

1. [Error 1: Corrupción de datos en memoria por mutación *in-place* (`value /= 27`)](#error-1-corrupción-de-datos-en-memoria-por-mutación-in-place-value--27)
2. [Error 2: Cálculo huérfano y parcial del indicador sintético `TRADE`](#error-2-cálculo-huérfano-y-parcial-del-indicador-sintético-trade)
3. [Error 3: Inconsistencia y desincronización de caché en memoria (`query_cache`)](#error-3-inconsistencia-y-desincronización-de-caché-en-memoria-query_cache)
4. [Error 4: Escaneo secuencial (*Full Table Scan*) y ausencia de índices compuestos en SQLite](#error-4-escaneo-secuencial-full-table-scan-y-ausencia-de-índices-compuestos-en-sqlite)
5. [Error 5: Degradación de rendimiento en deserialización de filas a modelos Pydantic (532 ms vs 35 ms)](#error-5-degradación-de-rendimiento-en-deserialización-de-filas-a-modelos-pydantic-532-ms-vs-35-ms)
6. [Error 6: Monolito de 770 líneas con condicionales repetitivos en `ObservationService`](#error-6-monolito-de-770-líneas-con-condicionales-repetitivos-en-observationservice)
7. [Error 7: Falta de transacciones atómicas en escrituras por lotes de observaciones](#error-7-falta-de-transacciones-atómicas-en-escrituras-por-lotes-de-observaciones)

---

### Error 1: Corrupción de datos en memoria por mutación *in-place* (`value /= 27`)
* **Severidad:** 🔴 **Crítica (Integridad de Datos Macro)**
* **Archivo afectado:** [`app/services/catalog/query_service.py`](file:///home/dano/sight/backend/app/services/catalog/query_service.py) (`QueryService.compare_regions()`)

#### Descripción del Fallo y Causa Raíz
En el método `QueryService.compare_regions()`, existía un condicional destinado a "normalizar" el PIB de la Unión Europea frente a países individuales:
```python
# Código original con error:
if indicator_code == "GDP" and "EU27_2020" in grouped:
    for observation in grouped["EU27_2020"]:
        observation.value /= 27  # <-- ¡Mutación in-place destructiva!
```
1. Al modificar el atributo `observation.value` directamente sobre la instancia existente, si la lista de observaciones procedía de la caché en memoria o era compartida por otras partes de la aplicación, el objeto quedaba **permanentemente dividido entre 27**.
2. Si un usuario o proceso volvía a consultar el PIB de la Unión Europea, el dato ya no era el PIB oficial (aprox. 15 billones de dólares), sino que se redividía entre 27 en cada llamada subsecuente (555.000 millones, luego 20.000 millones, etc.).
3. **Fallo econométrico conceptual:** Dividir el PIB conjunto de la UE entre 27 no representa ni el PIB per cápita (dado que los países tienen poblaciones enormemente distintas: 84M en Alemania vs 500K en Malta), ni una media económica ponderada válida.

#### Solución Aplicada
Se suprimió por completo la mutación destructiva. Las comparaciones regionales devuelven estrictamente las cifras oficiales reportadas por Eurostat sin alteraciones arbitrarias sobre las observaciones.

---

### Error 2: Cálculo huérfano y parcial del indicador sintético `TRADE`
* **Severidad:** 🟠 **Alta (Funcionalidad Incompleta / Falla en Consultas Globales)**
* **Archivo afectado:** [`app/services/catalog/query_service.py`](file:///home/dano/sight/backend/app/services/catalog/query_service.py)

#### Descripción del Fallo y Causa Raíz
El indicador `TRADE` (Balanza Comercial) se calcula de forma sintética a partir de las exportaciones e importaciones:
$$\text{TRADE} = \text{EXPORTS} - \text{IMPORTS}$$
El cálculo estaba codificado de forma aislada y estricta únicamente dentro del método `get_by_region_and_indicator()`.
Si el cliente o la API invocaba:
* `QueryService.get_by_indicator("TRADE")`
* `QueryService.compare_regions("TRADE", ["DE", "FR", "ES"])`
la llamada fallaba con un error o devolvía listas vacías porque `TRADE` no existe como registro físico en la tabla SQLite `observations` y no se calculaba en esas funciones.

#### Solución Aplicada
Se desacopló la lógica sintética creando la función generalizada `_compute_trade_observations(region_code: str | None = None)`.
* Si `region_code` se proporciona, calcula la diferencia para dicha región.
* Si `region_code` es `None`, recupera las exportaciones e importaciones de todas las regiones soportadas, sincroniza las fechas por pares y emite la balanza comercial de forma homogénea para todos los países.
* Ambos endpoints (`get_by_indicator` y `compare_regions`) ahora delegan en esta función ante consultas de `TRADE`.

---

### Error 3: Inconsistencia y desincronización de caché en memoria (`query_cache`)
* **Severidad:** 🟡 **Media (Consistencia de Datos / Lecturas Obsoletas)**
* **Archivos afectados:**
  - [`app/services/catalog/observation_service.py`](file:///home/dano/sight/backend/app/services/catalog/observation_service.py)
  - [`app/services/catalog/query_service.py`](file:///home/dano/sight/backend/app/services/catalog/query_service.py)
  - [`app/cache/query_cache.py`](file:///home/dano/sight/backend/app/cache/query_cache.py)

#### Descripción del Fallo y Causa Raíz
1. **Desincronización tras refresco:** Cuando un usuario o tarea programada solicitaba actualizar datos desde proveedores oficiales mediante `ObservationService.get_observations(..., refresh=True)`, la base de datos SQLite se actualizaba correctamente con las nuevas filas. Sin embargo, **`query_cache` nunca era invalidada**. Como consecuencia, las peticiones HTTP subsiguientes continuaban sirviendo los datos viejos cacheados durante los 5 minutos de tiempo de vida (TTL).
2. **Chequeo tardío de caché:** En varios métodos de `QueryService`, se ejecutaban validaciones de catálogo o transformaciones previas antes de verificar si la respuesta ya residía en caché.

#### Solución Aplicada
1. En `ObservationService`: Cada vez que se reemplazan observaciones en SQLite (`ObservationRepository.replace_by_region_indicator_source` o `replace_batch`), se ejecuta inmediatamente `query_cache.clear()`, invalidando de forma automática las respuestas cacheadas y garantizando consistencia inmediata.
2. En `QueryService`: Se colocó la comprobación de clave de caché en la primera línea de ejecución de todos los métodos de consulta.

---

### Error 4: Escaneo secuencial (*Full Table Scan*) y ausencia de índices compuestos en SQLite
* **Severidad:** 🟠 **Alta (Rendimiento y Escalabilidad de Base de Datos)**
* **Archivos afectados:**
  - [`app/repositories/observation_repository.py`](file:///home/dano/sight/backend/app/repositories/observation_repository.py)
  - [`app/database/sight.db`](file:///home/dano/sight/backend/app/database/sight.db)

#### Descripción del Fallo y Causa Raíz
La tabla `observations` almacenaba más de 30.000 observaciones macroeconómicas y solo contaba con la restricción de clave única:
```sql
UNIQUE(region_code, indicator_code, source_code, date)
```
Dado que `region_code` era la primera columna de la clave única:
1. Una consulta como `SELECT * FROM observations WHERE indicator_code = 'GDP'` no podía utilizar el índice y obligaba al motor SQLite a escanear secuencialmente toda la tabla fila por fila (*Full Table Scan*).
2. El método `ObservationRepository.exists(indicator_code, region_code)` ejecutaba `SELECT COUNT(*) FROM observations ...`, obligando a contar todos los miles de registros coincidentes en lugar de detenerse en el primer resultado encontrado.

#### Solución Aplicada
1. **Creación de índices compuestos en SQLite:**
   ```sql
   CREATE INDEX IF NOT EXISTS idx_observations_indicator_region 
   ON observations (indicator_code, region_code);

   CREATE INDEX IF NOT EXISTS idx_observations_region_indicator 
   ON observations (region_code, indicator_code);

   CREATE INDEX IF NOT EXISTS idx_observations_indicator 
   ON observations (indicator_code);
   ```
2. **Optimización con parada temprana ($O(1)$) en `exists()`:**
   Se reformuló la consulta SQL para usar `SELECT 1 ... LIMIT 1`:
   ```sql
   SELECT 1 FROM observations 
   WHERE indicator_code = ? AND region_code = ? 
   LIMIT 1
   ```
   La búsqueda se detiene en el primer nodo del árbol B-Tree, convirtiendo la verificación de existencia en una operación prácticamente instantánea.

---

### Error 5: Degradación de rendimiento en deserialización de filas a modelos Pydantic (532 ms vs 35 ms)
* **Severidad:** 🟠 **Alta (Cuello de Botella en CPU y Asignación de Memoria)**
* **Archivos afectados:**
  - [`app/repositories/observation_repository.py`](file:///home/dano/sight/backend/app/repositories/observation_repository.py)
  - [`app/services/catalog/region_service.py`](file:///home/dano/sight/backend/app/services/catalog/region_service.py)
  - [`app/services/catalog/indicator_service.py`](file:///home/dano/sight/backend/app/services/catalog/indicator_service.py)
  - [`app/services/catalog/source_service.py`](file:///home/dano/sight/backend/app/services/catalog/source_service.py)
  - [`app/services/catalog/category_service.py`](file:///home/dano/sight/backend/app/services/catalog/category_service.py)

#### Descripción del Fallo y Causa Raíz
Al recuperar registros de SQLite, el método `ObservationRepository._rows_to_observations(rows)` transformaba cada tupla devuelta por la base de datos en una instancia del modelo Pydantic `Observation`. Para ello, invocaba repetidamente:
```python
region = RegionService.get_region(row[0])
indicator = IndicatorService.get_indicator(row[1])
source = SourceService.get_by_code(row[2])
```
Cada uno de estos métodos volvía a instanciar listas completas de modelos Pydantic (`Region(...)`, `Indicator(...)`, etc.) para luego buscar en ellas mediante bucles lineales.
* En una consulta habitual de 7.870 observaciones (como `INTEREST_RATE` para todas las regiones), **se creaban y destruían más de 300.000 objetos temporales de Pydantic** en cuestión de milisegundos.
* Tiempo medido antes de la optimización: **532.5 ms** por consulta.

#### Solución Aplicada
Se transformaron `RegionService`, `IndicatorService`, `SourceService` y `CategoryService` en catálogos estáticos singleton:
1. Las entidades se instancian una única vez al importar el módulo y se almacenan en diccionarios indexados por clave normalizada (`.upper()`).
2. Las llamadas a `get_region()`, `get_indicator()` y `get_by_code()` se convirtieron en búsquedas directas en tabla hash en tiempo constante $O(1)$.
3. **Resultado:** El tiempo de deserialización para las mismas 7.870 observaciones cayó de **532.5 ms a 35.0 ms** (**16 veces más rápido**), liberando presión masiva sobre el *Garbage Collector* de Python.

---

### Error 6: Monolito de 770 líneas con condicionales repetitivos en `ObservationService`
* **Severidad:** 🟡 **Media (Mantenibilidad y Deuda Técnica)**
* **Archivo afectado:** [`app/services/catalog/observation_service.py`](file:///home/dano/sight/backend/app/services/catalog/observation_service.py)

#### Descripción del Fallo y Causa Raíz
La versión original de `ObservationService` contenía un método de 770 líneas compuesto íntegramente por cadenas interminables de `if / elif`:
```python
if indicator_code == "GDP":
    client = BeaClient()
    normalizer = BeaNormalizer()
    ...
elif indicator_code == "CPI":
    client = BlsClient()
    normalizer = BlsNormalizer()
    ...
```
Esta arquitectura hacía extremadamente frágil la incorporación de nuevos indicadores o proveedores, dificultaba las pruebas unitarias y propiciaba errores de copy-paste.

#### Solución Aplicada
Se refactorizó el servicio mediante un registro declarativo `_FETCHER_REGISTRY`:
```python
_FETCHER_REGISTRY: dict[str, tuple[Callable, Callable, str]] = {
    "GDP": (EurostatClient.get_gdp, EurostatNormalizer.to_observations, "EUROSTAT"),
    "CPI": (BlsClient.get_cpi, BlsNormalizer.to_observations, "BLS"),
    ...
}
```
El archivo se redujo a menos de 180 líneas, con una función de despacho limpia, desacoplada y fácilmente extensible.

---

### Error 7: Falta de transacciones atómicas en escrituras por lotes de observaciones
* **Severidad:** 🟡 **Media (Resiliencia ante Fallos en Base de Datos)**
* **Archivo afectado:** [`app/repositories/observation_repository.py`](file:///home/dano/sight/backend/app/repositories/observation_repository.py)

#### Descripción del Fallo y Causa Raíz
Al sincronizar grandes volúmenes de observaciones agrupadas por región e indicador, las eliminaciones e inserciones no se ejecutaban dentro de una única transacción atómica explícita con control de rollback. Si la conexión a la base de datos se interrumpía o un valor arrojaba error a mitad de proceso, la tabla quedaba en un estado corrupto con datos borrados y nuevas observaciones incompletas.

#### Solución Aplicada
Se implementó `replace_batch(grouped_observations)` utilizando un bloque transaccional explícito:
```python
with connection:
    cursor.execute("BEGIN TRANSACTION")
    # ... eliminaciones de series e inserciones masivas executemany() ...
    # Commit automático al finalizar el context manager, o ROLLBACK ante excepción.
```
Garantizando que las operaciones de actualización masiva sean estrictamente ACID (todo se actualiza o nada se modifica).

---

## Verificación y Pruebas Unitarias del Catálogo

Se diseñó y ejecutó una batería de tests unitarios específicos en [`tests/unit/services/catalog/`](file:///home/dano/sight/backend/tests/unit/services/catalog/):
* `test_catalog_services.py`: Comprueba el acceso $O(1)$, la inmutabilidad y la insensibilidad a mayúsculas/minúsculas de indicadores, regiones, fuentes y categorías.
* `test_query_service.py`: Verifica que `compare_regions` no altere los objetos en sitio, que `_compute_trade_observations` opere correctamente y que la caché responda sin fallos.
* `test_observation_repository.py`: Valida los índices SQLite, la parada temprana de `exists()`, las transacciones atómicas de `replace_batch` y la deserialización ultrarrápida.
* `test_observation_service.py`: Asegura que el registro declarativo invoque a los clientes y normalizadores correctos e invalide la caché tras cada escritura.

```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/unit/services/catalog/
# 23 passed in 0.35s
```
