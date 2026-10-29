from backend.app.services.catalog.observation_service import ObservationService
from backend.app.services.analysis.macro.analysis_service import AnalysisService
from backend.app.services.analysis.macro.macro_regime_service import MacroRegimeService


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main() -> None:

    section("ANÁLISIS MACROECONÓMICO COMPLETO")

    # ==========================================================
    # 1. OBTENER OBSERVACIONES
    # ==========================================================

    observations = ObservationService.get_observations(
        indicator_code="GDP",
        region_code="DE",
    )

    if not observations:
        raise RuntimeError(
            "No se obtuvieron observaciones para GDP / DE"
        )

    section("OBSERVACIONES")

    print("Número de observaciones:", len(observations))
    print(
        "Periodo:",
        observations[0].date,
        "→",
        observations[-1].date,
    )
    print(
        "Indicador:",
        observations[0].indicator.code,
    )
    print(
        "Región:",
        observations[0].region.code,
    )
    print(
        "Fuente:",
        observations[0].source.code,
    )
    print(
        "Frecuencia:",
        observations[0].indicator.frequency,
    )

    # ==========================================================
    # 2. ANÁLISIS COMPLETO
    # ==========================================================

    section("ANÁLISIS")

    result = AnalysisService.analyze(
        observations=observations,
    )

    if not isinstance(result, dict):
        raise TypeError(
            "AnalysisService.analyze() debe devolver un dict"
        )

    print("✓ AnalysisService ejecutado correctamente")

    # ==========================================================
    # 3. DATOS ORIGINALES
    # ==========================================================

    data = result["data"]

    section("DATOS ORIGINALES")

    print("Frecuencia:", data["frequency"])
    print("Observaciones:", data["count"])

    print("\nPrimeras observaciones:")

    for observation in data["observations"][:5]:
        print(observation)

    print("\nÚltimas observaciones:")

    for observation in data["observations"][-5:]:
        print(observation)

    # ==========================================================
    # 4. FEATURES
    # ==========================================================

    features = result["features"]

    section("FEATURES")

    if not isinstance(features, list):
        raise TypeError(
            "result['features'] debe ser una lista"
        )

    print("Número de registros:", len(features))

    if features:
        feature_columns = [
            column
            for column in features[0]
            if column != "date"
        ]

        print(
            "Número de features:",
            len(feature_columns),
        )

        print("\nFeatures:")

        for column in feature_columns:
            print(" -", column)

        print("\nÚltimo registro:")
        print(features[-1])

    # ==========================================================
    # 5. SEÑALES
    # ==========================================================

    signals = result["signals"]

    section("SEÑALES")

    if not isinstance(signals, list):
        raise TypeError(
            "result['signals'] debe ser una lista"
        )

    print("Número de registros:", len(signals))

    if signals:
        signal_columns = [
            column
            for column in signals[0]
            if column != "date"
        ]

        print(
            "Número de señales:",
            len(signal_columns),
        )

        print("\nSeñales:")

        for column in signal_columns:
            print(" -", column)

        print("\nÚltimo registro:")
        print(signals[-1])

    # ==========================================================
    # 6. ANÁLISIS DE CICLOS
    # ==========================================================

    cycles = result["cycles"]

    section("ANÁLISIS DE CICLOS")

    print(
        "Observaciones:",
        cycles["observations"],
    )

    print(
        "Periodo:",
        cycles["start_date"],
        "→",
        cycles["end_date"],
    )

    robust_cycles = cycles.get(
        "robust_cycles",
        [],
    )

    print(
        "Ciclos detectados:",
        len(robust_cycles),
    )

    if robust_cycles:

        print("\nCiclos robustos:")

        for index, cycle in enumerate(
            robust_cycles,
            start=1,
        ):

            print(
                f"\n{index}. "
                f"{cycle['period_years']:.2f} años"
            )

            print(
                "   Score:",
                cycle["score"],
            )

            print(
                "   Confianza:",
                cycle["confidence"],
            )

            print(
                "   Métodos:",
                cycle["method_count"],
                "/ 3",
            )

            print(
                "   Cobertura:",
                f"{cycle['method_coverage'] * 100:.0f}%",
            )

            print(
                "   Ciclos observables:",
                cycle["cycles_observable"],
            )

    # ==========================================================
    # 7. INTERPRETACIÓN DE CICLOS
    # ==========================================================

    cycle_interpretation = result[
        "cycle_interpretation"
    ]

    section("INTERPRETACIÓN DE CICLOS")

    print(
        "Ciclo detectado:",
        cycle_interpretation["cycle_detected"],
    )

    overall = cycle_interpretation["overall"]

    print("\nEvaluación global:")

    print(
        " - Assessment:",
        overall["assessment"],
    )

    print(
        " - Ciclos detectados:",
        overall["cycles_detected"],
    )

    print(
        " - Mejor score:",
        overall.get("best_score"),
    )

    print(
        " - Mejor confianza:",
        overall.get("best_confidence"),
    )

    best_cycle = cycle_interpretation.get(
        "best_cycle"
    )

    if best_cycle:

        print("\nMejor ciclo:")

        print(
            " - Periodo:",
            best_cycle["period_years"],
            "años",
        )

        print(
            " - Score:",
            best_cycle["score"],
        )

        print(
            " - Confianza:",
            best_cycle["confidence"],
        )

        print(
            " - Nivel de evidencia:",
            best_cycle["evidence_level"],
        )

        print(
            " - Métodos:",
            best_cycle["method_count"],
        )

        print(
            " - Ciclos observables:",
            best_cycle["cycles_observable"],
        )

        print(
            " - Calidad de muestra:",
            best_cycle["sample_quality"],
        )

        print(
            " - Descripción:",
            best_cycle["description"],
        )

    print("\nAdvertencia:")

    print(
        cycle_interpretation.get(
            "caution",
            "No disponible.",
        )
    )

    # ==========================================================
    # 8. INTERPRETACIÓN ECONÓMICA
    # ==========================================================

    economic = result[
        "economic_interpretation"
    ]

    section("INTERPRETACIÓN ECONÓMICA")

    print("Indicador:", economic["indicator"])
    print("Región:", economic["region"])
    print("Fecha:", economic["date"])
    print("Régimen:", economic["regime"])

    # ----------------------------------------------------------
    # GROWTH
    # ----------------------------------------------------------

    growth = economic["growth"]

    print("\nGROWTH")

    print(" - Estado:", growth["state"])
    print(
        " - Variación:",
        growth["percentage_change"],
    )
    print(
        " - Crecimiento positivo:",
        growth["positive"],
    )
    print(
        " - Crecimiento negativo:",
        growth["negative"],
    )
    print(
        " - Acelerando:",
        growth["accelerating"],
    )

    # ----------------------------------------------------------
    # TREND
    # ----------------------------------------------------------

    trend = economic["trend"]

    print("\nTREND")

    print(" - Estado:", trend["state"])
    print(" - Bullish:", trend["bullish"])
    print(" - Bearish:", trend["bearish"])
    print(" - Reversal:", trend["reversal"])
    print(" - Slope corto:", trend["short_slope"])
    print(" - Slope medio:", trend["medium_slope"])
    print(" - Slope largo:", trend["long_slope"])
    print(" - Acceleration:", trend["acceleration"])
    print(" - Trend change:", trend["trend_change"])

    # ----------------------------------------------------------
    # MOMENTUM
    # ----------------------------------------------------------

    momentum = economic["momentum"]

    print("\nMOMENTUM")

    print(" - Estado:", momentum["state"])
    print(" - Valor:", momentum["value"])

    # ----------------------------------------------------------
    # VOLATILITY
    # ----------------------------------------------------------

    volatility = economic["volatility"]

    print("\nVOLATILITY")

    print(" - Estado:", volatility["state"])
    print(" - Alta:", volatility["high"])
    print(
        " - Aumentando:",
        volatility["increasing"],
    )
    print(
        " - Volatilidad:",
        volatility["volatility"],
    )
    print(
        " - Volatility z-score:",
        volatility["volatility_zscore"],
    )
    print(
        " - Volatility change:",
        volatility["volatility_change"],
    )

    # ----------------------------------------------------------
    # POSITION
    # ----------------------------------------------------------

    position = economic["position"]

    print("\nPOSITION")

    print(" - Estado:", position["state"])
    print(
        " - Cerca del máximo:",
        position["near_high"],
    )
    print(
        " - Cerca del mínimo:",
        position["near_low"],
    )
    print(
        " - Z-score:",
        position["zscore"],
    )
    print(
        " - Percentile:",
        position["percentile"],
    )
    print(
        " - Distancia de la media:",
        position["distance_from_mean"],
    )
    print(
        " - Distancia del máximo:",
        position["distance_from_max"],
    )
    print(
        " - Distancia del mínimo:",
        position["distance_from_min"],
    )
    print(
        " - Drawdown:",
        position["drawdown"],
    )

    # ----------------------------------------------------------
    # TRANSITION
    # ----------------------------------------------------------

    transition = economic["transition"]

    print("\nTRANSITION")

    print(
        " - Detectada:",
        transition["detected"],
    )
    print(
        " - Estado:",
        transition["state"],
    )
    print(
        " - Tipo:",
        transition.get("type"),
    )
    print(
        " - Dirección:",
        transition["direction"],
    )
    print(
        " - Score:",
        transition["score"],
    )
    print(
        " - Confianza:",
        transition["confidence"],
    )
    print(
        " - Razones:",
        transition["reasons"],
    )

    # ----------------------------------------------------------
    # ASSESSMENT
    # ----------------------------------------------------------

    assessment = economic["assessment"]

    print("\nASSESSMENT")

    print(assessment)

    # ----------------------------------------------------------
    # HISTORIAL
    # ----------------------------------------------------------

    history = economic["history"]

    print("\nHISTORIAL")

    print(
        " - Observaciones:",
        history["observations"],
    )

    print(
        " - Inicio:",
        history["start"],
    )

    print(
        " - Fin:",
        history["end"],
    )

    # ==========================================================
    # 9. INTERPRETACIÓN DE INVERSIÓN
    # ==========================================================

    investment = result[
        "investment_interpretation"
    ]

    section("INTERPRETACIÓN DE INVERSIÓN")

    print("Indicador:", investment["indicator"])
    print("Región:", investment["region"])
    print("Fecha:", investment["date"])
    print("Régimen:", investment["regime"])

    # ----------------------------------------------------------
    # ENVIRONMENT
    # ----------------------------------------------------------

    environment = investment["environment"]

    print("\nENVIRONMENT")

    print(" - Estado:", environment["state"])
    print(" - Score:", environment["score"])
    print(" - Razones:", environment["reasons"])

    # ----------------------------------------------------------
    # RISK
    # ----------------------------------------------------------

    risk = investment["risk"]

    print("\nRISK")

    print(" - Estado:", risk["state"])
    print(" - Score:", risk["score"])
    print(" - Razones:", risk["reasons"])

    # ----------------------------------------------------------
    # OPPORTUNITY
    # ----------------------------------------------------------

    opportunity = investment["opportunity"]

    print("\nOPPORTUNITY")

    print(
        " - Estado:",
        opportunity["state"],
    )

    print(
        " - Score:",
        opportunity["score"],
    )

    print(
        " - Razones:",
        opportunity["reasons"],
    )

    # ----------------------------------------------------------
    # SIGNALS
    # ----------------------------------------------------------

    investment_signals = investment["signals"]

    print("\nSIGNALS")

    for signal, value in investment_signals.items():
        print(
            f" - {signal}: {value}"
        )

    # ----------------------------------------------------------
    # CONFIDENCE
    # ----------------------------------------------------------

    confidence = investment["confidence"]

    print("\nCONFIDENCE")

    print(
        " - Estado:",
        confidence["state"],
    )

    print(
        " - Score:",
        confidence["score"],
    )

    print(
        " - Razones:",
        confidence["reasons"],
    )

    # ==========================================================
    # 10. RÉGIMEN MACROECONÓMICO
    # ==========================================================

    interpretations = {
        economic["indicator"]: economic,
    }

    macro_regime = MacroRegimeService.classify(
        interpretations=interpretations,
    )

    section("RÉGIMEN MACROECONÓMICO")

    print(
        "Régimen:",
        macro_regime["regime"],
    )

    print(
        "Confianza:",
        macro_regime["confidence"],
    )

    print(
        "Score:",
        macro_regime["score"],
    )

    print("\nScores:")

    for regime, score in macro_regime["scores"].items():
        print(
            f" - {regime}: {score}"
        )

    print("\nIndicadores utilizados:")

    for indicator in macro_regime["indicators_used"]:
        print(
            " -",
            indicator,
        )

    print("\nEvidencia:")

    if macro_regime["evidence"]:

        for item in macro_regime["evidence"]:
            print(
                f" - [{item['indicator']}] "
                f"{item['reason']} "
                f"(peso={item['weight']})"
            )

    else:
        print(" - Sin evidencia suficiente.")

    # ==========================================================
    # 11. VALIDACIONES FINALES
    # ==========================================================

    section("VALIDACIONES")

    required_result_keys = {
        "data",
        "features",
        "signals",
        "cycles",
        "cycle_interpretation",
        "economic_interpretation",
        "investment_interpretation",
    }

    missing_keys = (
        required_result_keys
        - set(result.keys())
    )

    if missing_keys:
        raise AssertionError(
            "Faltan claves en AnalysisService: "
            f"{sorted(missing_keys)}"
        )

    assert len(observations) > 0
    assert len(features) > 0
    assert len(signals) > 0

    assert economic["indicator"] == "GDP"
    assert economic["region"] == "DE"

    assert isinstance(
        economic["regime"],
        str,
    )

    assert isinstance(
        economic["transition"],
        dict,
    )

    assert isinstance(
        investment["environment"],
        dict,
    )

    assert isinstance(
        investment["risk"],
        dict,
    )

    assert isinstance(
        investment["opportunity"],
        dict,
    )

    assert isinstance(
        macro_regime,
        dict,
    )

    print("✓ Observaciones válidas")
    print("✓ Features válidas")
    print("✓ Señales válidas")
    print("✓ Ciclos válidos")
    print("✓ Interpretación económica válida")
    print("✓ Transition válida")
    print("✓ Interpretación de inversión válida")
    print("✓ Régimen macroeconómico válido")

    # ==========================================================
    # 12. RESUMEN FINAL
    # ==========================================================

    section("ANÁLISIS COMPLETADO")

    print("✓ Observaciones:", len(observations))
    print("✓ Features:", len(features))
    print("✓ Señales:", len(signals))
    print("✓ Ciclos robustos:", len(robust_cycles))
    print(
        "✓ Ciclo:",
        cycle_interpretation["cycle_detected"],
    )
    print(
        "✓ Régimen económico:",
        economic["regime"],
    )
    print(
        "✓ Transición:",
        transition["type"],
    )
    print(
        "✓ Régimen macroeconómico:",
        macro_regime["regime"],
    )
    print(
        "✓ Confianza régimen macro:",
        macro_regime["confidence"],
    )
    print(
        "✓ Entorno de inversión:",
        investment["environment"]["state"],
    )
    print(
        "✓ Riesgo de inversión:",
        investment["risk"]["state"],
    )
    print(
        "✓ Oportunidad de inversión:",
        investment["opportunity"]["state"],
    )
    print(
        "✓ Confianza de interpretación:",
        investment["confidence"]["state"],
    )

    print("=" * 70)


if __name__ == "__main__":
    main()