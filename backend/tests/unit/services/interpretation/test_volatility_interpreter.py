from __future__ import annotations

import pandas as pd

from app.services.interpretation.macro.volatility_interpreter import (
    VolatilityInterpreter,
)


def make_features(
    volatility=1.0,
    volatility_zscore=0.0,
    volatility_change=0.0,
):
    return pd.Series(
        {
            "rolling_volatility": volatility,
            "volatility_zscore": volatility_zscore,
            "volatility_change": volatility_change,
        }
    )


def make_signals(
    high=False,
    extreme=False,
    increasing=False,
    decreasing=False,
    shock=False,
):
    return pd.Series(
        {
            "high_volatility": high,
            "extreme_volatility": extreme,
            "volatility_increasing": increasing,
            "volatility_decreasing": decreasing,
            "volatility_shock": shock,
        }
    )


def interpret(
    *,
    features=None,
    signals=None,
):
    if features is None:
        features = make_features()

    if signals is None:
        signals = make_signals()

    return VolatilityInterpreter.interpret(
        features=features,
        signals=signals,
    )


# ---------------------------------------------------------------------
# LEVEL
# ---------------------------------------------------------------------


def test_extreme_signal_creates_extreme_level():
    result = interpret(
        signals=make_signals(
            extreme=True,
        ),
    )

    assert result["level"] == "extreme"


def test_extreme_level_has_priority_over_high_level():
    result = interpret(
        signals=make_signals(
            high=True,
            extreme=True,
        ),
    )

    assert result["level"] == "extreme"


def test_high_signal_creates_high_level():
    result = interpret(
        signals=make_signals(
            high=True,
            extreme=False,
        ),
    )

    assert result["level"] == "high"


def test_non_high_volatility_creates_normal_level():
    result = interpret(
        features=make_features(
            volatility=0.8,
        ),
        signals=make_signals(
            high=False,
            extreme=False,
        ),
    )

    assert result["level"] == "normal"


def test_missing_volatility_creates_unknown_level():
    result = interpret(
        features=make_features(
            volatility=None,
        ),
        signals=make_signals(
            high=False,
            extreme=False,
        ),
    )

    assert result["level"] == "unknown"


def test_high_signal_can_classify_level_when_volatility_value_is_missing():
    result = interpret(
        features=make_features(
            volatility=None,
        ),
        signals=make_signals(
            high=True,
        ),
    )

    assert result["level"] == "high"


def test_extreme_signal_can_classify_level_when_volatility_value_is_missing():
    result = interpret(
        features=make_features(
            volatility=None,
        ),
        signals=make_signals(
            extreme=True,
        ),
    )

    assert result["level"] == "extreme"


# ---------------------------------------------------------------------
# DIRECTION
# ---------------------------------------------------------------------


def test_increasing_signal_creates_rising_direction():
    result = interpret(
        features=make_features(
            volatility_change=-1.0,
        ),
        signals=make_signals(
            increasing=True,
            decreasing=False,
        ),
    )

    assert result["direction"] == "rising"


def test_decreasing_signal_creates_falling_direction():
    result = interpret(
        features=make_features(
            volatility_change=1.0,
        ),
        signals=make_signals(
            increasing=False,
            decreasing=True,
        ),
    )

    assert result["direction"] == "falling"


def test_increasing_and_decreasing_signals_use_volatility_change():
    result = interpret(
        features=make_features(
            volatility_change=1.0,
        ),
        signals=make_signals(
            increasing=True,
            decreasing=True,
        ),
    )

    assert result["direction"] == "rising"


def test_increasing_and_decreasing_signals_with_negative_change_are_falling():
    result = interpret(
        features=make_features(
            volatility_change=-1.0,
        ),
        signals=make_signals(
            increasing=True,
            decreasing=True,
        ),
    )

    assert result["direction"] == "falling"


def test_positive_volatility_change_creates_rising_direction():
    result = interpret(
        features=make_features(
            volatility_change=0.1,
        ),
        signals=make_signals(
            increasing=False,
            decreasing=False,
        ),
    )

    assert result["direction"] == "rising"


def test_negative_volatility_change_creates_falling_direction():
    result = interpret(
        features=make_features(
            volatility_change=-0.1,
        ),
        signals=make_signals(
            increasing=False,
            decreasing=False,
        ),
    )

    assert result["direction"] == "falling"


def test_zero_volatility_change_creates_stable_direction():
    result = interpret(
        features=make_features(
            volatility_change=0.0,
        ),
        signals=make_signals(
            increasing=False,
            decreasing=False,
        ),
    )

    assert result["direction"] == "stable"


def test_missing_volatility_change_creates_unknown_direction():
    result = interpret(
        features=make_features(
            volatility_change=None,
        ),
        signals=make_signals(
            increasing=False,
            decreasing=False,
        ),
    )

    assert result["direction"] == "unknown"


# ---------------------------------------------------------------------
# STRESS
# ---------------------------------------------------------------------


