from __future__ import annotations

from app.services.analysis.cycle.cycle_diagnostics import (
    CycleDiagnostics,
)


def make_result():
    return {
        "start_date": "1980-01-01",
        "end_date": "2025-01-01",
        "observations": 46,
        "observations_per_year": 1,
        "growth": {
            "dominant_periods": [],
        },
        "linear_detrend": {
            "dominant_periods": [],
        },
        "hp": {
            "dominant_periods": [],
        },
        "robust_cycles": [],
    }


class TestCycleDiagnostics:

    def test_prints_without_cycles(
        self,
        capsys,
    ):
        CycleDiagnostics.print(
            make_result()
        )

        output = capsys.readouterr().out

        assert "DETECTOR ROBUSTO DE CICLOS" in output

        assert (
            "No se han encontrado ciclos"
            in output
        )

        assert "Frecuencia: anual" in output

    def test_prints_detected_cycle(
        self,
        capsys,
    ):
        result = make_result()

        result["robust_cycles"] = [
            {
                "period_years": 8.0,
                "score": 75.0,
                "confidence": "ALTA",
                "method_count": 3,
                "method_coverage": 1.0,
                "cycles_observable": 5.0,
                "period_dispersion": 0.02,
                "evidence": [
                    {
                        "method": "growth",
                        "period_years": 8.0,
                        "power": 1.0,
                        "relative_power": 0.50,
                    }
                ],
            }
        ]

        CycleDiagnostics.print(result)

        output = capsys.readouterr().out

        assert "8.00 años" in output
        assert "75.0/100" in output
        assert "ALTA" in output
        assert "3/3" in output
        assert "50.0%" not in output
        assert "0.5000" in output

        assert (
            "El ciclo con mayor evidencia"
            in output
        )

        assert (
            "detectado por 3 de 3 métodos"
            in output
        )

        assert (
            "La muestra permite observar"
            in output
        )

        assert (
            "periodicidades estadísticas"
            in output
        )