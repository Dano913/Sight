# Arquitectura de Clientes de Ingesta Externa: `app/clients`

El directorio `app/clients` implementa la capa de conectividad HTTP y extracción de datos primarios de **Sight** frente a las agencias estadísticas oficiales internacionales: **Eurostat** (Unión Europea y Estados miembros), **BEA** (*Bureau of Economic Analysis*, EE. UU.), **BLS** (*Bureau of Labor Statistics*, EE. UU.) y **NBS** (*National Bureau of Statistics*, China).

---

## 1. Principios de Diseño

1. **Desacoplamiento entre Transporte y Normalización**:
   - Los clientes (`BeaClient`, `BlsClient`, `EurostatClient`, `NbsClient`) sólo gestionan la autenticación, paginación temporal, reintentos, control de frecuencia (*rate limiting*) y validación estructural de las respuestas crudas. No dependen de los modelos de dominio `Observation` ni de SQLite.
2. **Resolución Dinámica de Credenciales**:
   - Las claves de API (`BEA_API_KEY`, `BLS_API_KEY`) se resuelven dinámicamente en el momento de la petición (`cls._get_api_key()`), permitiendo inyectar variables de entorno en caliente o en baterías de pruebas sin depender del orden de importación de módulos.
3. **Tolerancia a Fallos de Red y WAF**:
   - Timeouts explícitos en todas las llamadas `requests` (`20s`–`30s`), conversión de fallos de transporte/parseo JSON a `RuntimeError` descriptivos y, en el caso de `NbsClient`, gestión de sesión con precarga de cookies, rotación de *User-Agent* y *backoff* exponencial con *jitter*.

---

## 2. Mapa de Estructura

```
backend/app/clients/
├── __init__.py            # Exportación formal (__all__) de los 4 clientes
├── eurostat_client.py     # Cliente SDMX/DataFrame para Eurostat (UE-27 y 14 países europeos)
├── bea_client.py          # Cliente REST JSON para BEA (Tabla NIPA T10106: GDP, EXPORTS, IMPORTS de EE. UU.)
├── bls_client.py          # Cliente REST JSON v2 para BLS (CPI, Inflación YoY derivada y Desempleo de EE. UU.)
└── nbs_client.py          # Cliente resiliente para NBS China (CPI, GDP, Desempleo e Inflación)
```

---

## 3. Flujo de Integración con `ObservationService` y Normalizadores

```mermaid
flowchart LR
    subgraph Providers ["Agencias Estadísticas Oficiales"]
        API_EU["Eurostat API (SDMX)"]
        API_BEA["BEA NIPA API (T10106)"]
        API_BLS["BLS Public API v2"]
        API_NBS["NBS China easyquery"]
    end

    subgraph Clients ["1. Capa de Clientes (app/clients)"]
        EC["EurostatClient"]
        BC["BeaClient"]
        BLC["BlsClient"]
        NC["NbsClient"]
    end

    subgraph Normalizers ["2. Capa de Normalización (app/normalizers)"]
        EN["EurostatNormalizer"]
        BN["BeaNormalizer"]
        BLN["BlsNormalizer"]
        NN["NbsNormalizer"]
    end

    subgraph Catalog ["3. Persistencia (app/services/catalog)"]
        OS["ObservationService.get_observations()"]
        DB[("SQLite (observations)")]
    end

    API_EU --> EC -->|"pd.DataFrame"| EN
    API_BEA --> BC -->|"list[dict] (NIPA)"| BN
    API_BLS --> BLC -->|"list[dict] (Series)"| BLN
    API_NBS --> NC -->|"dict (returndata)"| NN

    EN & BN & BLN & NN -->|"list[Observation]"| OS --> DB
```

---

## 4. Catálogo de Datasets y Series por Cliente

| Cliente | Método Público | Dataset / Serie Oficial | Indicador Sight | Cobertura Geográfica | Frecuencia Nativa |
|:---|:---|:---|:---|:---|:---|
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_gdp()` | `nama_10_gdp` (`B1G`, `CLV05_MEUR`) | `GDP` | `EU27_2020` + 14 países UE | Anual |
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_inflation()` | `prc_hicp_aind` (`CP00`, `RCH_A_AVG`) | `INFLATION` | `EU27_2020` + 14 países UE | Anual |
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_cpi()` | `prc_hicp_midx` | `CPI` | `EU27_2020` + 14 países UE | Mensual |
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_unemployment()` | `une_rt_a` (`PC_ACT`, `Y15-74`) | `UNEMPLOYMENT` | `EU27_2020` + 14 países UE | Anual |
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_house_price_index()` | `prc_hpi_q` | `HOUSE_PRICE_INDEX` | `EU27_2020` + 14 países UE | Trimestral |
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_interest_rate()` | `ei_mfir_m` | `INTEREST_RATE` | `EU27_2020` + 14 países UE | Mensual |
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_industrial_production()` | `sts_inpr_m` (`PRD`, `C`, `SCA`, `I21`) | `INDUSTRIAL_PRODUCTION` | `EU27_2020` + 14 países UE | Mensual |
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_retail_sales()` | `sts_trtu_m` (`VOL_SLS`, `G47`, `SCA`, `I21`) | `RETAIL_SALES` | `EU27_2020` + 14 países UE | Mensual |
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_exports()` / `get_imports()` | `ext_st_eu27_2020sitc` (`EXP` / `IMP`) | `EXPORTS` / `IMPORTS` | `EU27_2020` (Extra-UE) | Mensual |
| [`EurostatClient`](file:///home/dano/sight/backend/app/clients/eurostat_client.py) | `get_exports_by_country()` / `get_imports_by_country()` / `get_trade_balance_by_country()` | `ext_lt_intertrd` (`MIO_EXP_VAL`, `MIO_IMP_VAL`, `MIO_BAL_VAL`) | `*_BY_COUNTRY` | 14 Estados miembros UE | Anual |
| [`BeaClient`](file:///home/dano/sight/backend/app/clients/bea_client.py) | `get_gdp()` | NIPA `T10106` (`SeriesCode="A191RX"`, Línea 1) | `GDP` | `US` | Trimestral |
| [`BeaClient`](file:///home/dano/sight/backend/app/clients/bea_client.py) | `get_exports()` | NIPA `T10106` (`SeriesCode="A020RX"`) | `EXPORTS` | `US` | Trimestral |
| [`BeaClient`](file:///home/dano/sight/backend/app/clients/bea_client.py) | `get_imports()` | NIPA `T10106` (`SeriesCode="A021RX"`) | `IMPORTS` | `US` | Trimestral |
| [`BlsClient`](file:///home/dano/sight/backend/app/clients/bls_client.py) | `get_cpi()` | `CUUR0000SA0` (paginado en bloques de 10 años, 1947–2026) | `CPI` | `US` | Mensual |
| [`BlsClient`](file:///home/dano/sight/backend/app/clients/bls_client.py) | `get_inflation()` | Variación YoY calculada sobre `CUUR0000SA0` | `INFLATION` | `US` | Mensual |
| [`BlsClient`](file:///home/dano/sight/backend/app/clients/bls_client.py) | `get_unemployment()` | `LNS14000000` | `UNEMPLOYMENT` | `US` | Mensual |
| [`NbsClient`](file:///home/dano/sight/backend/app/clients/nbs_client.py) | `get_cpi()`, `get_gdp()`, `get_unemployment()`, `get_inflation()` | `hgnd`: `A0901`, `A0201`, `A0302`, `A0902` | `CPI`, `GDP`, `UNEMPLOYMENT`, `INFLATION` | `CN` | Anual / Mensual |
