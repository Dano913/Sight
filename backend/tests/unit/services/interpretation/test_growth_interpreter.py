from __future__ import annotations

import math

import pandas as pd
import pytest

from app.services.interpretation.macro.growth_interpreter import GrowthInterpreter


def make_features(
    *,
    percentage_change=0.02,
    acceleration=0.01,
) -> pd.Series:
    return pd.Series(
        {
            "percentage_change": percentage_change,
            "acceleration": acceleration,
        }
    )


def make_signals(
    *,
    positive_growth=False,
    negative_growth=False,
    accelerating_growth=False,
    decelerating_growth=False,
    growth_reversal=False,
) -> pd.Series:
    return pd.Series(
        {
            "positive_growth": positive_growth,
            "negative_growth": negative_growth,
            "accelerating_growth": accelerating_growth,
            "decelerating_growth": decelerating_growth,
            "growth_reversal": growth_reversal,
        }
    )


# ---------------------------------------------------------------------------
# STATE
# ---------------------------------------------------------------------------


def test_negative_signal_produces_negative_state():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(negative_growth=True),
    )

    assert result["state"] == "negative"


def test_positive_signal_produces_positive_state():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(positive_growth=True),
    )

    assert result["state"] == "positive"


def test_no_positive_or_negative_signal_produces_flat_state():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(),
    )

    assert result["state"] == "flat"


def test_negative_signal_has_priority_over_positive_signal():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(
            positive_growth=True,
            negative_growth=True,
        ),
    )

    assert result["state"] == "negative"


# ---------------------------------------------------------------------------
# GROWTH RATE STATE
# ---------------------------------------------------------------------------


def test_positive_percentage_change_is_positive_growth_rate():
    result = GrowthInterpreter.interpret(
        make_features(percentage_change=0.01),
        make_signals(),
    )

    assert result["growth_rate_state"] == "positive"


def test_negative_percentage_change_is_negative_growth_rate():
    result = GrowthInterpreter.interpret(
        make_features(percentage_change=-0.01),
        make_signals(),
    )

    assert result["growth_rate_state"] == "negative"


def test_percentage_change_inside_flat_threshold_is_flat():
    result = GrowthInterpreter.interpret(
        make_features(percentage_change=0.0005),
        make_signals(),
    )

    assert result["growth_rate_state"] == "flat"


def test_percentage_change_exactly_at_positive_threshold_is_flat():
    result = GrowthInterpreter.interpret(
        make_features(
            percentage_change=GrowthInterpreter.GROWTH_FLAT_THRESHOLD
        ),
        make_signals(),
    )

    assert result["growth_rate_state"] == "flat"


def test_percentage_change_exactly_at_negative_threshold_is_flat():
    result = GrowthInterpreter.interpret(
        make_features(
            percentage_change=-GrowthInterpreter.GROWTH_FLAT_THRESHOLD
        ),
        make_signals(),
    )

    assert result["growth_rate_state"] == "flat"


def test_percentage_change_just_above_positive_threshold_is_positive():
    result = GrowthInterpreter.interpret(
        make_features(
            percentage_change=GrowthInterpreter.GROWTH_FLAT_THRESHOLD + 1e-9
        ),
        make_signals(),
    )

    assert result["growth_rate_state"] == "positive"


def test_percentage_change_just_below_negative_threshold_is_negative():
    result = GrowthInterpreter.interpret(
        make_features(
            percentage_change=-GrowthInterpreter.GROWTH_FLAT_THRESHOLD - 1e-9
        ),
        make_signals(),
    )

    assert result["growth_rate_state"] == "negative"


def test_missing_percentage_change_produces_unknown_growth_rate_state():
    result = GrowthInterpreter.interpret(
        make_features(percentage_change=None),
        make_signals(),
    )

    assert result["growth_rate_state"] == "unknown"


# ---------------------------------------------------------------------------
# DIRECTION
# ---------------------------------------------------------------------------


def test_positive_acceleration_means_improving_direction():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=0.01),
        make_signals(),
    )

    assert result["direction"] == "improving"


