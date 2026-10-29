from __future__ import annotations

import pandas as pd

from .utils.rolling import (
    rolling_mean,
    rolling_median,
    rolling_min,
    rolling_max,
    rolling_percentile,
    rolling_zscore,
)

from .utils.dynamics import (
    distance_from_rolling_mean,
)


"""
    Level Features
    --------------

    1. value                       → Valor actual de la serie.

    2. rolling_mean               → Media de los valores recientes.

    3. rolling_median             → Mediana de los valores recientes.

    4. rolling_min                → Mínimo de los valores recientes.

    5. rolling_max                → Máximo de los valores recientes.

    6. rolling_percentile         → Posición relativa del valor actual
                                    dentro de los valores recientes.

    7. rolling_zscore             → Mide cómo de anormal es el valor actual
                                    respecto a su comportamiento reciente.

    8. distance_from_rolling_mean → Mide cuánto se aleja el valor actual
                                    de su media móvil.
"""


def level_features(
    series: pd.Series,
    window: int,
) -> pd.DataFrame:
    """
    Calcula los features de nivel de una serie temporal.

    Parameters
    ----------
    series:
        Serie temporal de entrada.

    window:
        Tamaño de la ventana utilizada para las métricas rolling.

    Returns
    -------
    pd.DataFrame
        DataFrame con los features de nivel.
    """

    return pd.DataFrame(
        {
            "value": series,
            "rolling_mean": rolling_mean(
                series,
                window,
            ),
            "rolling_median": rolling_median(
                series,
                window,
            ),
            "rolling_min": rolling_min(
                series,
                window,
            ),
            "rolling_max": rolling_max(
                series,
                window,
            ),
            "rolling_percentile": rolling_percentile(
                series,
                window,
            ),
            "rolling_zscore": rolling_zscore(
                series,
                window,
            ),
            "distance_from_rolling_mean": distance_from_rolling_mean(
                series,
                window,
            ),
        },
        index=series.index,
    )