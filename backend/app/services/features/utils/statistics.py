from __future__ import annotations

import pandas as pd


"""
    Statistical Utilities
    ---------------------

    1. zscore()     → Mide cuántas desviaciones estándar se encuentra
                      cada observación respecto a la media histórica.

    2. percentile() → Indica qué posición ocupa cada observación dentro
                      de la distribución histórica completa.
"""


def zscore(
    series: pd.Series,
) -> pd.Series:
    """
    Calcula el z-score histórico de una serie.

    Mide la distancia de cada observación respecto a la media
    de toda la serie, expresada en desviaciones estándar.

    Parameters
    ----------
    series:
        Serie temporal de entrada.

    Returns
    -------
    pd.Series
        Z-score de cada observación.
    """

    mean = series.mean()
    std = series.std()

    if std == 0:
        return pd.Series(
            0.0,
            index=series.index,
        )

    return (series - mean) / std


def percentile(
    series: pd.Series,
) -> pd.Series:
    """
    Calcula el percentil histórico de cada observación.

    Indica qué proporción de las observaciones históricas
    son menores o iguales que cada valor.

    Parameters
    ----------
    series:
        Serie temporal de entrada.

    Returns
    -------
    pd.Series
        Percentil histórico de cada observación.
    """

    return series.rank(
        method="average",
        pct=True,
    )