from __future__ import annotations

import numpy as np
import pandas as pd

"""
    1. log_series()        → Transforma la serie mediante logaritmo.
    2. log_difference()    → Calcula crecimiento logarítmico.
    3. percentage_change() → Calcula crecimiento porcentual.
    4. cumulative_growth() → Calcula crecimiento acumulado entre dos puntos.
"""


def log_series(
    series: pd.Series,
) -> pd.Series:
    """
    Calcula el logaritmo natural de una serie positiva.

    Conserva el índice temporal original.
    """

    if not isinstance(series, pd.Series):
        raise TypeError(
            "series debe ser un pandas.Series"
        )

    if (series <= 0).any():
        raise ValueError(
            "La serie debe contener valores positivos "
            "para calcular el logaritmo."
        )

    return np.log(series)


def log_difference(
    series: pd.Series,
    periods: int = 1,
) -> pd.Series:
    """
    Calcula el crecimiento logarítmico de una serie positiva.

    Equivale a:

        log(X_t) - log(X_{t-p})

    Conserva el índice temporal original.

    La serie debe contener exclusivamente valores positivos.
    """

    if not isinstance(series, pd.Series):
        raise TypeError(
            "series debe ser un pandas.Series"
        )

    if periods < 1:
        raise ValueError(
            "periods debe ser >= 1"
        )

    if (series <= 0).any():
        raise ValueError(
            "La serie debe contener valores positivos "
            "para calcular la diferencia logarítmica."
        )

    return log_series(series).diff(periods)


def percentage_change(
    series: pd.Series,
    periods: int = 1,
) -> pd.Series:
    """
    Calcula el cambio porcentual de una serie.

    Equivale a:

        X_t
       _____  - 1
       X_{t-p}

    Conserva el índice temporal original.

    Si el valor anterior es 0, el cambio porcentual no está
    definido. En ese caso se devuelve NaN en lugar de inf/-inf.
    """

    if not isinstance(series, pd.Series):
        raise TypeError(
            "series debe ser un pandas.Series"
        )

    if periods < 1:
        raise ValueError(
            "periods debe ser >= 1"
        )

    result = series.pct_change(periods)

    # Evitar inf/-inf, que no son valores JSON válidos.
    result = result.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    return result


def cumulative_growth(
    series: pd.Series,
    periods: int,
) -> pd.Series:
    """
    Calcula el crecimiento acumulado desde el inicio
    de la serie.

    El crecimiento se calcula como:

        (X_t / X_0) - 1

    Los primeros `periods` valores se dejan como NaN.
    """

    if periods <= 0:
        raise ValueError(
            "periods debe ser mayor que 0"
        )

    result = series / series.iloc[0] - 1

    result.iloc[:periods] = np.nan

    return result