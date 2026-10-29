import pandas as pd

from app.services.interpretation.macro.position_interpreter import (
    PositionInterpreter,
)


def make_features(
    percentile=0.50,
    rolling_percentile=0.50,
    zscore=0.0,
    distance_from_rolling_mean=0.0,
    distance_from_max=0.0,
    distance_from_min=0.0,
    drawdown=0.0,
):
    return pd.Series(
        {
            "percentile": percentile,
            "rolling_percentile": rolling_percentile,
            "zscore": zscore,
            "distance_from_rolling_mean": distance_from_rolling_mean,
            "distance_from_max": distance_from_max,
            "distance_from_min": distance_from_min,
            "drawdown": drawdown,
        }
    )


def make_signals(
    near_historical_high=False,
    near_historical_low=False,
    significant_drawdown=False,
    severe_drawdown=False,
    historical_extreme_high=False,
    historical_extreme_low=False,
    recovering_from_drawdown=False,
    falling_from_high=False,
):
    return pd.Series(
        {
            "near_historical_high": near_historical_high,
            "near_historical_low": near_historical_low,
            "significant_drawdown": significant_drawdown,
            "severe_drawdown": severe_drawdown,
            "historical_extreme_high": historical_extreme_high,
            "historical_extreme_low": historical_extreme_low,
            "recovering_from_drawdown": recovering_from_drawdown,
            "falling_from_high": falling_from_high,
        }
    )


def test_middle_position():
    result = PositionInterpreter.interpret(
        make_features(
            percentile=0.50,
            distance_from_rolling_mean=0.0,
            drawdown=0.0,
        ),
        make_signals(),
    )

    assert result["position"] == "middle"
    assert result["mean_position"] == "at_mean"
    assert result["drawdown_state"] == "none"
    assert result["direction"] == "stable"
    assert result["extreme"] == "none"
    assert result["state"] == "normal"


def test_upper_position():
    result = PositionInterpreter.interpret(
        make_features(percentile=0.80),
        make_signals(),
    )

    assert result["position"] == "upper"
    assert result["state"] == "upper"


def test_lower_position():
    result = PositionInterpreter.interpret(
        make_features(percentile=0.20),
        make_signals(),
    )

    assert result["position"] == "lower"
    assert result["state"] == "lower"


def test_upper_extreme_position():
    result = PositionInterpreter.interpret(
        make_features(percentile=0.95),
        make_signals(),
    )

    assert result["position"] == "upper_extreme"
    assert result["state"] == "upper_extreme"


def test_lower_extreme_position():
    result = PositionInterpreter.interpret(
        make_features(percentile=0.05),
        make_signals(),
    )

    assert result["position"] == "lower_extreme"
    assert result["state"] == "lower_extreme"


def test_historical_extreme_high_overrides_percentile():
    result = PositionInterpreter.interpret(
        make_features(percentile=0.60),
        make_signals(historical_extreme_high=True),
    )

    assert result["position"] == "upper_extreme"
    assert result["extreme"] == "high"
    assert result["state"] == "historical_high"


def test_historical_extreme_low_overrides_percentile():
    result = PositionInterpreter.interpret(
        make_features(percentile=0.40),
        make_signals(historical_extreme_low=True),
    )

    assert result["position"] == "lower_extreme"
    assert result["extreme"] == "low"
    assert result["state"] == "historical_low"


def test_near_high_classifies_upper():
    result = PositionInterpreter.interpret(
        make_features(percentile=0.60),
        make_signals(near_historical_high=True),
    )

    assert result["position"] == "upper"


def test_near_low_classifies_lower():
    result = PositionInterpreter.interpret(
        make_features(percentile=0.40),
        make_signals(near_historical_low=True),
    )

    assert result["position"] == "lower"


def test_mean_position_well_above_mean():
    result = PositionInterpreter.interpret(
        make_features(distance_from_rolling_mean=0.10),
        make_signals(),
    )

    assert result["mean_position"] == "well_above_mean"


def test_mean_position_above_mean():
    result = PositionInterpreter.interpret(
        make_features(distance_from_rolling_mean=0.02),
        make_signals(),
    )

    assert result["mean_position"] == "above_mean"


def test_mean_position_at_mean():
    result = PositionInterpreter.interpret(
        make_features(distance_from_rolling_mean=0.0),
        make_signals(),
    )

    assert result["mean_position"] == "at_mean"


def test_mean_position_below_mean():
    result = PositionInterpreter.interpret(
        make_features(distance_from_rolling_mean=-0.02),
        make_signals(),
    )

    assert result["mean_position"] == "below_mean"


def test_mean_position_well_below_mean():
    result = PositionInterpreter.interpret(
        make_features(distance_from_rolling_mean=-0.10),
        make_signals(),
    )

    assert result["mean_position"] == "well_below_mean"


def test_no_drawdown():
    result = PositionInterpreter.interpret(
        make_features(drawdown=0.0),
        make_signals(),
    )

    assert result["drawdown_state"] == "none"


def test_minor_drawdown():
    result = PositionInterpreter.interpret(
        make_features(drawdown=-0.05),
        make_signals(),
    )

    assert result["drawdown_state"] == "minor"


def test_significant_drawdown_from_value():
    result = PositionInterpreter.interpret(
        make_features(drawdown=-0.15),
        make_signals(),
    )

    assert result["drawdown_state"] == "significant"
    assert result["state"] == "drawdown"


def test_significant_drawdown_from_signal():
    result = PositionInterpreter.interpret(
        make_features(drawdown=-0.05),
        make_signals(significant_drawdown=True),
    )

    assert result["drawdown_state"] == "significant"
    assert result["state"] == "drawdown"


