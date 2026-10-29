from __future__ import annotations

import pandas as pd

from app.models.enums import GrowthMethod

from .utils.validation import periods_per_year
from .utils.transformations import (
    log_difference,
    percentage_change,
    cumulative_growth,
)
from .utils.dynamics import momentum


"""
Growth Features
---------------

Para series de nivel:

1. log_difference()
2. percentage_change()
3. cumulative_growth()
4. momentum()
5. yoy_growth()
6. yoy_log_growth()

Para series de tasa:

1. change()
2. yoy_change()
3. momentum()

Las series de tasa no utilizan transformaciones logarítmicas
ni cambios porcentuales porque pueden cruzar cero.
"""


MOMENTUM_PERIODS: dict[str, int] = {
    "daily": 20,
    "weekly": 4,
    "monthly": 3,
    "quarterly": 2,
    "annual": 2,
}


def growth_features(
    series: pd.Series,
    frequency: str,
    growth_method: GrowthMethod = GrowthMethod.LOG,
) -> pd.DataFrame:
    """
    Calcula los features de crecimiento de una serie temporal.

    LOG:
        Utilizado para series de nivel positivas.

    RATE:
        Utilizado para tasas o series que pueden cruzar cero.
        El crecimiento y momentum se expresan como cambio absoluto
        (diferencia aritmética) para evitar distorsiones por cruce de cero
        o división por niveles negativos.

    Parameters
    ----------
    series:
        Serie temporal de entrada.

    frequency:
        Frecuencia de la serie.

    growth_method:
        Método de transformación apropiado para el indicador.

    Returns
    -------
    pd.DataFrame
        DataFrame con los features de crecimiento.
    """

    periods = periods_per_year(frequency)
    momentum_periods = MOMENTUM_PERIODS[frequency]

    if growth_method == GrowthMethod.RATE:
        return pd.DataFrame(
            {
                "change": series.diff(),
                "yoy_change": series.diff(periods),
                "momentum": series.diff(momentum_periods),
            },
            index=series.index,
        )

    return pd.DataFrame(
        {
            "log_difference": log_difference(
                series,
            ),
            "percentage_change": percentage_change(
                series,
            ),
            "cumulative_growth": cumulative_growth(
                series,
                periods=periods,
            ),
            "momentum": momentum(
                series,
                periods=momentum_periods,
            ),
            "yoy_growth": percentage_change(
                series,
                periods=periods,
            ),
            "yoy_log_growth": log_difference(
                series,
                periods=periods,
            ),
        },
        index=series.index,
    )