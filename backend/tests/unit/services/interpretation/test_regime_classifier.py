from app.services.interpretation.macro.regime_classifier import (
    RegimeClassifier,
)


def make_growth(state="positive", direction="improving"):
    return {
        "state": state,
        "direction": direction,
    }


def make_trend(state="bullish", direction="improving"):
    return {
        "state": state,
        "direction": direction,
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


def make_transition(
    detected=False,
    direction="unknown",
    state="none",
):
    return {
        "detected": detected,
        "direction": direction,
        "state": state,
    }


def classify(
    *,
    growth=None,
    trend=None,
    momentum=None,
    volatility=None,
    position=None,
    transition=None,
):
    return RegimeClassifier.classify(
        growth=growth if growth is not None else make_growth(),
        trend=trend if trend is not None else make_trend(),
        momentum=momentum
        if momentum is not None
        else make_momentum(),
        volatility=volatility
        if volatility is not None
        else make_volatility(),
        position=position
        if position is not None
        else make_position(),
        transition=transition
        if transition is not None
        else make_transition(),
    )


def test_expansion():
    assert classify() == "expansion"


def test_contraction():
    assert (
        classify(
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
        == "contraction"
    )


def test_contraction_with_negative_growth_and_bearish_trend():
    assert (
        classify(
            growth=make_growth(
                "negative",
                "deteriorating",
            ),
            trend=make_trend(
                "bearish",
                "stable",
            ),
            momentum=make_momentum(
                "neutral",
                "stable",
            ),
        )
        == "contraction"
    )


def test_recovery():
    assert (
        classify(
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
                "stable",
            ),
        )
        == "recovery"
    )


def test_recovery_requires_two_improving_components():
    result = classify(
        growth=make_growth(
            "negative",
            "improving",
        ),
        trend=make_trend(
            "bearish",
            "stable",
        ),
        momentum=make_momentum(
            "negative",
            "stable",
        ),
    )

    assert result != "recovery"


def test_recovery_from_transition():
    assert (
        classify(
            growth=make_growth(
                "negative",
                "stable",
            ),
            trend=make_trend(
                "bearish",
                "stable",
            ),
            momentum=make_momentum(
                "negative",
                "stable",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_recovery",
                state="moderate",
            ),
        )
        == "recovery"
    )


def test_strong_recovery_transition():
    assert (
        classify(
            growth=make_growth(
                "negative",
                "stable",
            ),
            trend=make_trend(
                "bearish",
                "stable",
            ),
            momentum=make_momentum(
                "negative",
                "stable",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_recovery",
                state="strong",
            ),
        )
        == "recovery"
    )


def test_weak_recovery_transition_does_not_create_recovery():
    result = classify(
        growth=make_growth(
            "negative",
            "stable",
        ),
        trend=make_trend(
            "bearish",
            "stable",
        ),
        momentum=make_momentum(
            "negative",
            "stable",
        ),
        transition=make_transition(
            detected=True,
            direction="toward_recovery",
            state="weak",
        ),
    )

    assert result != "recovery"


def test_late_expansion_from_growth_deterioration():
    assert (
        classify(
            growth=make_growth(
                "positive",
                "deteriorating",
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
        == "late_expansion"
    )


def test_late_expansion_from_trend_deterioration():
    assert (
        classify(
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
                "improving",
            ),
        )
        == "late_expansion"
    )


def test_late_expansion_from_momentum_deterioration():
    assert (
        classify(
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
                "deteriorating",
            ),
        )
        == "late_expansion"
    )


def test_late_expansion_from_slowdown_transition():
    assert (
        classify(
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
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="moderate",
            ),
        )
        == "late_expansion"
    )


def test_expansion_requires_positive_growth_trend_and_momentum():
    result = classify(
        growth=make_growth(
            "positive",
            "improving",
        ),
        trend=make_trend(
            "bullish",
            "improving",
        ),
        momentum=make_momentum(
            "neutral",
            "improving",
        ),
    )

    assert result != "expansion"