def test_zscore_below_elevated_threshold_is_normal_stress():
    result = interpret(
        features=make_features(
            volatility_zscore=0.99,
        ),
    )

    assert result["stress"] == "normal"


def test_zscore_exactly_at_elevated_threshold_is_elevated():
    result = interpret(
        features=make_features(
            volatility_zscore=VolatilityInterpreter.VOLATILITY_ELEVATED_ZSCORE,
        ),
    )

    assert result["stress"] == "elevated"


def test_zscore_between_elevated_and_extreme_is_elevated():
    result = interpret(
        features=make_features(
            volatility_zscore=1.5,
        ),
    )

    assert result["stress"] == "elevated"


def test_zscore_exactly_at_extreme_threshold_is_extreme():
    result = interpret(
        features=make_features(
            volatility_zscore=VolatilityInterpreter.VOLATILITY_EXTREME_ZSCORE,
        ),
    )

    assert result["stress"] == "extreme"


def test_zscore_above_extreme_threshold_is_extreme():
    result = interpret(
        features=make_features(
            volatility_zscore=3.5,
        ),
    )

    assert result["stress"] == "extreme"


def test_negative_zscore_is_normal_stress():
    result = interpret(
        features=make_features(
            volatility_zscore=-2.0,
        ),
    )

    assert result["stress"] == "normal"


def test_missing_zscore_creates_unknown_stress():
    result = interpret(
        features=make_features(
            volatility_zscore=None,
        ),
    )

    assert result["stress"] == "unknown"


# ---------------------------------------------------------------------
# SHOCK
# ---------------------------------------------------------------------


def test_shock_signal_is_preserved():
    result = interpret(
        signals=make_signals(
            shock=True,
        ),
    )

    assert result["shock"] is True


def test_no_shock_signal_returns_false():
    result = interpret(
        signals=make_signals(
            shock=False,
        ),
    )

    assert result["shock"] is False


def test_shock_does_not_change_level():
    result = interpret(
        features=make_features(
            volatility=1.0,
        ),
        signals=make_signals(
            high=False,
            extreme=False,
            shock=True,
        ),
    )

    assert result["level"] == "normal"
    assert result["shock"] is True


def test_shock_does_not_change_direction():
    result = interpret(
        features=make_features(
            volatility_change=0.0,
        ),
        signals=make_signals(
            shock=True,
        ),
    )

    assert result["direction"] == "stable"
    assert result["shock"] is True


def test_shock_does_not_change_stress():
    result = interpret(
        features=make_features(
            volatility_zscore=0.5,
        ),
        signals=make_signals(
            shock=True,
        ),
    )

    assert result["stress"] == "normal"
    assert result["shock"] is True


# ---------------------------------------------------------------------
# SEMANTIC SEPARATION
# ---------------------------------------------------------------------


def test_high_rising_elevated_volatility_is_not_automatically_extreme():
    result = interpret(
        features=make_features(
            volatility=2.0,
            volatility_zscore=1.5,
            volatility_change=0.5,
        ),
        signals=make_signals(
            high=True,
            extreme=False,
            increasing=True,
        ),
    )

    assert result["level"] == "high"
    assert result["direction"] == "rising"
    assert result["stress"] == "elevated"
    assert result["shock"] is False


def test_extreme_rising_extreme_stress_can_exist_without_shock():
    result = interpret(
        features=make_features(
            volatility=3.0,
            volatility_zscore=2.5,
            volatility_change=1.0,
        ),
        signals=make_signals(
            extreme=True,
            increasing=True,
            shock=False,
        ),
    )

    assert result["level"] == "extreme"
    assert result["direction"] == "rising"
    assert result["stress"] == "extreme"
    assert result["shock"] is False


def test_normal_level_can_have_elevated_stress():
    result = interpret(
        features=make_features(
            volatility=1.0,
            volatility_zscore=1.5,
        ),
        signals=make_signals(
            high=False,
            extreme=False,
        ),
    )

    assert result["level"] == "normal"
    assert result["stress"] == "elevated"


# ---------------------------------------------------------------------
# RAW VALUES AND SIGNALS
# ---------------------------------------------------------------------


def test_raw_values_are_returned():
    result = interpret(
        features=make_features(
            volatility=1.25,
            volatility_zscore=1.4,
            volatility_change=-0.35,
        ),
    )

    assert result["volatility"] == 1.25
    assert result["volatility_zscore"] == 1.4
    assert result["volatility_change"] == -0.35


def test_raw_boolean_signals_are_returned():
    result = interpret(
        signals=make_signals(
            high=True,
            extreme=True,
            increasing=True,
            decreasing=False,
            shock=True,
        ),
    )

    assert result["high"] is True
    assert result["extreme"] is True
    assert result["increasing"] is True
    assert result["decreasing"] is False
    assert result["shock"] is True


def test_output_contains_all_expected_fields():
    result = interpret()

    expected_keys = {
        "level",
        "direction",
        "stress",
        "shock",
        "high",
        "extreme",
        "increasing",
        "decreasing",
        "volatility",
        "volatility_zscore",
        "volatility_change",
    }

    assert set(result) == expected_keys