def test_severe_drawdown():
    result = PositionInterpreter.interpret(
        make_features(drawdown=-0.30),
        make_signals(severe_drawdown=True),
    )

    assert result["drawdown_state"] == "severe"
    assert result["state"] == "severe_drawdown"


def test_severe_drawdown_has_priority_over_significant_drawdown():
    result = PositionInterpreter.interpret(
        make_features(drawdown=-0.20),
        make_signals(
            significant_drawdown=True,
            severe_drawdown=True,
        ),
    )

    assert result["drawdown_state"] == "severe"


def test_recovering_direction():
    result = PositionInterpreter.interpret(
        make_features(),
        make_signals(recovering_from_drawdown=True),
    )

    assert result["direction"] == "recovering"


def test_falling_direction():
    result = PositionInterpreter.interpret(
        make_features(),
        make_signals(falling_from_high=True),
    )

    assert result["direction"] == "falling"


def test_mixed_direction():
    result = PositionInterpreter.interpret(
        make_features(),
        make_signals(
            recovering_from_drawdown=True,
            falling_from_high=True,
        ),
    )

    assert result["direction"] == "mixed"


def test_stable_direction():
    result = PositionInterpreter.interpret(
        make_features(),
        make_signals(),
    )

    assert result["direction"] == "stable"


def test_extreme_high():
    result = PositionInterpreter.interpret(
        make_features(),
        make_signals(historical_extreme_high=True),
    )

    assert result["extreme"] == "high"


def test_extreme_low():
    result = PositionInterpreter.interpret(
        make_features(),
        make_signals(historical_extreme_low=True),
    )

    assert result["extreme"] == "low"


def test_mixed_extreme():
    result = PositionInterpreter.interpret(
        make_features(),
        make_signals(
            historical_extreme_high=True,
            historical_extreme_low=True,
        ),
    )

    assert result["extreme"] == "mixed"


def test_drawdown_state_has_priority_over_historical_position():
    result = PositionInterpreter.interpret(
        make_features(
            percentile=0.95,
            drawdown=-0.20,
        ),
        make_signals(
            historical_extreme_high=True,
            significant_drawdown=True,
        ),
    )

    assert result["position"] == "upper_extreme"
    assert result["extreme"] == "high"
    assert result["drawdown_state"] == "significant"
    assert result["state"] == "drawdown"


def test_severe_drawdown_has_priority_over_everything():
    result = PositionInterpreter.interpret(
        make_features(
            percentile=0.95,
            drawdown=-0.30,
        ),
        make_signals(
            historical_extreme_high=True,
            severe_drawdown=True,
        ),
    )

    assert result["state"] == "severe_drawdown"


def test_historical_high_state_has_priority_over_upper_position():
    result = PositionInterpreter.interpret(
        make_features(percentile=0.80),
        make_signals(historical_extreme_high=True),
    )

    assert result["position"] == "upper_extreme"
    assert result["extreme"] == "high"
    assert result["state"] == "historical_high"


def test_missing_percentile_produces_unknown_position():
    result = PositionInterpreter.interpret(
        make_features(percentile=float("nan")),
        make_signals(),
    )

    assert result["position"] == "unknown"
    assert result["state"] == "unknown"


def test_missing_mean_distance_produces_unknown_mean_position():
    result = PositionInterpreter.interpret(
        make_features(distance_from_rolling_mean=float("nan")),
        make_signals(),
    )

    assert result["mean_position"] == "unknown"


def test_missing_drawdown_produces_unknown_drawdown_state():
    result = PositionInterpreter.interpret(
        make_features(drawdown=float("nan")),
        make_signals(),
    )

    assert result["drawdown_state"] == "unknown"


def test_output_contains_expected_fields():
    result = PositionInterpreter.interpret(
        make_features(),
        make_signals(),
    )

    assert set(result) == {
        "state",
        "position",
        "mean_position",
        "drawdown_state",
        "direction",
        "extreme",
        "near_high",
        "near_low",
        "historical_extreme_high",
        "historical_extreme_low",
        "significant_drawdown",
        "severe_drawdown",
        "recovering_from_drawdown",
        "falling_from_high",
        "zscore",
        "percentile",
        "rolling_percentile",
        "distance_from_mean",
        "distance_from_max",
        "distance_from_min",
        "drawdown",
    }


def test_signal_flags_are_preserved():
    result = PositionInterpreter.interpret(
        make_features(),
        make_signals(
            near_historical_high=True,
            near_historical_low=True,
            significant_drawdown=True,
            severe_drawdown=True,
            historical_extreme_high=True,
            historical_extreme_low=True,
            recovering_from_drawdown=True,
            falling_from_high=True,
        ),
    )

    assert result["near_high"] is True
    assert result["near_low"] is True
    assert result["significant_drawdown"] is True
    assert result["severe_drawdown"] is True
    assert result["historical_extreme_high"] is True
    assert result["historical_extreme_low"] is True
    assert result["recovering_from_drawdown"] is True
    assert result["falling_from_high"] is True


def test_numeric_features_are_serialized_and_preserved():
    result = PositionInterpreter.interpret(
        make_features(
            percentile=0.75,
            rolling_percentile=0.70,
            zscore=1.5,
            distance_from_rolling_mean=0.06,
            distance_from_max=-0.10,
            distance_from_min=0.50,
            drawdown=-0.10,
        ),
        make_signals(),
    )

    assert result["zscore"] == 1.5
    assert result["percentile"] == 0.75
    assert result["rolling_percentile"] == 0.70
    assert result["distance_from_mean"] == 0.06
    assert result["distance_from_max"] == -0.10
    assert result["distance_from_min"] == 0.50
    assert result["drawdown"] == -0.10