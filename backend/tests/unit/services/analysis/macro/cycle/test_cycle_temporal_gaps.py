from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from app.services.analysis.cycle.cycle_analysis_service import (
    CycleAnalysisService,
)
from app.services.analysis.cycle.cycle_preprocessor import (
    CyclePreprocessor,
)
from app.services.analysis.cycle.cycle_signal_analyzer import (
    CycleSignalAnalyzer,
)


def make_obs(d: date, val: float):
    return type(
        "Observation",
        (),
        {
            "date": d,
            "value": val,
        },
    )()


class TestCycleTemporalGaps:

    def test_check_regularity_detects_regular_series(self):
        dates = pd.date_range("2020-01-01", periods=12, freq="MS")
        is_regular, missing = CyclePreprocessor.check_regularity(dates, observations_per_year=12)

        assert is_regular is True
        assert missing == 0

    def test_check_regularity_detects_gapped_monthly_series(self):
        # 2020-01, 2020-02, 2020-05 (faltan marzo y abril -> 2 meses)
        dates = pd.to_datetime(["2020-01-01", "2020-02-01", "2020-05-01", "2020-06-01"])
        is_regular, missing = CyclePreprocessor.check_regularity(dates, observations_per_year=12)

        assert is_regular is False
        assert missing == 2

    def test_check_regularity_detects_gapped_quarterly_series(self):
        # 2020-Q1, 2020-Q2, 2021-Q1 (faltan Q3 y Q4 -> 2 trimestres)
        dates = pd.to_datetime(["2020-01-01", "2020-04-01", "2021-01-01", "2021-04-01"])
        is_regular, missing = CyclePreprocessor.check_regularity(dates, observations_per_year=4)

        assert is_regular is False
        assert missing == 2

    def test_linear_detrend_with_dates_avoids_gap_distortion(self):
        # Serie perfectamente lineal en el tiempo: y = 100 + 2 * t_years
        dates = pd.to_datetime(["2020-01-01", "2020-04-01", "2021-01-01", "2021-04-01"])
        t_years = (dates - dates[0]).days / 365.25
        values = 100.0 + 2.0 * t_years

        # Con fechas, el residuo del detrending lineal debe ser exactamente 0
        detrended = CyclePreprocessor.linear_detrend(values, use_log=False, dates=dates)
        assert np.allclose(detrended, 0.0, atol=1e-10)

    def test_periodogram_uses_lomb_scargle_for_gapped_series(self):
        # Onda sinusoidal pura de 5 años con muestreo mensual y huecos
        np.random.seed(42)
        dates_all = pd.date_range("2000-01-01", periods=120, freq="MS") # 10 años
        t_years = (dates_all - dates_all[0]).days / 365.25
        wave = np.sin(2 * np.pi * t_years / 5.0)

        # Introducir una laguna de 6 meses
        mask = np.ones(len(dates_all), dtype=bool)
        mask[30:36] = False
        dates_gapped = dates_all[mask]
        wave_gapped = wave[mask]

        pgram = CycleSignalAnalyzer.periodogram(
            wave_gapped,
            observations_per_year=12,
            dates=dates_gapped,
        )

        assert len(pgram) > 0
        peak = max(pgram, key=lambda x: x["power"])
        # El periodo detectado debe estar muy próximo al periodo real de 5 años
        assert np.isclose(peak["period_years"], 5.0, atol=0.25)

    def test_cycle_analysis_service_sampling_metadata(self):
        # Observaciones con un hueco
        dates = [
            date(2000, 1, 1),
            date(2001, 1, 1),
            date(2002, 1, 1),
            # Salto de 2 años (falta 2003 y 2004)
            date(2005, 1, 1),
            date(2006, 1, 1),
            date(2007, 1, 1),
            date(2008, 1, 1),
            date(2009, 1, 1),
            date(2010, 1, 1),
            date(2011, 1, 1),
        ]
        obs = [
            make_obs(d, 100.0 + i)
            for i, d in enumerate(dates)
        ]

        result = CycleAnalysisService.analyze(obs)

        assert "sampling" in result
        sampling = result["sampling"]
        assert sampling["is_regular"] is False
        assert sampling["gaps_count"] == 2
        assert sampling["spectral_method"] == "lomb_scargle"
