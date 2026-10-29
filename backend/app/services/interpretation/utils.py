from __future__ import annotations

from typing import Any

import pandas as pd


def safe_float(value: Any) -> float | None:
    """
    Convierte un valor a float de forma segura.

    Devuelve None cuando el valor no puede convertirse
    o representa un valor nulo/NaN.
    """
    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if pd.isna(value):
        return None

    return value


def serialize(value: Any) -> Any:
    """
    Convierte valores pandas/numpy en tipos serializables.

    Maneja:
        - None
        - NaN
        - fechas/objetos con isoformat()
        - valores numpy con item()
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "isoformat"):
        return value.isoformat()

    if hasattr(value, "item"):
        return value.item()

    return value