def test_expansion_allows_stable_direction():
    assert (
        classify(
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
        == "expansion"
    )


def test_expansion_allows_unknown_direction():
    assert (
        classify(
            growth=make_growth(
                "positive",
                "unknown",
            ),
            trend=make_trend(
                "bullish",
                "unknown",
            ),
            momentum=make_momentum(
                "positive",
                "unknown",
            ),
        )
        == "expansion"
    )


def test_slowdown_requires_two_deteriorating_components():
    assert (
        classify(
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
        == "slowdown"
    )


def test_one_deteriorating_component_is_not_slowdown():
    result = classify(
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

    assert result != "slowdown"


def test_slowdown_from_transition_with_current_deterioration():
    assert (
        classify(
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
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="moderate",
            ),
        )
        == "slowdown"
    )


def test_stagnation():
    assert (
        classify(
            growth=make_growth(
                "flat",
                "stable",
            ),
            trend=make_trend(
                "neutral",
                "stable",
            ),
            momentum=make_momentum(
                "neutral",
                "stable",
            ),
        )
        == "stagnation"
    )


def test_stagnation_with_unknown_components():
    assert (
        classify(
            growth=make_growth(
                "unknown",
                "unknown",
            ),
            trend=make_trend(
                "unknown",
                "unknown",
            ),
            momentum=make_momentum(
                "neutral",
                "stable",
            ),
        )
        == "stagnation"
    )


def test_positive_stable_growth_can_contribute_to_stagnation():
    assert (
        classify(
            growth=make_growth(
                "positive",
                "stable",
            ),
            trend=make_trend(
                "neutral",
                "stable",
            ),
            momentum=make_momentum(
                "neutral",
                "stable",
            ),
        )
        == "stagnation"
    )


def test_severe_drawdown_prevents_stagnation():
    assert (
        classify(
            growth=make_growth(
                "flat",
                "stable",
            ),
            trend=make_trend(
                "neutral",
                "stable",
            ),
            momentum=make_momentum(
                "neutral",
                "stable",
            ),
            position=make_position(
                position="lower",
                drawdown_state="severe",
            ),
        )
        == "neutral"
    )


def test_neutral_when_no_regime_rule_matches():
    assert (
        classify(
            growth=make_growth(
                "positive",
                "improving",
            ),
            trend=make_trend(
                "mixed",
                "stable",
            ),
            momentum=make_momentum(
                "positive",
                "stable",
            ),
        )
        == "neutral"
    )


def test_contraction_has_priority_over_recovery():
    assert (
        classify(
            growth=make_growth(
                "negative",
                "deteriorating",
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
        == "contraction"
    )


def test_contraction_has_priority_over_transition_to_recovery():
    assert (
        classify(
            growth=make_growth(
                "negative",
                "deteriorating",
            ),
            trend=make_trend(
                "bearish",
                "stable",
            ),
            momentum=make_momentum(
                "negative",
                "stable",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_recovery",
                state="strong",
            ),
        )
        == "contraction"
    )


def test_late_expansion_has_priority_over_expansion():
    assert (
        classify(
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
        == "late_expansion"
    )


def test_transition_is_ignored_when_not_detected():
    assert (
        classify(
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
            transition=make_transition(
                detected=False,
                direction="toward_slowdown",
                state="strong",
            ),
        )
        == "expansion"
    )


def test_volatility_does_not_directly_determine_regime():
    assert (
        classify(
            volatility=make_volatility(
                level="extreme",
                direction="rising",
            ),
        )
        == "expansion"
    )


def test_position_does_not_directly_determine_regime():
    assert (
        classify(
            position=make_position(
                position="upper_extreme",
                drawdown_state="none",
            ),
        )
        == "expansion"
    )


def test_classify_with_none_inputs_returns_stagnation():
    result = RegimeClassifier.classify(
        growth=None,
        trend=None,
        momentum=None,
        volatility=None,
        position=None,
        transition=None,
    )
    assert result == "stagnation"