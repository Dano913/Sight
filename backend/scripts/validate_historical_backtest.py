#!/usr/bin/env python3
"""
Backtest histórico independiente para Sight.

Ejecutar desde backend/:
    python scripts/validate_historical_backtest.py

Lee observaciones históricas de app/database/sight.db y los CSV de
data/validation/market. No modifica la base de datos ni el código de producción.

Importante:
- Las señales se recalculan en cada fecha usando solo observaciones <= fecha.
- Los índices de mercado se usan para calcular retornos futuros.
- Los índices de precios (oro/petróleo) representan variación de precio, no retorno total.
- No se usan series de rentabilidad no comparables (p. ej. yield de letras del Tesoro).
- El backtest no elimina el sesgo de revisiones históricas de datos macroeconómicos.
"""
from __future__ import annotations

import csv
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pandas as pd

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
DB_PATH = BACKEND / "app" / "database" / "sight.db"
MARKET_DIR = BACKEND / "data" / "validation" / "market"
OUTPUT_DIR = BACKEND / "data" / "validation" / "backtest"
START = pd.Timestamp("1975-01-01")
END = pd.Timestamp("2015-12-31")
HORIZONS = (3, 6, 12, 24)

# Metadata alineada con IndicatorService. Si se añaden indicadores, revisar aquí.
INDICATOR_META = {
    "GDP": ("annual", "log"),
    "INFLATION": ("monthly", "rate"),
    "UNEMPLOYMENT": ("monthly", "rate"),
    "HOUSE_PRICE_INDEX": ("quarterly", "log"),
    "CPI": ("monthly", "log"),
    "INTEREST_RATE": ("monthly", "rate"),
    "INDUSTRIAL_PRODUCTION": ("monthly", "log"),
    "RETAIL_SALES": ("monthly", "log"),
}
REGION_CANDIDATES = {"US", "USA", "UNITED_STATES", "UNITED STATES"}


