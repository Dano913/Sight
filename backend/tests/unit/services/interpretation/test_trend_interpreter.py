from __future__ import annotations

import pandas as pd

from app.services.interpretation.macro.trend_interpreter import TrendInterpreter


def make_features(
    short_slope=1.0,
    medium_slope=1.0,
    long_slope=1.0,
    acceleration=0.1,
    slope_change=0.1,
    trend_change=0.1,
):
    return pd.Series(
        {
            "rolling_slope_short": short_slope,
            "rolling_slope_medium": medium_slope,
            "rolling_slope_long": long_slope,
            "acceleration": acceleration,
            "slope_change": slope_change,
            "trend_change": trend_change,
        }
    )


def make_signals(
    bullish=True,
    bearish=False,
    mixed=False,
    reversal=False,
    strengthening=False,
    weakening=False,
):
    return pd.Series(
        {
            "bullish_trend": bullish,
            "bearish_trend": bearish,
            "mixed_trend": mixed,
            "trend_reversal": reversal,
            "trend_strengthening": strengthening,
            "trend_weakening": weakening,
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

    return TrendInterpreter.interpret(
        features=features,
        signals=signals,
    )


# ---------------------------------------------------------------------
# STATE
# ---------------------------------------------------------------------


def test_positive_slopes_create_bullish_state():
    result = interpret(
        features=make_features(
            short_slope=1.0,
            medium_slope=2.0,
            long_slope=3.0,
        ),
    )

    assert result["state"] == "bullish"


def test_negative_slopes_create_bearish_state():
    result = interpret(
        features=make_features(
            short_slope=-1.0,
            medium_slope=-2.0,
            long_slope=-3.0,
        ),
        signals=make_signals(
            bullish=False,
            bearish=True,
        ),
    )

    assert result["state"] == "bearish"


def test_zero_slopes_create_neutral_state():
    result = interpret(
        features=make_features(
            short_slope=0.0,
            medium_slope=0.0,
            long_slope=0.0,
        ),
        signals=make_signals(
            bullish=False,
            bearish=False,
            mixed=False,
        ),
    )

    assert result["state"] == "neutral"


def test_mixed_slopes_create_mixed_state():
    result = interpret(
        features=make_features(
            short_slope=1.0,
            medium_slope=-1.0,
            long_slope=1.0,
        ),
        signals=make_signals(
            bullish=False,
            bearish=False,
            mixed=True,
        ),
    )

    assert result["state"] == "mixed"


def test_epsilon_slopes_are_considered_neutral():
    epsilon = TrendInterpreter.TREND_EPSILON

    result = interpret(
        features=make_features(
            short_slope=epsilon,
            medium_slope=-epsilon,
            long_slope=0.0,
        ),
        signals=make_signals(
            bullish=False,
            bearish=False,
            mixed=False,
        ),
    )

    assert result["state"] == "neutral"


def test_partial_missing_slopes_fall_back_to_bullish_signal():
    result = interpret(
        features=make_features(
            short_slope=None,
            medium_slope=None,
            long_slope=None,
        ),
        signals=make_signals(
            bullish=True,
            bearish=False,
            mixed=False,
        ),
    )

    assert result["state"] == "bullish"


def test_partial_missing_slopes_fall_back_to_bearish_signal():
    result = interpret(
        features=make_features(
            short_slope=None,
            medium_slope=None,
            long_slope=None,
        ),
        signals=make_signals(
            bullish=False,
            bearish=True,
            mixed=False,
        ),
    )

    assert result["state"] == "bearish"


def test_partial_missing_slopes_fall_back_to_mixed_signal():
    result = interpret(
        features=make_features(
            short_slope=None,
            medium_slope=None,
            long_slope=None,
        ),
        signals=make_signals(
            bullish=False,
            bearish=False,
            mixed=True,
        ),
    )

    assert result["state"] == "mixed"


def test_missing_slopes_and_signals_create_unknown_state():
    result = interpret(
        features=make_features(
            short_slope=None,
            medium_slope=None,
            long_slope=None,
        ),
        signals=make_signals(
            bullish=False,
            bearish=False,
            mixed=False,
        ),
    )

    assert result["state"] == "unknown"


# ---------------------------------------------------------------------
# INDIVIDUAL SLOPE DIRECTIONS
# ---------------------------------------------------------------------


def test_individual_slope_directions_are_returned():
    result = interpret(
        features=make_features(
            short_slope=1.0,
            medium_slope=-1.0,
            long_slope=0.0,
        ),
    )

    assert result["short_direction"] == "up"
    assert result["medium_direction"] == "down"
    assert result["long_direction"] == "flat"


def test_missing_individual_slopes_are_unknown():
    result = interpret(
        features=make_features(
            short_slope=None,
            medium_slope=None,
            long_slope=None,
        ),
        signals=make_signals(),
    )

    assert result["short_direction"] == "unknown"
    assert result["medium_direction"] == "unknown"
    assert result["long_direction"] == "unknown"


# ---------------------------------------------------------------------
# DIRECTION
# ---------------------------------------------------------------------


def test_strengthening_signal_has_priority_for_improving_direction():
    result = interpret(
        features=make_features(
            trend_change=-10.0,
        ),
        signals=make_signals(
            strengthening=True,
            weakening=False,
        ),
    )

    assert result["direction"] == "improving"


def test_weakening_signal_has_priority_for_deteriorating_direction():
    result = interpret(
        features=make_features(
            trend_change=10.0,
        ),
        signals=make_signals(
            strengthening=False,
            weakening=True,
        ),
    )

    assert result["direction"] == "deteriorating"


def test_both_strengthening_and_weakening_use_trend_change():
    result = interpret(
        features=make_features(
            trend_change=0.5,
        ),
        signals=make_signals(
            strengthening=True,
            weakening=True,
        ),
    )

    assert result["direction"] == "improving"


def test_both_strengthening_and_weakening_with_negative_change_is_deteriorating():
    result = interpret(
        features=make_features(
            trend_change=-0.5,
        ),
        signals=make_signals(
            strengthening=True,
            weakening=True,
        ),
    )

    assert result["direction"] == "deteriorating"


def test_trend_change_above_threshold_is_improving():
    result = interpret(
        features=make_features(
            trend_change=TrendInterpreter.TREND_CHANGE_THRESHOLD + 0.01,
        ),
        signals=make_signals(
            strengthening=False,
            weakening=False,
        ),
    )

    assert result["direction"] == "improving"


def test_trend_change_below_negative_threshold_is_deteriorating():
    result = interpret(
        features=make_features(
            trend_change=-(TrendInterpreter.TREND_CHANGE_THRESHOLD + 0.01),
        ),
        signals=make_signals(
            strengthening=False,
            weakening=False,
        ),
    )

    assert result["direction"] == "deteriorating"


def test_trend_change_inside_threshold_is_stable():
    result = interpret(
        features=make_features(
            trend_change=0.1,
        ),
        signals=make_signals(
            strengthening=False,
            weakening=False,
        ),
    )

    assert result["direction"] == "stable"


def test_trend_change_exactly_at_positive_threshold_is_stable():
    result = interpret(
        features=make_features(
            trend_change=TrendInterpreter.TREND_CHANGE_THRESHOLD,
        ),
        signals=make_signals(
            strengthening=False,
            weakening=False,
        ),
    )

    assert result["direction"] == "stable"


def test_trend_change_exactly_at_negative_threshold_is_stable():
    result = interpret(
        features=make_features(
            trend_change=-TrendInterpreter.TREND_CHANGE_THRESHOLD,
        ),
        signals=make_signals(
            strengthening=False,
            weakening=False,
        ),
    )

    assert result["direction"] == "stable"


def test_missing_trend_change_creates_unknown_direction():
    result = interpret(
        features=make_features(
            trend_change=None,
        ),
        signals=make_signals(
            strengthening=False,
            weakening=False,
        ),
    )

    assert result["direction"] == "unknown"


# ---------------------------------------------------------------------
# CHANGE STATE
# ---------------------------------------------------------------------


def test_strengthening_signal_creates_strengthening_change_state():
    result = interpret(
        signals=make_signals(
            strengthening=True,
            weakening=False,
        ),
    )

    assert result["change_state"] == "strengthening"


def test_weakening_signal_creates_weakening_change_state():
    result = interpret(
        signals=make_signals(
            strengthening=False,
            weakening=True,
        ),
    )

    assert result["change_state"] == "weakening"


def test_missing_trend_change_creates_unknown_change_state():
    result = interpret(
        features=make_features(
            trend_change=None,
        ),
        signals=make_signals(
            strengthening=False,
            weakening=False,
        ),
    )

    assert result["change_state"] == "unknown"


def test_small_trend_change_creates_stable_change_state():
    result = interpret(
        features=make_features(
            trend_change=0.1,
        ),
        signals=make_signals(
            strengthening=False,
            weakening=False,
        ),
    )

    assert result["change_state"] == "stable"


# ---------------------------------------------------------------------
# STRENGTH
# ---------------------------------------------------------------------


def test_no_slopes_create_unknown_strength():
    result = interpret(
        features=make_features(
            short_slope=None,
            medium_slope=None,
            long_slope=None,
        ),
        signals=make_signals(),
    )

    assert result["strength"] == "unknown"


def test_zero_slopes_create_weak_strength():
    result = interpret(
        features=make_features(
            short_slope=0.0,
            medium_slope=0.0,
            long_slope=0.0,
        ),
        signals=make_signals(
            bullish=False,
            bearish=False,
            mixed=False,
        ),
    )

    assert result["strength"] == "weak"


def test_normal_slopes_create_moderate_strength():
    result = interpret(
        features=make_features(
            short_slope=0.5,
            medium_slope=0.5,
            long_slope=0.5,
            trend_change=0.5,
        ),
    )

    assert result["strength"] == "moderate"


def test_trend_change_above_one_creates_strong_strength():
    result = interpret(
        features=make_features(
            short_slope=0.5,
            medium_slope=0.5,
            long_slope=0.5,
            trend_change=1.01,
        ),
    )

    assert result["strength"] == "strong"


def test_negative_trend_change_above_one_in_absolute_value_creates_strong_strength():
    result = interpret(
        features=make_features(
            short_slope=-0.5,
            medium_slope=-0.5,
            long_slope=-0.5,
            trend_change=-1.01,
        ),
        signals=make_signals(
            bullish=False,
            bearish=True,
        ),
    )

    assert result["strength"] == "strong"


def test_strength_uses_average_absolute_slope():
    result = interpret(
        features=make_features(
            short_slope=0.1,
            medium_slope=0.2,
            long_slope=0.3,
            trend_change=0.5,
        ),
    )

    assert result["strength"] == "moderate"


# ---------------------------------------------------------------------
# REVERSAL
# ---------------------------------------------------------------------


def test_reversal_signal_is_preserved():
    result = interpret(
        signals=make_signals(
            reversal=True,
        ),
    )

    assert result["reversal"] is True


def test_reversal_can_be_false():
    result = interpret(
        signals=make_signals(
            reversal=False,
        ),
    )

    assert result["reversal"] is False


# ---------------------------------------------------------------------
# STATE AND DIRECTION ARE SEMANTICALLY SEPARATED
# ---------------------------------------------------------------------


def test_bullish_trend_can_be_deteriorating():
    result = interpret(
        features=make_features(
            short_slope=1.0,
            medium_slope=1.0,
            long_slope=1.0,
            trend_change=-1.0,
        ),
        signals=make_signals(
            bullish=True,
            bearish=False,
            mixed=False,
            strengthening=False,
            weakening=True,
        ),
    )

    assert result["state"] == "bullish"
    assert result["direction"] == "deteriorating"


def test_bearish_trend_can_be_improving():
    result = interpret(
        features=make_features(
            short_slope=-1.0,
            medium_slope=-1.0,
            long_slope=-1.0,
            trend_change=1.0,
        ),
        signals=make_signals(
            bullish=False,
            bearish=True,
            mixed=False,
            strengthening=True,
            weakening=False,
        ),
    )

    assert result["state"] == "bearish"
    assert result["direction"] == "improving"


# ---------------------------------------------------------------------
# RAW VALUES AND OUTPUT STRUCTURE
# ---------------------------------------------------------------------


def test_raw_metrics_are_returned():
    result = interpret(
        features=make_features(
            short_slope=1.25,
            medium_slope=0.75,
            long_slope=-0.25,
            acceleration=0.33,
            slope_change=-0.12,
            trend_change=0.55,
        ),
    )

    assert result["short_slope"] == 1.25
    assert result["medium_slope"] == 0.75
    assert result["long_slope"] == -0.25
    assert result["acceleration"] == 0.33
    assert result["slope_change"] == -0.12
    assert result["trend_change"] == 0.55


def test_raw_boolean_signals_are_returned():
    result = interpret(
        signals=make_signals(
            bullish=True,
            bearish=False,
            mixed=True,
            reversal=True,
            strengthening=True,
            weakening=False,
        ),
    )

    assert result["bullish"] is True
    assert result["bearish"] is False
    assert result["mixed"] is True
    assert result["reversal"] is True
    assert result["strengthening"] is True
    assert result["weakening"] is False


def test_output_contains_all_expected_fields():
    result = interpret()

    expected_keys = {
        "state",
        "direction",
        "strength",
        "reversal",
        "change_state",
        "short_direction",
        "medium_direction",
        "long_direction",
        "bullish",
        "bearish",
        "mixed",
        "strengthening",
        "weakening",
        "short_slope",
        "medium_slope",
        "long_slope",
        "acceleration",
        "slope_change",
        "trend_change",
    }

    assert set(result) == expected_keys


# ---------------------------------------------------------------------
# PRIORITY / EDGE CASES
# ---------------------------------------------------------------------


def test_strengthening_and_weakening_do_not_override_each_other():
    result = interpret(
        features=make_features(
            trend_change=0.0,
        ),
        signals=make_signals(
            strengthening=True,
            weakening=True,
        ),
    )

    assert result["direction"] == "stable"
    assert result["change_state"] == "stable"


def test_bullish_signal_does_not_override_explicit_mixed_slope_structure():
    result = interpret(
        features=make_features(
            short_slope=1.0,
            medium_slope=-1.0,
            long_slope=1.0,
        ),
        signals=make_signals(
            bullish=True,
            bearish=False,
            mixed=False,
        ),
    )

    assert result["state"] == "mixed"


def test_bearish_signal_does_not_override_explicit_bullish_slope_structure():
    result = interpret(
        features=make_features(
            short_slope=1.0,
            medium_slope=1.0,
            long_slope=1.0,
        ),
        signals=make_signals(
            bullish=False,
            bearish=True,
            mixed=False,
        ),
    )

    assert result["state"] == "bullish"