from app.services.interpretation.macro.transition_detector import (
    TransitionDetector,
)


def make_growth(state="positive", direction="improving"):
    return {
        "state": state,
        "direction": direction,
    }


def make_trend(
    state="bullish",
    direction="improving",
    reversal=False,
):
    return {
        "state": state,
        "direction": direction,
        "reversal": reversal,
    }


def make_momentum(state="positive", direction="improving"):
    return {
        "state": state,
        "direction": direction,
    }


def make_volatility(level="normal", direction="stable"):
    return {
        "level": level,
        "direction": direction,
    }


def make_position(position="middle", drawdown_state="none"):
    return {
        "position": position,
        "drawdown_state": drawdown_state,
    }


def detect(
    *,
    growth=None,
    trend=None,
    momentum=None,
    volatility=None,
    position=None,
):
    return TransitionDetector.detect(
        growth=(
            growth
            if growth is not None
            else make_growth()
        ),
        trend=(
            trend
            if trend is not None
            else make_trend()
        ),
        momentum=(
            momentum
            if momentum is not None
            else make_momentum()
        ),
        volatility=(
            volatility
            if volatility is not None
            else make_volatility()
        ),
        position=(
            position
            if position is not None
            else make_position()
        ),
    )


# ==========================================================
# NO TRANSITION
# ==========================================================


def test_no_transition_when_no_evidence():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["detected"] is False
    assert result["state"] == "none"
    assert result["direction"] == "unknown"
    assert result["type"] == "none"
    assert result["score"] == 0
    assert result["confidence"] == "low"
    assert result["reasons"] == []
    assert result["evidence"] == []


# ==========================================================
# SLOWDOWN
# ==========================================================


def test_growth_deterioration_detects_slowdown():
    result = detect(
        growth=make_growth(
            "positive",
            "deteriorating",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["detected"] is True
    assert result["state"] == "early"
    assert result["direction"] == "toward_slowdown"
    assert result["type"] == "toward_slowdown"
    assert result["score"] == 2


def test_deteriorating_bullish_trend_detects_slowdown():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "deteriorating",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["direction"] == "toward_slowdown"
    assert result["type"] == "toward_slowdown"
    assert result["score"] == 2


def test_deteriorating_mixed_trend_detects_slowdown():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "mixed",
            "deteriorating",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["direction"] == "toward_slowdown"
    assert result["type"] == "toward_slowdown"


def test_positive_deteriorating_momentum_detects_slowdown():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "deteriorating",
        ),
    )

    assert result["direction"] == "toward_slowdown"
    assert result["type"] == "toward_slowdown"
    assert result["score"] == 2


def test_three_slowdown_components_create_strong_transition():
    result = detect(
        growth=make_growth(
            "positive",
            "deteriorating",
        ),
        trend=make_trend(
            "bullish",
            "deteriorating",
        ),
        momentum=make_momentum(
            "positive",
            "deteriorating",
        ),
    )

    assert result["detected"] is True
    assert result["direction"] == "toward_slowdown"
    assert result["type"] == "toward_slowdown"
    assert result["score"] == 6
    assert result["state"] == "strong"


# ==========================================================
# CONTRACTION
# ==========================================================


def test_negative_deteriorating_growth_detects_contraction():
    result = detect(
        growth=make_growth(
            "negative",
            "deteriorating",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["detected"] is True
    assert result["direction"] == "toward_contraction"
    assert result["type"] == "toward_contraction"
    assert result["score"] == 3
    assert result["state"] == "early"


def test_bearish_deteriorating_trend_detects_contraction():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bearish",
            "deteriorating",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["direction"] == "toward_contraction"
    assert result["type"] == "toward_contraction"
    assert result["score"] == 3


def test_negative_deteriorating_momentum_detects_contraction():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "negative",
            "deteriorating",
        ),
    )

    assert result["direction"] == "toward_contraction"
    assert result["type"] == "toward_contraction"
    assert result["score"] == 3


