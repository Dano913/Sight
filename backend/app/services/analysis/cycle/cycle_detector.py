from __future__ import annotations

import numpy as np


class CycleDetector:
    """
    Detecta y puntúa ciclos a partir de periodicidades
    obtenidas mediante distintos métodos.

    Responsabilidades:
    - Filtrar periodicidades.
    - Agrupar periodicidades similares.
    - Puntuar clusters.
    - Detectar ciclos robustos.
    """

    MAX_PERIOD_FRACTION = 0.50
    PERIOD_TOLERANCE = 0.20
    TOP_PERIODS_PER_METHOD = 8

    @classmethod
    def get_valid_periods(
        cls,
        periodogram,
        sample_size: int,
        observations_per_year: int,
        top_n: int | None = None,
    ):
        """
        Filtra periodicidades poco útiles.

        El periodo está expresado en años, por lo que el tamaño
        de la muestra debe convertirse previamente a años.
        """

        if observations_per_year <= 0:
            raise ValueError(
                "observations_per_year debe ser mayor que 0."
            )

        if top_n is None:
            top_n = cls.TOP_PERIODS_PER_METHOD

        sample_duration_years = (
            sample_size / observations_per_year
        )

        max_period = (
            sample_duration_years
            * cls.MAX_PERIOD_FRACTION
        )

        valid = [
            item
            for item in periodogram
            if (
                item["period_years"] >= 2.0
                and item["period_years"] <= max_period
            )
        ]

        valid.sort(
            key=lambda item: item["power"],
            reverse=True,
        )

        return valid[:top_n]

    @classmethod
    def periods_are_close(
        cls,
        period_a: float,
        period_b: float,
    ) -> bool:
        """
        Determina si dos periodicidades probablemente
        representan el mismo ciclo.

        Distancia relativa:

            |A-B| / media(A,B)
        """

        mean_period = (
            period_a + period_b
        ) / 2.0

        if mean_period <= 0:
            return False

        distance = (
            abs(period_a - period_b)
            / mean_period
        )

        return distance <= cls.PERIOD_TOLERANCE

    @classmethod
    def cluster_periods(
        cls,
        method_results: dict[str, list],
    ):
        """
        Agrupa periodicidades próximas procedentes
        de distintos métodos.
        """

        candidates = []

        for method_name, periods in method_results.items():
            for item in periods:
                candidates.append(
                    {
                        "method": method_name,
                        "period": item["period_years"],
                        "power": item["power"],
                        "relative_power": item["relative_power"],
                    }
                )

        candidates.sort(
            key=lambda item: item["period"]
        )

        clusters = []

        for candidate in candidates:
            placed = False

            for cluster in clusters:
                cluster_period = float(
                    np.median(
                        [
                            item["period"]
                            for item in cluster
                        ]
                    )
                )

                if cls.periods_are_close(
                    candidate["period"],
                    cluster_period,
                ):
                    cluster.append(candidate)
                    placed = True
                    break

            if not placed:
                clusters.append([candidate])

        return clusters

    @staticmethod
    def score_cluster(
        cluster,
        sample_size: int,
        observations_per_year: int,
        method_count: int = 3,
    ):
        """
        Calcula una puntuación de evidencia.

        Componentes:
        - Consistencia entre métodos.
        - Potencia relativa.
        - Número de ciclos observables.
        - Dispersión del periodo.
        """

        if observations_per_year <= 0:
            raise ValueError(
                "observations_per_year debe ser mayor que 0."
            )

        if method_count <= 0:
            raise ValueError(
                "method_count debe ser mayor que 0."
            )

        if not cluster:
            raise ValueError(
                "El cluster no puede estar vacío."
            )

        periods = [
            item["period"]
            for item in cluster
        ]

        representative_period = float(
            np.median(periods)
        )

        methods = {
            item["method"]
            for item in cluster
        }

        method_coverage = (
            len(methods)
            / method_count
        )

        # Cada método aporta como máximo una vez a la
        # potencia del cluster. Si un mismo método tiene
        # varios bins cercanos, solo se utiliza su mayor
        # potencia relativa.
        method_powers = {}

        for item in cluster:
            method = item["method"]
            relative_power = item["relative_power"]

            if (
                method not in method_powers
                or relative_power > method_powers[method]
            ):
                method_powers[method] = relative_power

        power_score = float(
            np.mean(
                list(method_powers.values())
            )
        )

        sample_duration_years = (
            sample_size
            / observations_per_year
        )

        cycles_observable = (
            sample_duration_years
            / representative_period
        )

        if cycles_observable >= 4:
            cycle_score = 1.0
        elif cycles_observable >= 3:
            cycle_score = 0.85
        elif cycles_observable >= 2:
            cycle_score = 0.65
        elif cycles_observable >= 1.5:
            cycle_score = 0.40
        else:
            cycle_score = 0.15

        if len(periods) > 1:
            dispersion = (
                np.std(periods)
                / np.mean(periods)
            )

            consistency_score = max(
                0.0,
                1.0 - dispersion * 5.0,
            )
        else:
            consistency_score = 0.25

        score = (
            0.40 * method_coverage
            + 0.25 * power_score
            + 0.20 * cycle_score
            + 0.15 * consistency_score
        )

        score *= 100.0

        if (
            method_coverage >= 0.66
            and cycles_observable >= 2.5
            and score >= 55
        ):
            confidence = "ALTA"
        elif (
            method_coverage >= 0.66
            and cycles_observable >= 2
        ):
            confidence = "MEDIA"
        else:
            confidence = "BAJA"

        return {
            "period_years": representative_period,
            "score": round(
                float(score),
                2,
            ),
            "confidence": confidence,
            "methods": sorted(methods),
            "method_count": len(methods),
            "method_coverage": round(
                method_coverage,
                3,
            ),
            "cycles_observable": round(
                cycles_observable,
                2,
            ),
            "period_dispersion": (
                round(
                    float(
                        np.std(periods)
                        / np.mean(periods)
                    ),
                    4,
                )
                if len(periods) > 1
                else 0.0
            ),
            "evidence": [
                {
                    "method": item["method"],
                    "period_years": round(
                        float(item["period"]),
                        3,
                    ),
                    "power": round(
                        float(item["power"]),
                        6,
                    ),
                    "relative_power": round(
                        float(item["relative_power"]),
                        6,
                    ),
                }
                for item in cluster
            ],
        }

    @classmethod
    def detect_robust_cycles(
        cls,
        method_results: dict[str, list],
        sample_size: int,
        observations_per_year: int,
    ):
        """
        Combina los resultados de los métodos y
        genera ciclos consensuados.
        """

        clusters = cls.cluster_periods(
            method_results
        )

        detected_cycles = [
            cls.score_cluster(
                cluster,
                sample_size,
                observations_per_year,
            )
            for cluster in clusters
        ]

        detected_cycles.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return detected_cycles