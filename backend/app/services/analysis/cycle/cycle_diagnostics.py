from __future__ import annotations

from typing import Any


class CycleDiagnostics:
    """
    Presenta los resultados del análisis de ciclos
    en formato legible para consola.
    """

    @staticmethod
    def print(
        result: dict[str, Any],
    ) -> None:

        print()

        print("=" * 64)
        print("DETECTOR ROBUSTO DE CICLOS")
        print("=" * 64)

        print(
            f"Periodo: "
            f"{result['start_date']} → "
            f"{result['end_date']}"
        )

        print(
            f"Observaciones: "
            f"{result['observations']}"
        )

        observations_per_year = (
            result.get(
                "observations_per_year"
            )
        )

        if observations_per_year == 1:
            frequency_label = "anual"
        elif observations_per_year == 4:
            frequency_label = "trimestral"
        elif observations_per_year == 12:
            frequency_label = "mensual"
        else:
            frequency_label = (
                f"{observations_per_year} "
                "observaciones/año"
            )

        if observations_per_year is not None:
            print(
                f"Frecuencia: {frequency_label}"
            )

        print()

        print("CICLOS DETECTADOS POR CONSENSO")
        print("-" * 64)

        cycles = result.get(
            "robust_cycles",
            [],
        )

        if not cycles:
            print(
                "No se han encontrado ciclos "
                "con evidencia suficiente."
            )

        else:
            for index, cycle in enumerate(
                cycles,
                start=1,
            ):
                print(
                    f"{index}. "
                    f"~{cycle['period_years']:.2f} años"
                )

                print(
                    f"   Score: "
                    f"{cycle['score']:.1f}/100"
                )

                print(
                    f"   Confianza: "
                    f"{cycle['confidence']}"
                )

                print(
                    f"   Métodos: "
                    f"{cycle['method_count']}/3"
                )

                print(
                    f"   Cobertura: "
                    f"{cycle['method_coverage'] * 100:.0f}%"
                )

                print(
                    f"   Ciclos observables: "
                    f"{cycle['cycles_observable']:.2f}"
                )

                print(
                    f"   Dispersión: "
                    f"{cycle['period_dispersion']:.3f}"
                )

                print(
                    "   Evidencia espectral:"
                )

                for evidence in cycle["evidence"]:
                    print(
                        f"      "
                        f"{evidence['method']}: "
                        f"{evidence['period_years']:.2f} años"
                        f" | potencia relativa: "
                        f"{evidence['relative_power']:.4f}"
                    )

                print()

        print("=" * 64)
        print("PERIODICIDADES POR MÉTODO")
        print("=" * 64)

        methods = [
            ("growth", "CRECIMIENTO"),
            ("linear_detrend", "TENDENCIA LINEAL"),
            ("hp", "HODRICK-PRESCOTT"),
        ]

        for key, label in methods:

            print()
            print(label)
            print("-" * 64)

            periods = result[key]["dominant_periods"]

            for item in periods:
                print(
                    f"{item['period_years']:>7.2f} años"
                    f" | potencia: "
                    f"{item['power']:.6f}"
                    f" | relativa: "
                    f"{item['relative_power']:.4f}"
                )

        print()

        print("=" * 64)
        print("INTERPRETACIÓN")
        print("=" * 64)

        if cycles:
            best = cycles[0]

            print(
                f"El ciclo con mayor evidencia "
                f"es aproximadamente de "
                f"{best['period_years']:.1f} años."
            )

            print(
                f"Ha sido detectado por "
                f"{best['method_count']} de 3 métodos."
            )

            if best["cycles_observable"] < 2:
                print(
                    "ADVERTENCIA: hay menos de "
                    "2 ciclos completos observables."
                )

            elif best["cycles_observable"] < 3:
                print(
                    "PRECAUCIÓN: hay menos de "
                    "3 ciclos completos observables."
                )

            else:
                print(
                    "La muestra permite observar "
                    "varios ciclos completos."
                )

        else:
            print(
                "No existe evidencia suficiente "
                "para identificar un ciclo robusto."
            )

        print()

        print(
            "NOTA: este detector identifica "
            "periodicidades estadísticas."
        )

        print(
            "No demuestra que exista un ciclo "
            "económico causal o estable."
        )

        print("=" * 64)