def test_three_contraction_components_create_strong_transition():
    result = detect(
        growth=make_growth(
            "negative",
            "deteriorating",
        ),
        trend=make_trend(
            "bearish",
            "deteriorating",
        ),
        momentum=make_momentum(
            "negative",
            "deteriorating",
        ),
    )

    assert result["detected"] is True
    assert result["direction"] == "toward_contraction"
    assert result["type"] == "toward_contraction"
    assert result["score"] == 9
    assert result["state"] == "strong"


# ==========================================================
# RECOVERY
# ==========================================================


def test_negative_improving_growth_detects_recovery():
    result = detect(
        growth=make_growth(
            "negative",
            "improving",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["detected"] is True
    assert result["direction"] == "toward_recovery"
    assert result["type"] == "toward_recovery"
    assert result["score"] == 3
    assert result["state"] == "early"


def test_bearish_improving_trend_detects_recovery():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bearish",
            "improving",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["direction"] == "toward_recovery"
    assert result["type"] == "toward_recovery"
    assert result["score"] == 3


def test_negative_improving_momentum_detects_recovery():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "negative",
            "improving",
        ),
    )

    assert result["direction"] == "toward_recovery"
    assert result["type"] == "toward_recovery"
    assert result["score"] == 3


def test_three_recovery_components_create_strong_transition():
    result = detect(
        growth=make_growth(
            "negative",
            "improving",
        ),
        trend=make_trend(
            "bearish",
            "improving",
        ),
        momentum=make_momentum(
            "negative",
            "improving",
        ),
    )

    assert result["detected"] is True
    assert result["direction"] == "toward_recovery"
    assert result["type"] == "toward_recovery"
    assert result["score"] == 9
    assert result["state"] == "strong"


# ==========================================================
# EXPANSION
# ==========================================================


def test_positive_improving_growth_detects_expansion():
    result = detect(
        growth=make_growth(
            "positive",
            "improving",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["detected"] is True
    assert result["direction"] == "toward_expansion"
    assert result["type"] == "toward_expansion"
    assert result["score"] == 3
    assert result["state"] == "early"


def test_bullish_improving_trend_detects_expansion():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "improving",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["direction"] == "toward_expansion"
    assert result["type"] == "toward_expansion"
    assert result["score"] == 3


def test_positive_improving_momentum_detects_expansion():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "improving",
        ),
    )

    assert result["direction"] == "toward_expansion"
    assert result["type"] == "toward_expansion"
    assert result["score"] == 3


def test_three_expansion_components_create_strong_transition():
    result = detect(
        growth=make_growth(
            "positive",
            "improving",
        ),
        trend=make_trend(
            "bullish",
            "improving",
        ),
        momentum=make_momentum(
            "positive",
            "improving",
        ),
    )

    assert result["detected"] is True
    assert result["direction"] == "toward_expansion"
    assert result["type"] == "toward_expansion"
    assert result["score"] == 9
    assert result["state"] == "strong"


# ==========================================================
# STRUCTURAL IMPROVEMENT
# ==========================================================