def test_negative_acceleration_means_deteriorating_direction():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=-0.01),
        make_signals(),
    )

    assert result["direction"] == "deteriorating"


def test_zero_acceleration_means_stable_direction():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=0.0),
        make_signals(),
    )

    assert result["direction"] == "stable"


def test_missing_acceleration_produces_unknown_direction():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=None),
        make_signals(),
    )

    assert result["direction"] == "unknown"


def test_direction_is_independent_from_current_growth_state():
    result = GrowthInterpreter.interpret(
        make_features(
            percentage_change=-0.02,
            acceleration=0.01,
        ),
        make_signals(negative_growth=True),
    )

    assert result["state"] == "negative"
    assert result["direction"] == "improving"


def test_negative_growth_can_be_deteriorating():
    result = GrowthInterpreter.interpret(
        make_features(
            percentage_change=-0.02,
            acceleration=-0.01,
        ),
        make_signals(negative_growth=True),
    )

    assert result["state"] == "negative"
    assert result["direction"] == "deteriorating"


# ---------------------------------------------------------------------------
# ACCELERATION STATE
# ---------------------------------------------------------------------------


def test_positive_acceleration_has_positive_acceleration_state():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=0.01),
        make_signals(),
    )

    assert result["acceleration"] == "positive"


def test_negative_acceleration_has_negative_acceleration_state():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=-0.01),
        make_signals(),
    )

    assert result["acceleration"] == "negative"


def test_zero_acceleration_has_stable_acceleration_state():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=0.0),
        make_signals(),
    )

    assert result["acceleration"] == "stable"


def test_missing_acceleration_has_unknown_acceleration_state():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=None),
        make_signals(),
    )

    assert result["acceleration"] == "unknown"


# ---------------------------------------------------------------------------
# DYNAMIC STATE
# ---------------------------------------------------------------------------


def test_accelerating_signal_produces_accelerating_dynamic_state():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(accelerating_growth=True),
    )

    assert result["dynamic_state"] == "accelerating"


def test_decelerating_signal_produces_decelerating_dynamic_state():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(decelerating_growth=True),
    )

    assert result["dynamic_state"] == "decelerating"


def test_no_dynamic_signal_produces_stable_dynamic_state():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(),
    )

    assert result["dynamic_state"] == "stable"


def test_accelerating_signal_has_priority_over_decelerating_signal():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(
            accelerating_growth=True,
            decelerating_growth=True,
        ),
    )

    assert result["dynamic_state"] == "accelerating"


# ---------------------------------------------------------------------------
# REVERSAL
# ---------------------------------------------------------------------------


def test_reversal_signal_is_preserved_as_boolean():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(growth_reversal=True),
    )

    assert result["reversal"] is True


def test_reversal_defaults_to_false_when_signal_is_false():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(),
    )

    assert result["reversal"] is False


# ---------------------------------------------------------------------------
# RAW / SERIALIZED VALUES
# ---------------------------------------------------------------------------


def test_percentage_change_is_returned_as_raw_serialized_value():
    result = GrowthInterpreter.interpret(
        make_features(percentage_change=0.025),
        make_signals(),
    )

    assert result["percentage_change"] == 0.025


def test_acceleration_value_is_returned_as_raw_serialized_value():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=-0.015),
        make_signals(),
    )

    assert result["acceleration_value"] == -0.015


def test_none_percentage_change_is_preserved_as_none():
    result = GrowthInterpreter.interpret(
        make_features(percentage_change=None),
        make_signals(),
    )

    assert result["percentage_change"] is None


def test_none_acceleration_is_preserved_as_none():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=None),
        make_signals(),
    )

    assert result["acceleration_value"] is None


# ---------------------------------------------------------------------------
# OUTPUT CONTRACT
# ---------------------------------------------------------------------------


