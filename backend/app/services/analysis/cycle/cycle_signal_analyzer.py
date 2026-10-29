from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import signal

from .cycle_preprocessor import CyclePreprocessor


class CycleSignalAnalyzer:
    """
    Analiza propiedades estadísticas de una señal temporal.

    Responsabilidades:
    - Autocorrelación.
    - Periodograma.
    """

    @staticmethod
    def autocorrelation(
        series: np.ndarray,
    ) -> list[dict[str, float]]:
        """
        Calcula la autocorrelación normalizada
        para todos los lags disponibles.
        """

        series = np.asarray(
            series,
            dtype=float,
        )

        if len(series) < 3:
            return []

        centered = series - np.mean(series)

        denominator = np.dot(
            centered,
            centered,
        )

        if denominator == 0:
            return []

        result = []

        for lag in range(1, len(series)):
            numerator = np.dot(
                centered[:-lag],
                centered[lag:],
            )

            result.append(
                {
                    "lag": lag,
                    "autocorrelation": float(
                        numerator / denominator
                    ),
                }
            )

        return result

    @staticmethod
    def periodogram(
        series: np.ndarray,
        observations_per_year: int,
        *,
        dates: pd.DatetimeIndex | None = None,
    ) -> list[dict[str, float]]:
        """
        Calcula el periodograma de una serie temporal.

        Si se proporcionan `dates` y se detectan lagunas o muestreo
        irregular, se utiliza automáticamente el algoritmo de Lomb-Scargle
        para preservar la periodicidad física real sin distorsión espectral.

        Parameters
        ----------
        series:
            Serie temporal previamente transformada/detrendida.
        observations_per_year:
            Número de observaciones por año:
            1 = anual, 4 = trimestral, 12 = mensual.
        dates:
            Fechas asociadas a las observaciones (opcional).

        Returns
        -------
        list[dict[str, float]]
            Frecuencia, periodo en años, potencia absoluta
            y potencia relativa.
        """

        series = np.asarray(
            series,
            dtype=float,
        )

        if len(series) < 4:
            return []

        if observations_per_year <= 0:
            raise ValueError(
                "observations_per_year debe ser mayor que 0."
            )

        if not np.all(np.isfinite(series)):
            return []

        # Detección de irregularidad temporal y delegación a Lomb-Scargle
        if dates is not None and len(dates) == len(series):
            is_regular, missing_count = CyclePreprocessor.check_regularity(
                dates, observations_per_year
            )
            if not is_regular and missing_count > 0:
                return CycleSignalAnalyzer._periodogram_lombscargle(
                    series=series,
                    dates=dates,
                    observations_per_year=observations_per_year,
                )

        series = series - np.mean(series)

        frequencies, power = signal.periodogram(
            series,
            fs=float(observations_per_year),
            detrend=False,
            scaling="density",
        )

        valid = frequencies > 0

        frequencies = frequencies[valid]
        power = power[valid]

        total_power = float(
            np.sum(power)
        )

        if total_power <= 0:
            return []

        result = []

        for frequency, power_value in zip(
            frequencies,
            power,
        ):
            if frequency <= 0:
                continue

            period = (
                1.0 / frequency
            )

            if not np.isfinite(period):
                continue

            relative_power = (
                float(power_value)
                / total_power
            )

            result.append(
                {
                    "frequency": float(frequency),
                    "period_years": float(period),
                    "power": float(power_value),
                    "relative_power": relative_power,
                }
            )

        return result

    @staticmethod
    def _periodogram_lombscargle(
        series: np.ndarray,
        dates: pd.DatetimeIndex,
        observations_per_year: int,
    ) -> list[dict[str, float]]:
        """
        Calcula el periodograma de Lomb-Scargle para series temporales
        con lagunas o muestreo no equiespaciado.
        """
        t_seconds = (dates - dates[0]).total_seconds().to_numpy(dtype=float)
        t_years = t_seconds / (365.25 * 86400.0)

        duration = float(t_years[-1] - t_years[0])
        if duration <= 0:
            return []

        centered = series - np.mean(series)

        min_freq = 1.0 / duration
        max_freq = float(observations_per_year) / 2.0

        if min_freq >= max_freq:
            return []

        num_freqs = max(len(series) * 4, 256)
        frequencies = np.linspace(min_freq, max_freq, num_freqs)
        angular_freqs = 2.0 * np.pi * frequencies

        power = signal.lombscargle(
            t_years,
            centered,
            angular_freqs,
            normalize=False,
        )

        total_power = float(np.sum(power))
        if total_power <= 0:
            return []

        result = []
        for frequency, power_value in zip(frequencies, power):
            if frequency <= 0:
                continue

            period = 1.0 / frequency
            if not np.isfinite(period):
                continue

            relative_power = float(power_value) / total_power

            result.append(
                {
                    "frequency": float(frequency),
                    "period_years": float(period),
                    "power": float(power_value),
                    "relative_power": relative_power,
                }
            )

        return result