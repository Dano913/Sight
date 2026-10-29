from __future__ import annotations

import numpy as np
import pandas as pd

"""
    1. validate_frequency() → Valida la frecuencia de la serie.
    2. periods_per_year()   → Calcula el número de observaciones por año según frecuencia.
    3. prepare_series()     → Prepara la serie para análisis.
"""

PERIODS_PER_YEAR: dict[str, int] = {
    "monthly": 12,
    "quarterly": 4,
    "annual": 1,
}


def validate_frequency(frequency: str) -> None:
    """
    Valida que la frecuencia sea una de las soportadas.
    """

    if frequency not in PERIODS_PER_YEAR:
        raise ValueError(
            "frequency debe ser "
            "'monthly', 'quarterly' o 'annual'"
        )


def periods_per_year(frequency: str) -> int:
    """
    Devuelve el número de observaciones por año
    correspondiente a la frecuencia.
    """

    validate_frequency(frequency)

    return PERIODS_PER_YEAR[frequency]


def prepare_series(
    series: pd.Series,
    *,
    require_positive: bool = False,
) -> pd.Series:
    """
    Valida y normaliza una serie temporal.

    Parameters
    ----------
    series:
        Serie temporal de entrada.

    require_positive:
        Si True, todos los valores deben ser > 0.
        Necesario para transformaciones logarítmicas.

    Returns
    -------
    pd.Series
        Copia limpia y ordenada cronológicamente.
    """

    if not isinstance(series, pd.Series):
        raise TypeError(
            "series debe ser un pandas.Series"
        )

    s = series.copy()

    s = pd.to_numeric(
        s,
        errors="coerce",
    ).astype(float)

    s = s.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    s = s.dropna()

    if s.empty:
        raise ValueError(
            "La serie no contiene observaciones válidas"
        )

    if not s.index.is_monotonic_increasing:
        s = s.sort_index()

    if require_positive and (s <= 0).any():
        raise ValueError(
            "La serie debe contener valores positivos"
        )

    return s