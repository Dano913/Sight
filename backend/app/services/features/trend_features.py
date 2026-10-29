from __future__ import annotations

import numpy as np
import pandas as pd

from .utils.rolling import rolling_slope

from .utils.dynamics import acceleration


"""
Trend Features
--------------

1. rolling_slope_short
   → Mide la dirección e intensidad de la tendencia
     reciente de corto plazo.

2. rolling_slope_medium
   → Mide la dirección e intensidad de la tendencia
     de medio plazo.

3. rolling_slope_long
   → Mide la dirección e intensidad de la tendencia
     de largo plazo.

4. acceleration
   → Mide si la dinámica de la serie está acelerando
     o desacelerando.

5. slope_change
   → Mide cuánto ha cambiado la pendiente de corto plazo
     respecto al período anterior.

6. trend_change
   → Score continuo entre -1 y +1 que mide la intensidad
     y dirección del cambio de tendencia.

     +1 → fuerte cambio hacia una tendencia alcista.
      0 → sin cambio relevante.
     -1 → fuerte cambio hacia una tendencia bajista.
"""


def trend_features(
    series: pd.Series,
    short_window: int,
    medium_window: int,
    long_window: int,
) -> pd.DataFrame:
    """
    Calcula los features de tendencia de una serie temporal.

    Parameters
    ----------
    series:
        Serie temporal de entrada.

    short_window:
        Ventana utilizada para la tendencia de corto plazo.

    medium_window:
        Ventana utilizada para la tendencia de medio plazo.

    long_window:
        Ventana utilizada para la tendencia de largo plazo.

    Returns
    -------
    pd.DataFrame
        DataFrame con los features de tendencia.
    """

    slope_short = rolling_slope(
        series,
        short_window,
    )

    slope_medium = rolling_slope(
        series,
        medium_window,
    )

    slope_long = rolling_slope(
        series,
        long_window,
    )

    slope_change = slope_short.diff()

    # ==========================================================
    # CAMBIO DE TENDENCIA
    # ==========================================================
    #
    # Comparamos la pendiente de corto plazo con las
    # tendencias de medio y largo plazo.
    #
    # Si la pendiente corta está por encima de las
    # tendencias de fondo → mejora.
    #
    # Si está por debajo → deterioro.
    #
    # Se normaliza mediante el rango absoluto para obtener
    # un score aproximadamente comprendido entre -1 y +1.
    # ==========================================================

    trend_difference = (
        0.6 * (slope_short - slope_medium)
        + 0.4 * (slope_short - slope_long)
    )

    trend_scale = (
        slope_short.abs()
        + slope_medium.abs()
        + slope_long.abs()
    )

    trend_change = np.where(
        trend_scale == 0.0,
        0.0,
        trend_difference / trend_scale.replace(0.0, np.nan),
    )
    trend_change = pd.Series(trend_change, index=series.index)
    trend_change = trend_change.where(slope_long.notna(), np.nan)

    trend_change = trend_change.clip(
        lower=-1.0,
        upper=1.0,
    )

    return pd.DataFrame(
        {
            "rolling_slope_short": slope_short,
            "rolling_slope_medium": slope_medium,
            "rolling_slope_long": slope_long,
            "acceleration": acceleration(series),
            "slope_change": slope_change,
            "trend_change": trend_change,
        },
        index=series.index,
    )