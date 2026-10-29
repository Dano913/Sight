from __future__ import annotations

import numpy as np
import pandas as pd


"""
    1. rolling_zscore()     → Mide cómo de anormal es el valor actual
                              respecto a su comportamiento reciente.

    2. rolling_percentile() → Indica qué posición ocupa el valor actual
                              respecto a los valores recientes.

    3. rolling_slope()      → Mide si la serie está subiendo o bajando
                              y con qué intensidad.

    4. rolling_mean()       → Calcula la media de los valores recientes.

    5. rolling_std()        → Mide la variabilidad de los valores recientes.

    6. rolling_min()        → Obtiene el valor mínimo de los valores recientes.

    7. rolling_max()        → Obtiene el valor máximo de los valores recientes.

    8. rolling_range()      → Mide la amplitud entre el máximo y el mínimo
                              de los valores recientes.

    9. rolling_median()     → Calcula el valor central de los valores recientes.
"""


def rolling_zscore(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula el z-score rolling.
    """
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()

    return (series - mean) / std


def rolling_percentile(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula el percentil histórico rolling de la observación actual.
    """

    def percentile(
        values: np.ndarray,
    ) -> float:
        valid = values[~np.isnan(values)]

        if valid.size == 0:
            return np.nan

        current = valid[-1]

        return float(
            (valid <= current).sum()
            / valid.size
        )

    return (
        series
        .rolling(window)
        .apply(
            percentile,
            raw=True,
        )
    )


def rolling_slope(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula la pendiente de una regresión lineal rolling.
    """
    if window < 2:
        raise ValueError("window debe ser >= 2 para calcular la pendiente")

    x = np.arange(window, dtype=np.float64)
    x_centered = x - x.mean()
    weights = x_centered / float(np.sum(x_centered ** 2))

    def slope(
        values: np.ndarray,
    ) -> float:
        if np.isnan(values).any():
            return np.nan

        return float(np.dot(values, weights))

    return (
        series
        .rolling(window)
        .apply(
            slope,
            raw=True,
        )
    )


def rolling_mean(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula la media móvil de la serie.
    """
    return series.rolling(window).mean()


def rolling_std(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula la desviación estándar móvil de la serie.
    """
    return series.rolling(window).std()


def rolling_min(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula el mínimo dentro de cada ventana móvil.
    """
    return series.rolling(window).min()


def rolling_max(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula el máximo dentro de cada ventana móvil.
    """
    return series.rolling(window).max()


def rolling_range(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula el rango móvil: máximo menos mínimo.
    """
    rolling = series.rolling(window)

    return rolling.max() - rolling.min()


def rolling_median(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula la mediana móvil de la serie.
    """
    return series.rolling(window).median()