def test_result_contains_expected_keys():
    result = GrowthInterpreter.interpret(
        make_features(),
        make_signals(),
    )

    assert set(result) == {
        "state",
        "direction",
        "acceleration",
        "reversal",
        "percentage_change",
        "growth_rate_state",
        "acceleration_value",
        "dynamic_state",
    }


# ---------------------------------------------------------------------------
# SAFE_FLOAT / NON-FINITE VALUES
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "unknown"),
        (float("inf"), "positive"),
        (float("-inf"), "negative"),
    ],
)
def test_non_finite_percentage_change_behavior(value, expected):
    result = GrowthInterpreter.interpret(
        make_features(percentage_change=value),
        make_signals(),
    )

    assert result["growth_rate_state"] == expected


@pytest.mark.parametrize(
    "value, expected_direction, expected_acceleration",
    [
        (float("nan"), "unknown", "unknown"),
        (float("inf"), "improving", "positive"),
        (float("-inf"), "deteriorating", "negative"),
    ],
)
def test_non_finite_acceleration_behavior(
    value,
    expected_direction,
    expected_acceleration,
):
    result = GrowthInterpreter.interpret(
        make_features(acceleration=value),
        make_signals(),
    )

    assert result["direction"] == expected_direction
    assert result["acceleration"] == expected_acceleration


# ---------------------------------------------------------------------------
# SEMANTIC SEPARATION
# ---------------------------------------------------------------------------


def test_positive_growth_does_not_imply_improving_direction():
    result = GrowthInterpreter.interpret(
        make_features(
            percentage_change=0.02,
            acceleration=-0.01,
        ),
        make_signals(positive_growth=True),
    )

    assert result["state"] == "positive"
    assert result["direction"] == "deteriorating"


def test_negative_growth_does_not_imply_deteriorating_direction():
    result = GrowthInterpreter.interpret(
        make_features(
            percentage_change=-0.02,
            acceleration=0.01,
        ),
        make_signals(negative_growth=True),
    )

    assert result["state"] == "negative"
    assert result["direction"] == "improving"


def test_dynamic_state_is_independent_from_direction():
    result = GrowthInterpreter.interpret(
        make_features(acceleration=0.01),
        make_signals(decelerating_growth=True),
    )

    assert result["direction"] == "improving"
    assert result["dynamic_state"] == "decelerating"


# ---------------------------------------------------------------------------
# BOUNDARY / EXTREME VALUES
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "percentage_change, expected",
    [
        (1.0, "positive"),
        (-1.0, "negative"),
        (100.0, "positive"),
        (-100.0, "negative"),
    ],
)
def test_extreme_percentage_change_values(
    percentage_change,
    expected,
):
    result = GrowthInterpreter.interpret(
        make_features(percentage_change=percentage_change),
        make_signals(),
    )

    assert result["growth_rate_state"] == expected


@pytest.mark.parametrize(
    "acceleration, expected_direction, expected_state",
    [
        (1.0, "improving", "positive"),
        (-1.0, "deteriorating", "negative"),
        (100.0, "improving", "positive"),
        (-100.0, "deteriorating", "negative"),
    ],
)
def test_extreme_acceleration_values(
    acceleration,
    expected_direction,
    expected_state,
):
    result = GrowthInterpreter.interpret(
        make_features(acceleration=acceleration),
        make_signals(),
    )

    assert result["direction"] == expected_direction
    assert result["acceleration"] == expected_state


def test_rate_series_interpretation_with_change_column():
    features = pd.Series({"change": 0.25, "acceleration": 0.05})
    signals = make_signals(positive_growth=True)

    result = GrowthInterpreter.interpret(features, signals)

    assert result["growth_rate_state"] == "not_applicable"
    assert result["percentage_change"] is None
    assert result["state"] == "positive"
    assert result["direction"] == "improving"


def test_missing_variation_columns_does_not_crash():
    features = pd.Series({"acceleration": 0.05})
    signals = make_signals()

    result = GrowthInterpreter.interpret(features, signals)

    assert result["growth_rate_state"] == "unknown"
    assert result["percentage_change"] is None
    assert result["direction"] == "improving"
