from collections import defaultdict

from app.services.analysis.cycle.cycle_analysis_service import (
    CycleAnalysisService,
)

from app.services.catalog.observation_service import (
    ObservationService
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

COUNTRIES = [
    "DE",
    "FR",
    "IT",
    "ES",
    "NL",
    "PL",
    "BE",
    "SE",
    "AT",
    "IE",
    "DK",
    "FI",
    "CZ",
    "PT",
]

INDICATOR = "GDP"

TOP_CYCLES_PER_COUNTRY = 7


# ============================================================
# UTILIDADES
# ============================================================

def print_country_result(country, result):

    print()
    print("=" * 70)
    print(f"PAÍS: {country}")
    print("=" * 70)

    print(
        f"Periodo: "
        f"{result['start_date']} → "
        f"{result['end_date']}"
    )

    print(
        f"Observaciones: "
        f"{result['observations']}"
    )

    # ========================================================
    # IMPORTANTE
    # ========================================================
    #
    # CycleAnalysisService devuelve:
    #
    #     "robust_cycles"
    #
    # NO:
    #
    #     "cycles"
    #

    cycles = result.get(
        "robust_cycles",
        []
    )

    if not cycles:

        print(
            "No se detectaron ciclos."
        )

        return

    print()
    print(
        "CICLOS DETECTADOS"
    )

    for i, cycle in enumerate(
        cycles,
        start=1,
    ):

        print(
            f"{i:2}. "
            f"~{cycle['period_years']:.2f} años | "
            f"Score: {cycle['score']:.1f} | "
            f"Confianza: {cycle['confidence']} | "
            f"Métodos: {cycle['method_count']}/3"
        )


# ============================================================
# ANÁLISIS POR PAÍS
# ============================================================

def collect_country_cycles():

    all_results = {}

    all_cycles = []

    print()
    print("=" * 70)
    print(
        "ANÁLISIS EUROPEO DE CICLOS DEL PIB"
    )
    print("=" * 70)

    print(
        f"Países analizados: "
        f"{len(COUNTRIES)}"
    )

    print(
        f"Indicador: "
        f"{INDICATOR}"
    )

    print()

    for index, country in enumerate(
        COUNTRIES,
        start=1,
    ):

        print()

        print(
            f"[{index}/{len(COUNTRIES)}] "
            f"Analizando {country}..."
        )

        try:

            observations = (
                ObservationService
                .get_observations(
                    indicator_code=INDICATOR,
                    region_code=country,
                )
            )

            if not observations:

                print(
                    f"[{country}] "
                    f"Sin observaciones."
                )

                continue

            result = (
                CycleAnalysisService
                .analyze(
                    observations,
                    top_n=TOP_CYCLES_PER_COUNTRY,
                )
            )

            all_results[country] = result

            print_country_result(
                country,
                result,
            )

            # ==================================================
            # AQUÍ ESTABA EL BUG
            # ==================================================

            cycles = result.get(
                "robust_cycles",
                []
            )

            for cycle in cycles:

                all_cycles.append(
                    {
                        "country": country,

                        "period": (
                            cycle[
                                "period_years"
                            ]
                        ),

                        "score": (
                            cycle[
                                "score"
                            ]
                        ),

                        "confidence": (
                            cycle[
                                "confidence"
                            ]
                        ),

                        "method_count": (
                            cycle[
                                "method_count"
                            ]
                        ),

                        "method_coverage": (
                            cycle[
                                "method_coverage"
                            ]
                        ),

                        "cycles_observable": (
                            cycle[
                                "cycles_observable"
                            ]
                        ),
                    }
                )

        except Exception as exc:

            print()

            print(
                f"[ERROR {country}] "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

    return (
        all_results,
        all_cycles,
    )


# ============================================================
# AGRUPACIÓN EUROPEA
# ============================================================

def build_european_ranking(
    all_cycles
):

    if not all_cycles:
        return []

    sorted_cycles = sorted(
        all_cycles,
        key=lambda x: x["period"],
    )

    clusters = []

    tolerance = 1.0

    for cycle in sorted_cycles:

        period = cycle["period"]

        assigned = False

        for cluster in clusters:

            current_mean = (
                sum(
                    item["period"]
                    for item in cluster
                )
                / len(cluster)
            )

            if abs(
                period - current_mean
            ) <= tolerance:

                cluster.append(
                    cycle
                )

                assigned = True

                break

        if not assigned:

            clusters.append(
                [cycle]
            )

    ranking = []

    for cluster in clusters:

        periods = [
            item["period"]
            for item in cluster
        ]

        scores = [
            item["score"]
            for item in cluster
        ]

        countries = sorted(
            {
                item["country"]
                for item in cluster
            }
        )

        mean_period = (
            sum(periods)
            / len(periods)
        )

        mean_score = (
            sum(scores)
            / len(scores)
        )

        if len(periods) > 1:

            variance = sum(
                (
                    period
                    - mean_period
                ) ** 2

                for period in periods

            ) / len(periods)

            dispersion = (
                variance ** 0.5
            )

        else:

            dispersion = 0.0

        country_count = len(
            countries
        )

        coverage = (
            country_count
            / len(COUNTRIES)
        )

        # ====================================================
        # SCORE EUROPEO
        # ====================================================

        country_score = (
            coverage * 50.0
        )

        quality_score = (
            min(
                mean_score,
                100.0
            )
            / 100.0
        ) * 30.0

        coherence_score = max(
            0.0,
            20.0 * (
                1.0
                - min(
                    dispersion
                    / tolerance,
                    1.0,
                )
            ),
        )

        european_score = (
            country_score
            + quality_score
            + coherence_score
        )

        # ====================================================
        # CONFIANZA
        # ====================================================

        if country_count >= 10:

            confidence = "MUY ALTA"

        elif country_count >= 7:

            confidence = "ALTA"

        elif country_count >= 4:

            confidence = "MEDIA"

        else:

            confidence = "BAJA"

        ranking.append(
            {
                "period_years":
                    mean_period,

                "countries":
                    countries,

                "country_count":
                    country_count,

                "coverage":
                    coverage,

                "mean_score":
                    mean_score,

                "dispersion":
                    dispersion,

                "european_score":
                    european_score,

                "confidence":
                    confidence,

                "observations":
                    len(cluster),
            }
        )

    ranking.sort(
        key=lambda x:
            x["european_score"],
        reverse=True,
    )

    return ranking


# ============================================================
# RANKING
# ============================================================

def print_european_ranking(
    ranking
):

    print()
    print()
    print("=" * 70)
    print(
        "RANKING EUROPEO DE CICLOS DEL PIB"
    )
    print("=" * 70)

    if not ranking:

        print(
            "No se encontraron ciclos suficientes."
        )

        return

    for index, cycle in enumerate(
        ranking,
        start=1,
    ):

        print()

        print(
            f"{index}. "
            f"~{cycle['period_years']:.2f} AÑOS"
        )

        print(
            f"   Score europeo : "
            f"{cycle['european_score']:.1f}/100"
        )

        print(
            f"   Confianza     : "
            f"{cycle['confidence']}"
        )

        print(
            f"   Países        : "
            f"{cycle['country_count']}/"
            f"{len(COUNTRIES)} "
            f"("
            f"{cycle['coverage'] * 100:.0f}%"
            f")"
        )

        print(
            f"   Score medio   : "
            f"{cycle['mean_score']:.1f}"
        )

        print(
            f"   Dispersión    : "
            f"{cycle['dispersion']:.3f} años"
        )

        print(
            "   Países        : "
            + ", ".join(
                cycle["countries"]
            )
        )


# ============================================================
# TABLA
# ============================================================

def print_summary_table(
    ranking
):

    print()
    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)

    print(
        f"{'#':<4}"
        f"{'Ciclo':<12}"
        f"{'Países':<10}"
        f"{'Cobertura':<12}"
        f"{'Score':<10}"
        f"{'Disp.':<10}"
        f"{'Confianza'}"
    )

    print("-" * 70)

    for index, cycle in enumerate(
        ranking,
        start=1,
    ):

        print(
            f"{index:<4}"
            f"{cycle['period_years']:<12.2f}"
            f"{cycle['country_count']:<10}"
            f"{cycle['coverage'] * 100:<12.0f}"
            f"{cycle['european_score']:<10.1f}"
            f"{cycle['dispersion']:<10.2f}"
            f"{cycle['confidence']}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    (
        all_results,
        all_cycles,
    ) = collect_country_cycles()

    print()

    print(
        f"Países con análisis válido: "
        f"{len(all_results)}/"
        f"{len(COUNTRIES)}"
    )

    print(
        f"Ciclos individuales recogidos: "
        f"{len(all_cycles)}"
    )

    # ========================================================
    # CONSENSO EUROPEO
    # ========================================================

    ranking = (
        build_european_ranking(
            all_cycles
        )
    )

    print_european_ranking(
        ranking
    )

    print_summary_table(
        ranking
    )

    # ========================================================
    # INTERPRETACIÓN
    # ========================================================

    print()
    print()
    print("=" * 70)
    print("INTERPRETACIÓN")
    print("=" * 70)

    if ranking:

        best = ranking[0]

        print(
            f"""
El ciclo con mayor consenso europeo es de
aproximadamente {best['period_years']:.2f} años.

Ha sido encontrado en
{best['country_count']} de {len(COUNTRIES)} países.

Score europeo:
{best['european_score']:.1f}/100

Dispersión:
{best['dispersion']:.2f} años

Países:
{", ".join(best['countries'])}
"""
        )

    else:

        print(
            "No se ha encontrado ningún "
            "consenso europeo."
        )

    print(
        """
IMPORTANTE:

Este análisis identifica periodicidades
estadísticas compartidas entre países.

No demuestra por sí solo la existencia
de un ciclo económico causal, estable
o predictivo.

La siguiente fase debería comprobar:

- estabilidad temporal;
- significación estadística;
- sensibilidad a los países incluidos;
- sensibilidad al método;
- y capacidad predictiva fuera de muestra.
"""
    )


if __name__ == "__main__":
    main()