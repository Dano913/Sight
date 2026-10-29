from __future__ import annotations

import pandas as pd

from .utils.rolling import (
    rolling_std,
    rolling_range,
    rolling_zscore,
)

from .utils.dynamics import (
    rolling_volatility,
)


"""
    Volatility Features
    -------------------

    1. rolling_std        → Mide la variabilidad reciente de la serie
                            dentro de una ventana móvil.

    2. rolling_volatility → Mide la volatilidad reciente a partir de
                            los cambios porcentuales de la serie.

    3. rolling_range      → Mide la amplitud entre el máximo y el mínimo
                            dentro de una ventana móvil.

    4. volatility_change  → Mide cómo está cambiando la volatilidad
                            respecto al período anterior.

    5. volatility_zscore  → Mide cómo de anormal es la volatilidad actual
                            respecto a su comportamiento reciente.
"""


def volatility_features(
    series: pd.Series,
    window: int,
) -> pd.DataFrame:
    """
    Calcula los features de volatilidad de una serie temporal.

    Parameters
    ----------
    series:
        Serie temporal de entrada.

    window:
        Tamaño de la ventana utilizada para las métricas rolling.

    Returns
    -------
    pd.DataFrame
        DataFrame con los features de volatilidad.
    """

    std = rolling_std(
        series,
        window,
    )

    volatility = rolling_volatility(
        series,
        window,
    )

    return pd.DataFrame(
        {
            "rolling_std": std,
            "rolling_volatility": volatility,
            "rolling_range": rolling_range(
                series,
                window,
            ),
            "volatility_change": volatility.diff(),
            "volatility_zscore": rolling_zscore(
                volatility,
                window,
            ),
        },
        index=series.index,
    )