def test_two_improving_components_add_structural_improvement():
    result = detect(
        growth=make_growth(
            "positive",
            "improving",
        ),
        trend=make_trend(
            "bullish",
            "improving",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    types = [
        item["type"]
        for item in result["evidence"]
    ]

    assert "structural_improvement" in types


def test_three_improving_components_add_structural_improvement_with_weight_three():
    result = detect(
        growth=make_growth(
            "positive",
            "improving",
        ),
        trend=make_trend(
            "bullish",
            "improving",
        ),
        momentum=make_momentum(
            "positive",
            "improving",
        ),
    )

    structural = next(
        item
        for item in result["evidence"]
        if item["type"] == "structural_improvement"
    )

    assert structural["weight"] == 3
    assert (
        structural["reason"]
        == "growth_trend_and_momentum_show_improvement"
    )


# ==========================================================
# STRUCTURAL DETERIORATION
# ==========================================================


def test_two_deteriorating_components_add_structural_deterioration():
    result = detect(
        growth=make_growth(
            "positive",
            "deteriorating",
        ),
        trend=make_trend(
            "bullish",
            "deteriorating",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    types = [
        item["type"]
        for item in result["evidence"]
    ]

    assert "structural_deterioration" in types


def test_three_deteriorating_components_add_structural_deterioration_with_weight_three():
    result = detect(
        growth=make_growth(
            "positive",
            "deteriorating",
        ),
        trend=make_trend(
            "bullish",
            "deteriorating",
        ),
        momentum=make_momentum(
            "positive",
            "deteriorating",
        ),
    )

    structural = next(
        item
        for item in result["evidence"]
        if item["type"] == "structural_deterioration"
    )

    assert structural["weight"] == 3
    assert (
        structural["reason"]
        == "growth_trend_and_momentum_show_deterioration"
    )


# ==========================================================
# REVERSAL
# ==========================================================


def test_improving_trend_reversal_adds_improvement_evidence():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "improving",
            reversal=True,
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    types = [
        item["type"]
        for item in result["evidence"]
    ]

    assert "reversal_toward_improvement" in types


def test_deteriorating_trend_reversal_adds_deterioration_evidence():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "deteriorating",
            reversal=True,
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    types = [
        item["type"]
        for item in result["evidence"]
    ]

    assert "reversal_toward_deterioration" in types


def test_reversal_without_direction_does_not_add_transition_evidence():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "stable",
            reversal=True,
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    types = [
        item["type"]
        for item in result["evidence"]
    ]

    assert "reversal_toward_improvement" not in types
    assert "reversal_toward_deterioration" not in types


# ==========================================================
# MIXED DIRECTIONS
# ==========================================================


def test_balanced_improvement_and_deterioration_is_mixed():
    result = detect(
        growth=make_growth(
            "negative",
            "improving",
        ),
        trend=make_trend(
            "bullish",
            "deteriorating",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["direction"] == "mixed"
    assert result["confidence"] == "low"


def test_mixed_direction_does_not_change_detected_state():
    result = detect(
        growth=make_growth(
            "negative",
            "improving",
        ),
        trend=make_trend(
            "bullish",
            "deteriorating",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    assert result["detected"] is True
    assert result["state"] != "none"


# ==========================================================
# AGGREGATION
# ==========================================================


def test_dominant_transition_determines_direction():
    evidence = [
        {
            "type": "toward_recovery",
            "weight": 3,
            "reason": "recovery_a",
        },
        {
            "type": "toward_recovery",
            "weight": 3,
            "reason": "recovery_b",
        },
        {
            "type": "toward_slowdown",
            "weight": 2,
            "reason": "slowdown",
        },
    ]

    result = TransitionDetector._aggregate_evidence(
        evidence
    )

    assert result["type"] == "toward_recovery"
    assert result["direction"] == "toward_recovery"
    assert result["score"] == 6
    assert result["total_score"] == 8
    assert result["dominant_share"] == 0.75
    assert result["confidence"] == "high"


def test_moderate_state_requires_score_of_four():
    evidence = [
        {
            "type": "toward_recovery",
            "weight": 4,
            "reason": "recovery",
        },
    ]

    result = TransitionDetector._aggregate_evidence(
        evidence
    )

    assert result["state"] == "moderate"


def test_strong_state_requires_score_of_six():
    evidence = [
        {
            "type": "toward_contraction",
            "weight": 6,
            "reason": "contraction",
        },
    ]

    result = TransitionDetector._aggregate_evidence(
        evidence
    )

    assert result["state"] == "strong"


def test_early_state_starts_at_score_two():
    evidence = [
        {
            "type": "toward_slowdown",
            "weight": 2,
            "reason": "slowdown",
        },
    ]

    result = TransitionDetector._aggregate_evidence(
        evidence
    )

    assert result["state"] == "early"


def test_confidence_is_medium_at_fifty_percent():
    evidence = [
        {
            "type": "toward_recovery",
            "weight": 2,
            "reason": "recovery",
        },
        {
            "type": "toward_slowdown",
            "weight": 2,
            "reason": "slowdown",
        },
    ]

    result = TransitionDetector._aggregate_evidence(
        evidence
    )

    assert result["dominant_share"] == 0.5
    assert result["direction"] == "mixed"
    assert result["confidence"] == "low"


def test_confidence_is_low_below_fifty_percent():
    evidence = [
        {
            "type": "toward_recovery",
            "weight": 2,
            "reason": "recovery",
        },
        {
            "type": "toward_slowdown",
            "weight": 3,
            "reason": "slowdown",
        },
    ]

    result = TransitionDetector._aggregate_evidence(
        evidence
    )

    assert result["confidence"] == "low"


# ==========================================================
# CONTEXTUAL INPUTS
# ==========================================================


def test_volatility_alone_does_not_create_transition():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
        volatility=make_volatility(
            "extreme",
            "rising",
        ),
    )

    assert result["detected"] is False
    assert result["direction"] == "unknown"


def test_position_alone_does_not_create_transition():
    result = detect(
        growth=make_growth(
            "positive",
            "stable",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
        position=make_position(
            "upper_extreme",
            "severe",
        ),
    )

    assert result["detected"] is False
    assert result["direction"] == "unknown"


def test_volatility_does_not_change_existing_transition():
    baseline = detect(
        growth=make_growth(
            "positive",
            "deteriorating",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
    )

    with_volatility = detect(
        growth=make_growth(
            "positive",
            "deteriorating",
        ),
        trend=make_trend(
            "bullish",
            "stable",
        ),
        momentum=make_momentum(
            "positive",
            "stable",
        ),
        volatility=make_volatility(
            "extreme",
            "rising",
        ),
    )

    assert (
        with_volatility["direction"]
        == baseline["direction"]
    )
    assert (
        with_volatility["type"]
        == baseline["type"]
    )
    assert (
        with_volatility["score"]
        == baseline["score"]
    )


# ==========================================================
# OUTPUT STRUCTURE
# ==========================================================


def test_detect_returns_complete_output_structure():
    result = detect(
        growth=make_growth(
            "positive",
            "deteriorating",
        ),
    )

    expected_keys = {
        "detected",
        "state",
        "direction",
        "type",
        "score",
        "total_score",
        "dominant_share",
        "confidence",
        "reasons",
        "evidence",
    }

    assert set(result) == expected_keys


def test_reasons_contain_only_dominant_transition_reasons():
    evidence = [
        {
            "type": "toward_recovery",
            "weight": 3,
            "reason": "recovery_one",
        },
        {
            "type": "toward_recovery",
            "weight": 3,
            "reason": "recovery_two",
        },
        {
            "type": "toward_slowdown",
            "weight": 2,
            "reason": "slowdown_one",
        },
    ]

    result = TransitionDetector._aggregate_evidence(
        evidence
    )

    assert result["reasons"] == [
        "recovery_one",
        "recovery_two",
    ]


def test_evidence_preserves_all_original_evidence():
    evidence = [
        {
            "type": "toward_recovery",
            "weight": 3,
            "reason": "recovery",
        },
        {
            "type": "toward_slowdown",
            "weight": 2,
            "reason": "slowdown",
        },
    ]

    result = TransitionDetector._aggregate_evidence(
        evidence
    )

    assert result["evidence"] == evidence


def test_detect_with_none_inputs_does_not_crash():
    result = TransitionDetector.detect(
        growth=None,
        trend=None,
        momentum=None,
        volatility=None,
        position=None,
    )
    assert result["detected"] is False
    assert result["state"] == "none"
    assert result["direction"] == "unknown"
