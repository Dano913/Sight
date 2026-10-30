from __future__ import annotations

from app.services.interpretation.macro.assessment_builder import (
    AssessmentBuilder,
)


def make_growth(
    state="positive",
    direction="improving",
):
    return {
        "state": state,
        "direction": direction,
    }


def make_trend(
    state="bullish",
    direction="improving",
):
    return {
        "state": state,
        "direction": direction,
    }


def make_momentum(
    state="positive",
    direction="improving",
):
    return {
        "state": state,
        "direction": direction,
    }


def make_volatility(
    level="normal",
    direction="stable",
):
    return {
        "level": level,
        "direction": direction,
    }


def make_position(
    position="middle",
    drawdown_state="none",
):
    return {
        "position": position,
        "drawdown_state": drawdown_state,
    }


def make_transition(
    detected=False,
    direction="unknown",
    state="none",
    confidence="low",
):
    return {
        "detected": detected,
        "direction": direction,
        "state": state,
        "confidence": confidence,
    }


def build(
    *,
    growth=None,
    trend=None,
    momentum=None,
    volatility=None,
    position=None,
    transition=None,
    regime="expansion",
):
    return AssessmentBuilder.build(
        growth=growth or make_growth(),
        trend=trend or make_trend(),
        momentum=momentum or make_momentum(),
        volatility=volatility or make_volatility(),
        position=position or make_position(),
        transition=transition or make_transition(),
        regime=regime,
    )


# ---------------------------------------------------------------------
# DIRECTIONAL BIAS
# ---------------------------------------------------------------------


def test_two_improving_dimensions_create_improving_bias():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="improving"),
        momentum=make_momentum(direction="stable"),
    )

    assert result["directional_bias"] == "improving"


def test_two_deteriorating_dimensions_create_deteriorating_bias():
    result = build(
        growth=make_growth(direction="deteriorating"),
        trend=make_trend(direction="deteriorating"),
        momentum=make_momentum(direction="stable"),
    )

    assert result["directional_bias"] == "deteriorating"


def test_two_stable_dimensions_create_stable_bias():
    result = build(
        growth=make_growth(direction="stable"),
        trend=make_trend(direction="stable"),
        momentum=make_momentum(direction="improving"),
    )

    assert result["directional_bias"] == "stable"


def test_improving_and_deteriorating_dimensions_create_mixed_bias():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="deteriorating"),
        momentum=make_momentum(direction="stable"),
    )

    assert result["directional_bias"] == "mixed"


def test_single_improving_dimension_creates_improving_bias():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="unknown"),
        momentum=make_momentum(direction="unknown"),
    )

    assert result["directional_bias"] == "improving"


def test_single_deteriorating_dimension_creates_deteriorating_bias():
    result = build(
        growth=make_growth(direction="deteriorating"),
        trend=make_trend(direction="unknown"),
        momentum=make_momentum(direction="unknown"),
    )

    assert result["directional_bias"] == "deteriorating"


def test_all_unknown_dimensions_create_unknown_bias():
    result = build(
        growth=make_growth(direction="unknown"),
        trend=make_trend(direction="unknown"),
        momentum=make_momentum(direction="unknown"),
    )

    assert result["directional_bias"] == "unknown"


def test_none_dimensions_create_unknown_bias():
    result = build(
        growth=make_growth(direction=None),
        trend=make_trend(direction=None),
        momentum=make_momentum(direction=None),
    )

    assert result["directional_bias"] == "unknown"


# ---------------------------------------------------------------------
# COHERENCE
# ---------------------------------------------------------------------


def test_all_improving_dimensions_create_high_coherence():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="improving"),
        momentum=make_momentum(direction="improving"),
    )

    assert result["coherence"] == "high"


def test_all_deteriorating_dimensions_create_high_coherence():
    result = build(
        growth=make_growth(direction="deteriorating"),
        trend=make_trend(direction="deteriorating"),
        momentum=make_momentum(direction="deteriorating"),
    )

    assert result["coherence"] == "high"


def test_all_stable_dimensions_create_high_coherence():
    result = build(
        growth=make_growth(direction="stable"),
        trend=make_trend(direction="stable"),
        momentum=make_momentum(direction="stable"),
    )

    assert result["coherence"] == "high"


def test_no_known_directions_create_unknown_coherence():
    result = build(
        growth=make_growth(direction="unknown"),
        trend=make_trend(direction="unknown"),
        momentum=make_momentum(direction=None),
    )

    assert result["coherence"] == "unknown"


def test_mixed_improving_and_deteriorating_directions_create_low_coherence():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="deteriorating"),
        momentum=make_momentum(direction="unknown"),
    )

    assert result["coherence"] == "low"


def test_one_known_direction_creates_medium_coherence():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="unknown"),
        momentum=make_momentum(direction="unknown"),
    )

    assert result["coherence"] == "medium"


def test_improving_and_stable_without_deterioration_create_medium_coherence():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="stable"),
        momentum=make_momentum(direction="unknown"),
    )

    assert result["coherence"] == "medium"