def stop(message: str, code: int = 1) -> None:
    print(f"\nERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def find_observation_table(conn: sqlite3.Connection) -> tuple[str, list[str]]:
    tables = [
        row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    ]
    for table in tables:
        columns = [
            row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')
        ]
        lower = {column.lower() for column in columns}
        required = {"region_code", "indicator_code", "source_code", "date", "value"}
        if required.issubset(lower):
            return table, columns
    details = []
    for table in tables:
        cols = [
            row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')
        ]
        details.append(f"{table}: {', '.join(cols)}")
    stop(
        "No encuentro una tabla con region_code, indicator_code, source_code, "
        "date y value. Tablas detectadas:\n  " + "\n  ".join(details)
    )
    raise AssertionError("unreachable")


def read_macro_rows() -> tuple[list[dict[str, Any]], str]:
    if not DB_PATH.exists():
        stop(f"No existe la base de datos: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    try:
        table, columns = find_observation_table(conn)
        by_lower = {column.lower(): column for column in columns}
        fields = [
            by_lower["region_code"], by_lower["indicator_code"],
            by_lower["source_code"], by_lower["date"], by_lower["value"],
        ]
        sql = (
            "SELECT " + ", ".join(f'"{field}"' for field in fields)
            + f' FROM "{table}"'
        )
        rows = conn.execute(sql).fetchall()
        records = []
        for region, indicator, source, raw_date, value in rows:
            if not all(x is not None for x in (region, indicator, source, raw_date, value)):
                continue
            parsed = pd.to_datetime(raw_date, errors="coerce")
            if pd.isna(parsed):
                continue
            records.append({
                "region_code": str(region).upper(),
                "indicator_code": str(indicator).upper(),
                "source_code": str(source).upper(),
                "date": pd.Timestamp(parsed).to_pydatetime(),
                "value": float(value),
            })
        return records, table
    finally:
        conn.close()


def read_market_series() -> dict[str, dict[str, Any]]:
    series: dict[str, dict[str, Any]] = {}
    if not MARKET_DIR.exists():
        stop(f"No existe el directorio de mercados: {MARKET_DIR}")
    for path in sorted(MARKET_DIR.glob("*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                continue
            fields = {field.strip().lower(): field for field in reader.fieldnames}
            required = {"date", "asset", "value", "value_type"}
            if not required.issubset(fields):
                continue
            rows = []
            for row in reader:
                parsed = pd.to_datetime(row[fields["date"]], errors="coerce")
                try:
                    value = float(row[fields["value"]])
                except (TypeError, ValueError):
                    continue
                if pd.isna(parsed):
                    continue
                rows.append({
                    "date": pd.Timestamp(parsed),
                    "asset": str(row[fields["asset"]]).upper(),
                    "value": value,
                    "value_type": str(row[fields["value_type"]]).lower(),
                    "source": row.get(fields.get("source", ""), ""),
                })
        if not rows:
            continue
        frame = pd.DataFrame(rows).sort_values("date")
        for asset, group in frame.groupby("asset"):
            group = group.drop_duplicates("date", keep="last").set_index("date")
            value_type = str(group["value_type"].iloc[0])
            # El yield anualizado no es un índice de retorno: no se compara como si lo fuera.
            if value_type not in {"total_return_index", "price_index"}:
                continue
            series[asset] = {
                "frame": group,
                "value_type": value_type,
                "file": path.name,
            }
    return series


def resolve_enum(enum_class_names: tuple[str, ...], value: str) -> Any:
    """Usa el enum real de Sight si existe; recurre a un objeto compatible si no."""
    try:
        import app.models.enums as enums_module
        for class_name in enum_class_names:
            enum_class = getattr(enums_module, class_name, None)
            if enum_class is None:
                continue
            for member in enum_class:
                if str(getattr(member, "value", "")).lower() == value.lower():
                    return member
                if str(getattr(member, "name", "")).lower() == value.lower():
                    return member
    except (ImportError, TypeError):
        pass
    return SimpleNamespace(value=value)


def namespace_observations(rows: list[dict[str, Any]]) -> list[Any]:
    """Crea objetos con los atributos consumidos por AnalysisService."""
    observations = []
    for row in rows:
        indicator_code = row["indicator_code"]
        frequency, growth = INDICATOR_META.get(
            indicator_code, ("monthly", "rate")
        )
        indicator = SimpleNamespace(
            id=indicator_code,
            code=indicator_code,
            name=indicator_code,
            frequency=resolve_enum(("Frequency",), frequency),
            growth_method=resolve_enum(("GrowthMethod", "GrowthMethodType"), growth),
        )
        region = SimpleNamespace(
            id=row["region_code"], code=row["region_code"], name=row["region_code"]
        )
        source = SimpleNamespace(
            id=row["source_code"], code=row["source_code"], name=row["source_code"]
        )
        observations.append(SimpleNamespace(
            indicator=indicator,
            region=region,
            source=source,
            date=row["date"],
            value=row["value"],
        ))
    return observations


def choose_fixed_sources(rows: list[dict[str, Any]]) -> dict[str, str]:
    """Fija una fuente por indicador usando solo cobertura dentro del periodo evaluado."""
    counts = Counter(
        (r["indicator_code"], r["source_code"])
        for r in rows if START <= pd.Timestamp(r["date"]) <= END
    )
    chosen: dict[str, str] = {}
    for indicator in sorted({r["indicator_code"] for r in rows}):
        options = [
            (count, source)
            for (code, source), count in counts.items()
            if code == indicator
        ]
        if options:
            # Desempate estable. La fuente queda fija para todas las fechas.
            chosen[indicator] = sorted(options, key=lambda item: (-item[0], item[1]))[0][1]
    return chosen


def as_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str, sort_keys=True)


def extract_regime(value: Any) -> str:
    """Intenta extraer una etiqueta sin asumir una única estructura de respuesta."""
    if isinstance(value, dict):
        for key in ("regime", "macro_regime", "classification", "label", "name", "phase"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        for candidate in value.values():
            result = extract_regime(candidate)
            if result != "UNKNOWN":
                return result
    elif isinstance(value, list):
        for candidate in value:
            result = extract_regime(candidate)
            if result != "UNKNOWN":
                return result
    elif isinstance(value, str) and value.strip():
        return value.strip()
    return "UNKNOWN"


def forward_return(market: dict[str, Any], signal_date: pd.Timestamp, months: int) -> float | None:
    frame = market["frame"]
    available = frame.loc[frame.index <= signal_date]
    if available.empty:
        return None
    start_date = available.index[-1]
    target = signal_date + pd.DateOffset(months=months)
    future = frame.loc[frame.index >= target]
    if future.empty:
        return None
    start_value = float(frame.loc[start_date, "value"])
    end_value = float(future.iloc[0]["value"])
    if start_value == 0:
        return None
    return end_value / start_value - 1.0


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    macro_rows, table = read_macro_rows()
    markets = read_market_series()

    print(f"Base: {DB_PATH}")
    print(f"Tabla macro detectada: {table}")
    print(f"Observaciones leídas: {len(macro_rows):,}")
    print(f"Series de mercado comparables: {len(markets)}")

    if not macro_rows:
        stop("La tabla existe, pero no contiene observaciones utilizables.")
    if not markets:
        stop("No se han encontrado índices de mercado comparables en los CSV.")

    # La comparación con estos activos solo tiene sentido para macro de EE. UU.
    us_rows = [r for r in macro_rows if r["region_code"] in REGION_CANDIDATES]
    if not us_rows:
        coverage = Counter(r["region_code"] for r in macro_rows)
        summary = ", ".join(f"{key}={value}" for key, value in coverage.most_common(20))
        stop(
            "No encuentro observaciones macro para EE. UU.; no compararé "
            f"regímenes de otra región con activos estadounidenses. Regiones: {summary}"
        )

    us_rows = [
        r for r in us_rows
        if pd.Timestamp(r["date"]) <= END
    ]
    source_by_indicator = choose_fixed_sources(us_rows)
    us_rows = [
        r for r in us_rows
        if source_by_indicator.get(r["indicator_code"]) == r["source_code"]
    ]

    coverage_rows = []
    by_indicator: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in us_rows:
        by_indicator[row["indicator_code"]].append(row)
    for code, group in sorted(by_indicator.items()):
        dates = sorted(pd.Timestamp(r["date"]) for r in group)
        coverage_rows.append({
            "indicator": code,
            "source": source_by_indicator.get(code, ""),
            "observations": len(group),
            "first_date": dates[0].date().isoformat(),
            "last_date": dates[-1].date().isoformat(),
            "in_backtest_period": sum(START <= d <= END for d in dates),
        })
    pd.DataFrame(coverage_rows).to_csv(OUTPUT_DIR / "macro_coverage.csv", index=False)

    # Fechas mensuales de decisión. En cada iteración solo se pasan datos <= cutoff.
    cutoffs = pd.date_range(START, END, freq="ME")
    snapshots = namespace_observations(us_rows)
    from app.services.analysis.analysis_service import AnalysisService

    signal_rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for number, cutoff in enumerate(cutoffs, start=1):
        visible = [
            obs for obs in snapshots
            if pd.Timestamp(obs.date) <= cutoff
            and pd.Timestamp(obs.date) >= START - pd.DateOffset(years=15)
        ]
        # Exige un mínimo razonable para no etiquetar señales calculadas con
        # unas pocas observaciones como resultados históricos válidos.
        counts = Counter(obs.indicator.code for obs in visible)
        usable_codes = {
            code for code, count in counts.items()
            if count >= 24
        }
        visible = [obs for obs in visible if obs.indicator.code in usable_codes]
        if not visible:
            failures.append({"date": cutoff.date().isoformat(), "error": "Sin indicadores con >=24 observaciones"})
            continue

        try:
            result = AnalysisService.analyze_multiple(visible)
        
            if cutoff.year == 2000 and cutoff.month == 1:
                for code, item in result["indicators"].items():
                    print(f"\n--- {code} ---")
                    print(item.get("economic_interpretation"))
                print("\n--- MACRO REGIME ---")
                print(result["macro_regime"])
        
        
        except Exception as exc:
            failures.append({
                "date": cutoff.date().isoformat(),
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue

        regime = result.get("macro_regime", {})
        if not isinstance(regime, dict):
            regime = {}

        try:
            evidence_count = max(0, int(regime.get("evidence_count", 0) or 0))
        except (TypeError, ValueError, OverflowError):
            evidence_count = 0

        signal_status = (
            "with_macro_evidence"
            if evidence_count > 0
            else "no_cyclical_evidence"
        )
        regime_label = extract_regime(regime)
        scores = result.get("asset_scores", [])
        signal = {
            "date": cutoff.date().isoformat(),
            "region": result.get("region", "US"),
            "indicators_used": ",".join(sorted(usable_codes)),
            "indicator_count": len(usable_codes),
            "evidence_count": evidence_count,
            "signal_status": signal_status,
            "macro_regime": regime_label,
            "macro_regime_json": as_json(regime),
            "macro_factor_scores_json": as_json(result.get("macro_factor_scores", {})),
            "asset_scores_json": as_json(scores),
        }
        signal_rows.append(signal)

        for asset, market in markets.items():
            for horizon in HORIZONS:
                ret = forward_return(market, cutoff, horizon)
                if ret is None:
                    continue
                detail_rows.append({
                    **{k: signal[k] for k in (
                        "date", "region", "indicator_count", "evidence_count",
                        "signal_status", "macro_regime", "macro_regime_json",
                        "macro_factor_scores_json", "asset_scores_json"
                    )},
                    "asset": asset,
                    "market_file": market["file"],
                    "market_value_type": market["value_type"],
                    "horizon_months": horizon,
                    "forward_return": ret,
                })

        if number % 60 == 0:
            print(f"Procesadas {number}/{len(cutoffs)} fechas; señales válidas: {len(signal_rows)}")

    signals_path = OUTPUT_DIR / "signals_by_month.csv"
    details_path = OUTPUT_DIR / "forward_returns.csv"
    failures_path = OUTPUT_DIR / "failed_dates.csv"
    pd.DataFrame(signal_rows).to_csv(signals_path, index=False)
    pd.DataFrame(detail_rows).to_csv(details_path, index=False)
    pd.DataFrame(failures).to_csv(failures_path, index=False)

    if detail_rows:
        details = pd.DataFrame(detail_rows)
        summary = (
            details.groupby(
                ["asset", "market_value_type", "horizon_months", "macro_regime", "signal_status"],
                dropna=False,
            )
            .agg(
                observations=("forward_return", "count"),
                mean_forward_return=("forward_return", "mean"),
                median_forward_return=("forward_return", "median"),
                positive_fraction=("forward_return", lambda s: float((s > 0).mean())),
            )
            .reset_index()
            .sort_values(["asset", "horizon_months", "macro_regime", "signal_status"])
        )
        summary.to_csv(OUTPUT_DIR / "summary_by_regime.csv", index=False)
    else:
        summary = pd.DataFrame()
        summary.to_csv(OUTPUT_DIR / "summary_by_regime.csv", index=False)

    print("\n=== RESULTADO ===")
    print(f"Fechas evaluadas: {len(cutoffs)}")
    print(f"Señales generadas: {len(signal_rows)}")
    print(f"Fechas fallidas: {len(failures)}")
    print(f"Retornos futuros calculados: {len(detail_rows)}")
    print(f"Indicadores usados: {', '.join(sorted(by_indicator)) or 'ninguno'}")
    print(f"Fuentes fijas: {as_json(source_by_indicator)}")
    print(f"\nArchivos creados en: {OUTPUT_DIR}")
    print(f"- {signals_path.name}")
    print(f"- {details_path.name}")
    print(f"- summary_by_regime.csv")
    print(f"- {failures_path.name}")
    print(f"- macro_coverage.csv")
    if failures:
        print("\nPrimeros errores:")
        for failure in failures[:5]:
            print(f"  {failure['date']}: {failure['error']}")
    print(
        "\nLIMITACIÓN: los resultados evitan usar observaciones posteriores a cada fecha, "
        "pero no controlan revisiones/vintages de las estadísticas macroeconómicas. "
        "La selección de una fuente fija por indicador se basa en la cobertura del "
        "periodo evaluado, no en rentabilidades futuras."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
