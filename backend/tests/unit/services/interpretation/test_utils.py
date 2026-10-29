from datetime import datetime

import numpy as np
import pandas as pd

from app.services.interpretation.utils import safe_float, serialize


# ============================================================
# safe_float
# ============================================================


def test_safe_float_with_integer():
    assert safe_float(10) == 10.0


def test_safe_float_with_float():
    assert safe_float(10.5) == 10.5


def test_safe_float_with_numeric_string():
    assert safe_float("10.5") == 10.5


def test_safe_float_with_none():
    assert safe_float(None) is None


def test_safe_float_with_invalid_string():
    assert safe_float("abc") is None


def test_safe_float_with_nan():
    assert safe_float(float("nan")) is None


def test_safe_float_with_pandas_nan():
    assert safe_float(pd.NA) is None


def test_safe_float_with_infinity():
    assert safe_float(float("inf")) == float("inf")


# ============================================================
# serialize
# ============================================================


def test_serialize_none():
    assert serialize(None) is None


def test_serialize_nan():
    assert serialize(float("nan")) is None


def test_serialize_pandas_nan():
    assert serialize(np.nan) is None


def test_serialize_datetime():
    value = datetime(2026, 8, 27, 20, 30, 0)

    assert serialize(value) == "2026-08-27T20:30:00"


def test_serialize_numpy_float():
    value = np.float64(10.5)

    assert serialize(value) == 10.5


def test_serialize_numpy_integer():
    value = np.int64(10)

    assert serialize(value) == 10


def test_serialize_normal_float():
    assert serialize(10.5) == 10.5


def test_serialize_normal_string():
    assert serialize("GDP") == "GDP"