# ---------------------------------------------------------------------
# TRANSITION
# ---------------------------------------------------------------------


def test_transition_defaults_to_not_detected():
    result = build(
        transition=make_transition(
            detected=False,
            direction="unknown",
            state="none",
        ),
    )

    assert result["transition_detected"] is False
    assert result["transition_direction"] == "unknown"
    assert result["transition_state"] == "none"


def test_detected_transition_is_preserved():
    result = build(
        transition=make_transition(
            detected=True,
            direction="toward_slowdown",
            state="moderate",
        ),
    )

    assert result["transition_detected"] is True
    assert result["transition_direction"] == "toward_slowdown"
    assert result["transition_state"] == "moderate"


def test_transition_values_are_read_without_reclassification():
    result = build(
        transition=make_transition(
            detected=True,
            direction="mixed",
            state="early",
        ),
    )

    assert result["transition_direction"] == "mixed"
    assert result["transition_state"] == "early"


# ---------------------------------------------------------------------
# REGIME -> ASSESSMENT
# ---------------------------------------------------------------------


def test_expansion_maps_to_expanding():
    result = build(regime="expansion")

    assert result["state"] == "expanding"


def test_late_expansion_maps_to_maturing():
    result = build(regime="late_expansion")

    assert result["state"] == "maturing"


def test_slowdown_maps_to_slowing():
    result = build(regime="slowdown")

    assert result["state"] == "slowing"


def test_stagnation_maps_to_stagnant():
    result = build(regime="stagnation")

    assert result["state"] == "stagnant"


def test_recovery_maps_to_improving():
    result = build(regime="recovery")

    assert result["state"] == "improving"


def test_contraction_maps_to_contracting():
    result = build(regime="contraction")

    assert result["state"] == "contracting"


def test_neutral_maps_to_neutral():
    result = build(regime="neutral")

    assert result["state"] == "neutral"


def test_unknown_regime_maps_to_neutral():
    result = build(regime="unknown_regime")

    assert result["state"] == "neutral"


# ---------------------------------------------------------------------
# REASONS
# ---------------------------------------------------------------------


def test_positive_growth_adds_positive_growth_reason():
    result = build(
        growth=make_growth(
            state="positive",
            direction="stable",
        ),
    )

    assert "positive_growth" in result["reasons"]


def test_negative_growth_adds_negative_growth_reason():
    result = build(
        growth=make_growth(
            state="negative",
            direction="stable",
        ),
    )

    assert "negative_growth" in result["reasons"]


def test_growth_direction_reasons_are_added():
    result = build(
        growth=make_growth(
            state="positive",
            direction="improving",
        ),
    )

    assert "growth_improving" in result["reasons"]


def test_growth_deterioration_reason_is_added():
    result = build(
        growth=make_growth(
            state="positive",
            direction="deteriorating",
        ),
    )

    assert "growth_deteriorating" in result["reasons"]


def test_trend_state_reasons_are_added():
    result = build(
        trend=make_trend(
            state="bullish",
            direction="stable",
        ),
    )

    assert "bullish_trend" in result["reasons"]


def test_bearish_trend_reason_is_added():
    result = build(
        trend=make_trend(
            state="bearish",
            direction="stable",
        ),
    )

    assert "bearish_trend" in result["reasons"]


def test_mixed_trend_reason_is_added():
    result = build(
        trend=make_trend(
            state="mixed",
            direction="stable",
        ),
    )

    assert "mixed_trend" in result["reasons"]


def test_trend_direction_reasons_are_added():
    result = build(
        trend=make_trend(
            state="bullish",
            direction="improving",
        ),
    )

    assert "trend_improving" in result["reasons"]


def test_trend_deterioration_reason_is_added():
    result = build(
        trend=make_trend(
            state="bullish",
            direction="deteriorating",
        ),
    )

    assert "trend_deteriorating" in result["reasons"]


def test_momentum_state_reasons_are_added():
    result = build(
        momentum=make_momentum(
            state="positive",
            direction="stable",
        ),
    )

    assert "positive_momentum" in result["reasons"]


def test_negative_momentum_reason_is_added():
    result = build(
        momentum=make_momentum(
            state="negative",
            direction="stable",
        ),
    )

    assert "negative_momentum" in result["reasons"]


def test_momentum_direction_reasons_are_added():
    result = build(
        momentum=make_momentum(
            state="positive",
            direction="improving",
        ),
    )

    assert "momentum_improving" in result["reasons"]


def test_momentum_deterioration_reason_is_added():
    result = build(
        momentum=make_momentum(
            state="positive",
            direction="deteriorating",
        ),
    )

    assert "momentum_deteriorating" in result["reasons"]


def test_volatility_level_reasons_are_added():
    result = build(
        volatility=make_volatility(
            level="high",
            direction="stable",
        ),
    )

    assert "high_volatility" in result["reasons"]


def test_extreme_volatility_reason_is_added():
    result = build(
        volatility=make_volatility(
            level="extreme",
            direction="stable",
        ),
    )

    assert "extreme_volatility" in result["reasons"]


