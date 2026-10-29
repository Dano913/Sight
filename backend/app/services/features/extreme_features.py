from __future__ import annotations

import numpy as np
import pandas as pd

from .utils.statistics import (
    zscore,
    percentile,
)

from .utils.dynamics import (
    drawdown,
)


"""
    Extreme Features
    -----------------

    1. zscore              → Mide cómo de alejado está el valor actual
                             respecto a la media histórica, en desviaciones
                             estándar.

    2. percentile          → Indica qué posición ocupa el valor actual
                             dentro de toda la distribución histórica.

    3. distance_from_max    → Mide la distancia del valor actual respecto
                             al máximo de la ventana reciente.

    4. distance_from_min    → Mide la distancia del valor actual respecto
                             al mínimo de la ventana reciente.

    5. drawdown             → Mide la caída del valor actual respecto
                             a su máximo histórico acumulado.
"""


def extreme_features(
    series: pd.Series,
    window: int,
) -> pd.DataFrame:
    """
    Calcula los features de extremos de una serie temporal.

    Parameters
    ----------
    series:
        Serie temporal de entrada.

    window:
        Tamaño de la ventana utilizada para los extremos recientes.

    Returns
    -------
    pd.DataFrame
        DataFrame con los features de extremos.
    """

    rolling_max = series.rolling(window).max()
    rolling_min = series.rolling(window).min()

    denom_max = rolling_max.abs().replace(0.0, np.nan)
    distance_from_max = (
        (series - rolling_max)
        / denom_max
    )

    denom_min = rolling_min.abs().replace(0.0, np.nan)
    distance_from_min = (
        (series - rolling_min)
        / denom_min
    )

    distance_from_max = distance_from_max.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    distance_from_min = distance_from_min.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    return pd.DataFrame(
        {
            "zscore": zscore(
                series,
            ),

            "percentile": percentile(
                series,
            ),

            "distance_from_max": distance_from_max,

            "distance_from_min": distance_from_min,

            "drawdown": drawdown(
                series,
            ),
        },
        index=series.index,
    )