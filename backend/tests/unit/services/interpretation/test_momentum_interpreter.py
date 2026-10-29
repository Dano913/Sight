from unittest.mock import patch

import pandas as pd

from app.services.interpretation.macro.momentum_interpreter import (
    MomentumInterpreter,
)


def make_features(
    momentum=0.5,
    acceleration=0.1,
):
    return pd.Series(
        {
            "momentum": momentum,
            "acceleration": acceleration,
        }
    )


def make_signals(
    positive_momentum=False,
    negative_momentum=False,
    momentum_improving=False,
    momentum_weakening=False,
):
    return pd.Series(
        {
            "positive_momentum": positive_momentum,
            "negative_momentum": negative_momentum,
            "momentum_improving": momentum_improving,
            "momentum_weakening": momentum_weakening,
        }
    )


def test_positive_momentum():
    result = MomentumInterpreter.interpret(
        make_features(momentum=0.5, acceleration=0.1),
        make_signals(positive_momentum=True),
    )

    assert result["state"] == "positive"
    assert result["direction"] == "improving"
    assert result["acceleration"] == "positive"
    assert result["value"] == 0.5
    assert result["acceleration_value"] == 0.1
    assert result["positive"] is True
    assert result["negative"] is False
    assert result["improving"] is False
    assert result["weakening"] is False


def test_negative_momentum():
    result = MomentumInterpreter.interpret(
        make_features(momentum=-0.5, acceleration=-0.1),
        make_signals(negative_momentum=True),
    )

    assert result["state"] == "negative"
    assert result["direction"] == "deteriorating"
    assert result["acceleration"] == "negative"
    assert result["value"] == -0.5
    assert result["acceleration_value"] == -0.1
    assert result["positive"] is False
    assert result["negative"] is True
    assert result["improving"] is False
    assert result["weakening"] is False


def test_zero_momentum_is_neutral_when_no_signal():
    result = MomentumInterpreter.interpret(
        make_features(momentum=0.0, acceleration=0.0),
        make_signals(),
    )

    assert result["state"] == "neutral"
    assert result["direction"] == "stable"
    assert result["acceleration"] == "stable"


def test_positive_momentum_without_positive_signal_uses_value():
    result = MomentumInterpreter.interpret(
        make_features(momentum=0.5, acceleration=0.0),
        make_signals(),
    )

    assert result["state"] == "positive"


def test_negative_momentum_without_negative_signal_uses_value():
    result = MomentumInterpreter.interpret(
        make_features(momentum=-0.5, acceleration=0.0),
        make_signals(),
    )

    assert result["state"] == "negative"


def test_improving_signal_has_priority_over_acceleration():
    result = MomentumInterpreter.interpret(
        make_features(momentum=0.5, acceleration=-0.1),
        make_signals(momentum_improving=True),
    )

    assert result["direction"] == "improving"
    assert result["acceleration"] == "negative"


def test_weakening_signal_has_priority_over_acceleration():
    result = MomentumInterpreter.interpret(
        make_features(momentum=0.5, acceleration=0.1),
        make_signals(momentum_weakening=True),
    )

    assert result["direction"] == "deteriorating"
    assert result["acceleration"] == "positive"


def test_direction_is_stable_when_acceleration_is_zero():
    result = MomentumInterpreter.interpret(
        make_features(momentum=0.5, acceleration=0.0),
        make_signals(),
    )

    assert result["direction"] == "stable"
    assert result["acceleration"] == "stable"


def test_missing_momentum_is_unknown():
    result = MomentumInterpreter.interpret(
        make_features(momentum=float("nan"), acceleration=0.1),
        make_signals(),
    )

    assert result["state"] == "unknown"
    assert result["direction"] == "improving"
    assert result["acceleration"] == "positive"


def test_missing_acceleration_is_unknown():
    result = MomentumInterpreter.interpret(
        make_features(momentum=0.5, acceleration=float("nan")),
        make_signals(),
    )

    assert result["state"] == "positive"
    assert result["direction"] == "unknown"
    assert result["acceleration"] == "unknown"


def test_signals_are_preserved_as_booleans():
    result = MomentumInterpreter.interpret(
        make_features(momentum=0.5, acceleration=0.1),
        make_signals(
            positive_momentum=True,
            negative_momentum=False,
            momentum_improving=True,
            momentum_weakening=False,
        ),
    )

    assert result["positive"] is True
    assert result["negative"] is False
    assert result["improving"] is True
    assert result["weakening"] is False


def test_output_contains_only_public_momentum_fields():
    result = MomentumInterpreter.interpret(
        make_features(),
        make_signals(),
    )

    assert set(result) == {
        "state",
        "direction",
        "acceleration",
        "value",
        "acceleration_value",
        "positive",
        "negative",
        "improving",
        "weakening",
    }