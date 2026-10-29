from __future__ import annotations

import numpy as np
import pandas as pd


"""
    1. acceleration()                 → Mide si la tasa de cambio de la serie
                                        está acelerando o desacelerando.

    2. rolling_volatility()           → Mide la variabilidad reciente de la
                                        serie mediante una ventana móvil.

    3. drawdown()                     → Mide la caída de la serie respecto
                                        a su máximo histórico anterior.

    4. distance_from_rolling_mean()   → Mide cuánto se aleja el valor actual
                                        de su media móvil.

    5. momentum()                     → Mide el cambio de la serie respecto
                                        a un número determinado de períodos
                                        anteriores.
"""


def acceleration(
    series: pd.Series,
) -> pd.Series:
    """
    Calcula la aceleración de la serie.

    Mide el cambio de la tasa de cambio entre observaciones consecutivas.
    """
    change = series.diff()

    return change.diff()


def rolling_volatility(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula la volatilidad rolling de la serie.

    Se define como la desviación estándar móvil de los cambios
    porcentuales de la serie.

    Si el cambio porcentual no está definido por un valor anterior
    igual a cero, se conserva como NaN.
    """
    returns = series.pct_change()

    returns = returns.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    return returns.rolling(window).std()


def drawdown(
    series: pd.Series,
) -> pd.Series:
    """
    Calcula el drawdown de la serie respecto a su máximo histórico.

    Devuelve la caída porcentual desde el máximo acumulado hasta
    cada observación.
    """
    running_max = series.cummax()
    denom = running_max.abs().replace(0.0, np.nan)

    result = (series - running_max) / denom

    return result.replace(
        [np.inf, -np.inf],
        np.nan,
    )


def distance_from_rolling_mean(
    series: pd.Series,
    window: int,
) -> pd.Series:
    """
    Calcula la distancia del valor actual respecto a su media móvil.

    Devuelve la diferencia porcentual entre la observación actual
    y la media de la ventana.
    """
    rolling_mean = series.rolling(window).mean()
    denom = rolling_mean.abs().replace(0.0, np.nan)

    result = (series - rolling_mean) / denom

    return result.replace(
        [np.inf, -np.inf],
        np.nan,
    )


def momentum(
    series: pd.Series,
    periods: int,
) -> pd.Series:
    """
    Calcula el momentum de la serie.

    Mide el cambio porcentual respecto al valor de hace
    un número determinado de períodos.

    Si el valor de referencia es cero, el cambio porcentual
    no está definido y se devuelve NaN.
    """
    result = series.pct_change(periods)

    return result.replace(
        [np.inf, -np.inf],
        np.nan,
    )