from __future__ import annotations

from typing import Any

from .cycle_diagnostics import CycleDiagnostics
from .cycle_detector import CycleDetector
from .cycle_preprocessor import CyclePreprocessor
from .cycle_signal_analyzer import CycleSignalAnalyzer


class CycleAnalysisService:
    """
    Orquesta el análisis de ciclos macroeconómicos.

    No contiene la lógica matemática de cada etapa.
    """

    @staticmethod
    def analyze(
        observations: list[Any],
        top_n: int = 5,
        hp_lambda: float | None = None,
    ) -> dict[str, Any]:
        (
            dates,
            values,
            observations_per_year,
            use_log,
        ) = CyclePreprocessor.prepare_series(
            observations
        )

        is_regular, missing_gaps = CyclePreprocessor.check_regularity(
            dates,
            observations_per_year,
        )

        # ======================================================
        # 1. CRECIMIENTO / VARIACIÓN
        # ======================================================

        growth = CyclePreprocessor.growth(
            values,
            use_log=use_log,
        )

        growth_dates = dates[1:]

        growth_periodogram = (
            CycleSignalAnalyzer.periodogram(
                growth,
                observations_per_year,
                dates=growth_dates,
            )
        )

        growth_periods = CycleDetector.get_valid_periods(
            growth_periodogram,
            len(growth),
            observations_per_year,
        )

        growth_autocorrelation = (
            CycleSignalAnalyzer.autocorrelation(
                growth
            )
        )

        # ======================================================
        # 2. DETRENDING LINEAL
        # ======================================================

        linear_cycle = (
            CyclePreprocessor.linear_detrend(
                values,
                use_log=use_log,
                dates=dates,
            )
        )

        linear_periodogram = (
            CycleSignalAnalyzer.periodogram(
                linear_cycle,
                observations_per_year,
                dates=dates,
            )
        )

        linear_periods = CycleDetector.get_valid_periods(
            linear_periodogram,
            len(linear_cycle),
            observations_per_year,
        )

        linear_autocorrelation = (
            CycleSignalAnalyzer.autocorrelation(
                linear_cycle
            )
        )

        # ======================================================
        # 3. HODRICK-PRESCOTT
        # ======================================================

        hp_trend, hp_cycle, resolved_hp_lambda = (
            CyclePreprocessor.hp_filter(
                values,
                lamb=hp_lambda,
                observations_per_year=observations_per_year,
                use_log=use_log,
            )
        )

        hp_periodogram = (
            CycleSignalAnalyzer.periodogram(
                hp_cycle,
                observations_per_year,
                dates=dates,
            )
        )

        hp_periods = CycleDetector.get_valid_periods(
            hp_periodogram,
            len(hp_cycle),
            observations_per_year,
        )

        hp_autocorrelation = (
            CycleSignalAnalyzer.autocorrelation(
                hp_cycle
            )
        )

        # ======================================================
        # 4. DETECCIÓN ROBUSTA
        # ======================================================

        method_results = {
            "growth": growth_periods,
            "linear_detrend": linear_periods,
            "hp": hp_periods,
        }

        robust_cycles = (
            CycleDetector.detect_robust_cycles(
                method_results,
                len(values),
                observations_per_year,
            )
        )

        # ======================================================
        # 5. RESULTADO
        # ======================================================

        return {
            "observations": len(values),

            "observations_per_year": (
                observations_per_year
            ),

            "sampling": {
                "is_regular": is_regular,
                "gaps_count": missing_gaps,
                "spectral_method": (
                    "lomb_scargle" if not is_regular else "fourier"
                ),
            },

            "transform": (
                "log"
                if use_log
                else "level"
            ),

            "start_date": (
                dates[0].date().isoformat()
            ),

            "end_date": (
                dates[-1].date().isoformat()
            ),

            "growth_observations": len(growth),

            "growth": {
                "series": [
                    {
                        "date": date.isoformat(),
                        "value": float(value),
                    }
                    for date, value in zip(
                        growth_dates,
                        growth,
                    )
                ],

                "autocorrelation": (
                    growth_autocorrelation
                ),

                "periodogram": (
                    growth_periodogram
                ),

                "dominant_periods": (
                    growth_periods[:top_n]
                ),
            },

            "linear_detrend": {
                "series": [
                    {
                        "date": date.isoformat(),
                        "value": float(value),
                    }
                    for date, value in zip(
                        dates,
                        linear_cycle,
                    )
                ],

                "autocorrelation": (
                    linear_autocorrelation
                ),

                "periodogram": (
                    linear_periodogram
                ),

                "dominant_periods": (
                    linear_periods[:top_n]
                ),
            },

            "hp": {
                "lambda": resolved_hp_lambda,

                "trend": [
                    {
                        "date": date.isoformat(),
                        "value": float(value),
                    }
                    for date, value in zip(
                        dates,
                        hp_trend,
                    )
                ],

                "cycle": [
                    {
                        "date": date.isoformat(),
                        "value": float(value),
                    }
                    for date, value in zip(
                        dates,
                        hp_cycle,
                    )
                ],

                "autocorrelation": (
                    hp_autocorrelation
                ),

                "periodogram": (
                    hp_periodogram
                ),

                "dominant_periods": (
                    hp_periods[:top_n]
                ),
            },

            "robust_cycles": robust_cycles,
        }

    @staticmethod
    def print_diagnostics(
        result: dict[str, Any],
    ) -> None:
        CycleDiagnostics.print(result)