def test_volatility_direction_reasons_are_added():
    result = build(
        volatility=make_volatility(
            level="normal",
            direction="rising",
        ),
    )

    assert "volatility_rising" in result["reasons"]


def test_falling_volatility_reason_is_added():
    result = build(
        volatility=make_volatility(
            level="normal",
            direction="falling",
        ),
    )

    assert "volatility_falling" in result["reasons"]


def test_significant_drawdown_reason_is_added():
    result = build(
        position=make_position(
            drawdown_state="significant",
        ),
    )

    assert "significant_drawdown" in result["reasons"]


def test_severe_drawdown_reason_is_added():
    result = build(
        position=make_position(
            drawdown_state="severe",
        ),
    )

    assert "severe_drawdown" in result["reasons"]


def test_upper_extreme_position_reason_is_added():
    result = build(
        position=make_position(
            position="upper_extreme",
        ),
    )

    assert "upper_extreme_position" in result["reasons"]


def test_lower_extreme_position_reason_is_added():
    result = build(
        position=make_position(
            position="lower_extreme",
        ),
    )

    assert "lower_extreme_position" in result["reasons"]


def test_detected_transition_adds_transition_reason():
    result = build(
        transition=make_transition(
            detected=True,
            direction="toward_recovery",
            state="moderate",
        ),
    )

    assert "transition_toward_recovery" in result["reasons"]


def test_undetected_transition_does_not_add_transition_reason():
    result = build(
        transition=make_transition(
            detected=False,
            direction="toward_recovery",
            state="moderate",
        ),
    )

    assert not any(
        reason.startswith("transition_")
        for reason in result["reasons"]
    )


# ---------------------------------------------------------------------
# CONFIDENCE
# ---------------------------------------------------------------------


def test_high_coherence_creates_high_confidence():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="improving"),
        momentum=make_momentum(direction="improving"),
        transition=make_transition(
            confidence="low",
        ),
    )

    assert result["coherence"] == "high"
    assert result["confidence"] == "high"


def test_medium_coherence_with_high_transition_confidence_creates_high_confidence():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="stable"),
        momentum=make_momentum(direction="unknown"),
        transition=make_transition(
            confidence="high",
        ),
    )

    assert result["coherence"] == "medium"
    assert result["confidence"] == "high"


def test_medium_coherence_with_medium_transition_confidence_creates_medium_confidence():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="stable"),
        momentum=make_momentum(direction="unknown"),
        transition=make_transition(
            confidence="medium",
        ),
    )

    assert result["coherence"] == "medium"
    assert result["confidence"] == "medium"


def test_medium_coherence_with_low_transition_confidence_creates_medium_confidence():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="stable"),
        momentum=make_momentum(direction="unknown"),
        transition=make_transition(
            confidence="low",
        ),
    )

    assert result["coherence"] == "medium"
    assert result["confidence"] == "medium"


def test_low_coherence_creates_low_confidence_even_with_high_transition_confidence():
    result = build(
        growth=make_growth(direction="improving"),
        trend=make_trend(direction="deteriorating"),
        momentum=make_momentum(direction="unknown"),
        transition=make_transition(
            confidence="high",
        ),
    )

    assert result["coherence"] == "low"
    assert result["confidence"] == "low"


def test_unknown_coherence_creates_low_confidence():
    result = build(
        growth=make_growth(direction="unknown"),
        trend=make_trend(direction="unknown"),
        momentum=make_momentum(direction="unknown"),
        transition=make_transition(
            confidence="high",
        ),
    )

    assert result["coherence"] == "unknown"
    assert result["confidence"] == "low"


# ---------------------------------------------------------------------
# COMPLETE OUTPUT
# ---------------------------------------------------------------------


def test_build_returns_complete_output_structure():
    result = build()

    expected_keys = {
        "state",
        "directional_bias",
        "regime",
        "coherence",
        "transition_detected",
        "transition_direction",
        "transition_state",
        "confidence",
        "reasons",
    }

    assert set(result) == expected_keys


def test_regime_is_preserved_exactly():
    result = build(
        regime="late_expansion",
    )

    assert result["regime"] == "late_expansion"


def test_assessment_does_not_reclassify_dimensions():
    result = build(
        growth=make_growth(
            state="negative",
            direction="improving",
        ),
        trend=make_trend(
            state="bearish",
            direction="improving",
        ),
        momentum=make_momentum(
            state="negative",
            direction="improving",
        ),
        regime="recovery",
    )

    assert result["state"] == "improving"
    assert result["directional_bias"] == "improving"
    assert result["regime"] == "recovery"
    assert result["coherence"] == "high"


def test_build_with_none_inputs_does_not_crash():
    result = AssessmentBuilder.build(
        growth=None,
        trend=None,
        momentum=None,
        volatility=None,
        position=None,
        transition=None,
        regime="neutral",
    )
    assert result["state"] == "neutral"
    assert result["directional_bias"] == "unknown"
    assert result["coherence"] == "unknown"
    assert result["confidence"] == "low"
    assert result["reasons"] == []
