# Arquitectura de Normalizadores de Datos: `app/normalizers`

El directorio `app/normalizers` constituye la frontera de traducción y saneamiento de datos entre las respuestas heterogéneas de los proveedores externos (`Eurostat`, `BEA`, `BLS`, `NBS`) y el modelo de dominio canónico [`Observation`](file:///home/dano/sight/backend/app/models/observation.py) de **Sight**.

---

## 1. Principios de Diseño

1. **Contrato de Salida Único (`list[Observation]`)**:
   - Todos los normalizadores exponen la firma estática uniforme `to_observations(data, indicator_code: str, source_code: str) -> list[Observation]`.
2. **Alineación Temporal Canónica (Inicio de Período)**:
   - Todas las frecuencias se normalizan a objetos `datetime.date` en el primer día del período correspondiente:
     - **Anual (`YYYY`)**: `YYYY-01-01`
     - **Trimestral (`YYYY-Q1`..`Q4`, `YYYYQ1`..`Q4`, `YYYYA`..`D`)**: `YYYY-01-01`, `YYYY-04-01`, `YYYY-07-01`, `YYYY-10-01`
     - **Mensual (`YYYY-MM`, `M01`..`M12`, `YYYYMM`)**: `YYYY-MM-01`
3. **Filtrado Defensivo de Valores No Finitos y Banderas Estadísticas**:
   - Se descartan silenciosamente marcadores de dato faltante o confidencial (`None`, `""`, `"(NA)"`, `"-"`, `"."`, `":"`, `"c"`, `"e"`), así como valores `NaN`, `inf` o `-inf` mediante `math.isfinite()`.

---

## 2. Mapa de Estructura

```
backend/app/normalizers/
├── __init__.py               # Exportación formal (__all__) de los 4 normalizadores
├── eurostat_normalizer.py    # Normalizador de DataFrames SDMX de Eurostat (anual, trimestral y mensual)
├── bea_normalizer.py         # Normalizador de tabla NIPA T10106 del BEA (conversión de millones a miles de millones USD)
├── bls_normalizer.py         # Normalizador de series temporales mensuales M01..M12 del BLS
└── nbs_normalizer.py         # Normalizador híbrido para NBS China (sobre nativo returndata.datanodes y listas planas)
```

---

## 3. Reglas de Transformación por Proveedor

| Normalizador | Formato de Entrada | Reglas de Filtrado y Transformación | Escalado / Unidad |
|:---|:---|:---|:---|
| [`EurostatNormalizer`](file:///home/dano/sight/backend/app/normalizers/eurostat_normalizer.py) | `pd.DataFrame` ancho (columnas de dimensión + columnas temporales) | 1. Filtra dimensiones por indicador (`FILTERS`).<br>2. Detecta la columna geográfica (`geo\TIME_PERIOD`, `geo\time` o `geo`).<br>3. Clasifica columnas temporales según frecuencia y convierte cada celda finita en `Observation`. | Mantiene la unidad oficial del dataset Eurostat. |
| [`BeaNormalizer`](file:///home/dano/sight/backend/app/normalizers/bea_normalizer.py) | `list[dict]` (filas JSON de NIPA `T10106`) | 1. Selecciona `SeriesCode` según el indicador (`GDP` → `A191RX`, `EXPORTS` → `A020RX`, `IMPORTS` → `A021RX`).<br>2. Limpia separadores de miles (`","`) en `DataValue`.<br>3. Convierte trimestres `YYYYQ1`..`YYYYQ4` a `date`. | Divide entre `1000.0` (de millones de USD a miles de millones de USD, `BILLION_USD`). |
| [`BlsNormalizer`](file:///home/dano/sight/backend/app/normalizers/bls_normalizer.py) | `list[dict]` (`{"year", "period", "value"}`) | 1. Filtra períodos mensuales válidos (`M01`..`M12`), descartando medias anuales (`M13`) y marcadores `"-"`.<br>2. Construye `date(year, month, 1)`. | Mantiene el valor en índice o porcentaje (`PERCENT` / `INDEX`). |
| [`NbsNormalizer`](file:///home/dano/sight/backend/app/normalizers/nbs_normalizer.py) | `dict` (`returndata.datanodes`) o `list[dict]` | 1. Extrae nodos con `hasdata == True` y dimensión temporal `wdcode == "sj"`.<br>2. Soporta códigos anuales (`2024`), trimestrales (`2024A`..`D`) y mensuales (`202401`..`12`). | Mantiene la unidad nativa reportada por NBS. |
