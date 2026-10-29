from app.services.interpretation.investment.risk_interpreter import (
    RiskInterpreter,
)


def _growth(
    *,
    state: str = "unknown",
    direction: str = "unknown",
) -> dict:
    return {
        "state": state,
        "direction": direction,
    }


def _trend(
    *,
    state: str = "unknown",
    direction: str = "unknown",
    reversal: bool = False,
) -> dict:
    return {
        "state": state,
        "direction": direction,
        "reversal": reversal,
    }


def _momentum(
    *,
    state: str = "unknown",
    direction: str = "unknown",
) -> dict:
    return {
        "state": state,
        "direction": direction,
    }


def _volatility(
    *,
    level: str = "normal",
    direction: str = "stable",
    stress: str = "none",
    shock: bool = False,
) -> dict:
    return {
        "level": level,
        "direction": direction,
        "stress": stress,
        "shock": shock,
    }


def _position(
    *,
    drawdown_state: str = "none",
    direction: str = "stable",
) -> dict:
    return {
        "drawdown_state": drawdown_state,
        "direction": direction,
    }


def _transition(
    *,
    detected: bool = False,
    direction: str = "unknown",
    state: str = "none",
) -> dict:
    return {
        "detected": detected,
        "direction": direction,
        "state": state,
    }


# ---------------------------------------------------------------------------
# interpret
# ---------------------------------------------------------------------------


def test_interpret_returns_complete_structure():
    result = RiskInterpreter.interpret(
        growth=_growth(
            state="negative",
            direction="deteriorating",
        ),
        trend=_trend(
            state="bearish",
            direction="deteriorating",
        ),
        momentum=_momentum(
            state="negative",
            direction="deteriorating",
        ),
        volatility=_volatility(
            shock=True,
        ),
        position=_position(
            drawdown_state="severe",
        ),
        transition=_transition(
            detected=True,
            direction="toward_contraction",
            state="strong",
        ),
        regime="contraction",
    )

    assert result["state"] == "high"

    assert result["dimensions"] == {
        "growth": "negative_growth_deteriorating",
        "trend": "bearish_trend_deteriorating",
        "momentum": "negative_momentum_deteriorating",
        "volatility": "volatility_shock",
        "position": "severe_drawdown",
        "transition": "strong_contraction_transition",
    }

    assert result["regime"] == "contraction"

    assert result["transition"] == {
        "detected": True,
        "direction": "toward_contraction",
        "state": "strong",
    }

    assert result["reasons"] == [
        "negative_growth_deteriorating",
        "bearish_trend_deteriorating",
        "negative_momentum_deteriorating",
        "volatility_shock",
        "severe_drawdown",
        "strong_contraction_transition",
        "contraction_regime",
    ]


def test_interpret_uses_defaults_for_empty_inputs():
    result = RiskInterpreter.interpret(
        growth={},
        trend={},
        momentum={},
        volatility={},
        position={},
        transition={},
        regime="expansion",
    )

    assert result["state"] == "low"

    assert result["dimensions"] == {
        "growth": None,
        "trend": None,
        "momentum": None,
        "volatility": None,
        "position": None,
        "transition": None,
    }

    assert result["regime"] == "expansion"

    assert result["transition"] == {
        "detected": False,
        "direction": "unknown",
        "state": "none",
    }

    assert result["reasons"] == []


# ---------------------------------------------------------------------------
# _growth_risk
# ---------------------------------------------------------------------------


def test_growth_risk_negative_and_deteriorating():
    result = RiskInterpreter._growth_risk(
        growth=_growth(
            state="negative",
            direction="deteriorating",
        )
    )

    assert result == "negative_growth_deteriorating"


def test_growth_risk_negative_and_stable():
    result = RiskInterpreter._growth_risk(
        growth=_growth(
            state="negative",
            direction="stable",
        )
    )

    assert result == "negative_growth"


def test_growth_risk_negative_and_unknown_direction():
    result = RiskInterpreter._growth_risk(
        growth=_growth(
            state="negative",
            direction="unknown",
        )
    )

    assert result == "negative_growth"


def test_growth_risk_positive_and_deteriorating():
    result = RiskInterpreter._growth_risk(
        growth=_growth(
            state="positive",
            direction="deteriorating",
        )
    )

    assert result == "growth_deteriorating"


def test_growth_risk_flat():
    result = RiskInterpreter._growth_risk(
        growth=_growth(
            state="flat",
            direction="stable",
        )
    )

    assert result == "flat_growth"


def test_growth_risk_returns_none_for_non_risk_growth():
    result = RiskInterpreter._growth_risk(
        growth=_growth(
            state="positive",
            direction="improving",
        )
    )

    assert result is None


# ---------------------------------------------------------------------------
# _trend_risk
# ---------------------------------------------------------------------------


def test_trend_risk_bearish_and_deteriorating():
    result = RiskInterpreter._trend_risk(
        trend=_trend(
            state="bearish",
            direction="deteriorating",
        )
    )

    assert result == "bearish_trend_deteriorating"


def test_trend_risk_bearish_and_stable():
    result = RiskInterpreter._trend_risk(
        trend=_trend(
            state="bearish",
            direction="stable",
        )
    )

    assert result == "bearish_trend"


def test_trend_risk_bearish_and_unknown_direction():
    result = RiskInterpreter._trend_risk(
        trend=_trend(
            state="bearish",
            direction="unknown",
        )
    )

    assert result == "bearish_trend"


def test_trend_risk_bullish_and_deteriorating():
    result = RiskInterpreter._trend_risk(
        trend=_trend(
            state="bullish",
            direction="deteriorating",
        )
    )

    assert result == "bullish_trend_deteriorating"


def test_trend_risk_bullish_reversing():
    result = RiskInterpreter._trend_risk(
        trend=_trend(
            state="bullish",
            direction="deteriorating",
            reversal=True,
        )
    )

    assert result == "bullish_trend_reversing"


def test_trend_risk_mixed_and_deteriorating():
    result = RiskInterpreter._trend_risk(
        trend=_trend(
            state="mixed",
            direction="deteriorating",
        )
    )

    assert result == "mixed_trend_deteriorating"


def test_trend_risk_returns_none_for_non_risk_trend():
    result = RiskInterpreter._trend_risk(
        trend=_trend(
            state="bullish",
            direction="strengthening",
        )
    )

    assert result is None


# ---------------------------------------------------------------------------
# _momentum_risk
# ---------------------------------------------------------------------------


def test_momentum_risk_negative_and_deteriorating():
    result = RiskInterpreter._momentum_risk(
        momentum=_momentum(
            state="negative",
            direction="deteriorating",
        )
    )

    assert result == "negative_momentum_deteriorating"


def test_momentum_risk_negative_and_stable():
    result = RiskInterpreter._momentum_risk(
        momentum=_momentum(
            state="negative",
            direction="stable",
        )
    )

    assert result == "negative_momentum"


def test_momentum_risk_negative_and_unknown():
    result = RiskInterpreter._momentum_risk(
        momentum=_momentum(
            state="negative",
            direction="unknown",
        )
    )

    assert result == "negative_momentum"


def test_momentum_risk_positive_and_deteriorating():
    result = RiskInterpreter._momentum_risk(
        momentum=_momentum(
            state="positive",
            direction="deteriorating",
        )
    )

    assert result == "positive_momentum_deteriorating"


def test_momentum_risk_returns_none_for_improving_momentum():
    result = RiskInterpreter._momentum_risk(
        momentum=_momentum(
            state="positive",
            direction="improving",
        )
    )

    assert result is None


# ---------------------------------------------------------------------------
# _volatility_risk
# ---------------------------------------------------------------------------


def test_volatility_risk_shock_has_highest_priority():
    result = RiskInterpreter._volatility_risk(
        volatility=_volatility(
            level="extreme",
            direction="rising",
            stress="extreme",
            shock=True,
        )
    )

    assert result == "volatility_shock"


def test_volatility_risk_extreme_stress():
    result = RiskInterpreter._volatility_risk(
        volatility=_volatility(
            stress="extreme",
        )
    )

    assert result == "extreme_volatility_stress"


def test_volatility_risk_elevated_stress_rising():
    result = RiskInterpreter._volatility_risk(
        volatility=_volatility(
            direction="rising",
            stress="elevated",
        )
    )

    assert result == "elevated_volatility_stress_rising"


def test_volatility_risk_elevated_stress_not_rising():
    result = RiskInterpreter._volatility_risk(
        volatility=_volatility(
            direction="stable",
            stress="elevated",
        )
    )

    assert result == "elevated_volatility_stress"


def test_volatility_risk_extreme_level_and_rising():
    result = RiskInterpreter._volatility_risk(
        volatility=_volatility(
            level="extreme",
            direction="rising",
            stress="none",
        )
    )

    assert result == "extreme_volatility_rising"


def test_volatility_risk_high_level_and_rising():
    result = RiskInterpreter._volatility_risk(
        volatility=_volatility(
            level="high",
            direction="rising",
            stress="none",
        )
    )

    assert result == "high_volatility_rising"


def test_volatility_risk_high_level_stable():
    result = RiskInterpreter._volatility_risk(
        volatility=_volatility(
            level="high",
            direction="stable",
            stress="none",
        )
    )

    assert result == "high_volatility"


def test_volatility_risk_returns_none_for_normal_volatility():
    result = RiskInterpreter._volatility_risk(
        volatility=_volatility()
    )

    assert result is None


# ---------------------------------------------------------------------------
# _position_risk
# ---------------------------------------------------------------------------


def test_position_risk_severe_drawdown():
    result = RiskInterpreter._position_risk(
        position=_position(
            drawdown_state="severe",
        )
    )

    assert result == "severe_drawdown"


def test_position_risk_significant_drawdown():
    result = RiskInterpreter._position_risk(
        position=_position(
            drawdown_state="significant",
        )
    )

    assert result == "significant_drawdown"


def test_position_risk_minor_drawdown_falling():
    result = RiskInterpreter._position_risk(
        position=_position(
            drawdown_state="minor",
            direction="falling",
        )
    )

    assert result == "drawdown_falling"


def test_position_risk_minor_drawdown_not_falling():
    result = RiskInterpreter._position_risk(
        position=_position(
            drawdown_state="minor",
            direction="stable",
        )
    )

    assert result is None


def test_position_risk_no_drawdown():
    result = RiskInterpreter._position_risk(
        position=_position()
    )

    assert result is None


# ---------------------------------------------------------------------------
# _transition_risk
# ---------------------------------------------------------------------------


def test_transition_risk_returns_none_when_not_detected():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=False,
            direction="toward_contraction",
            state="strong",
        )
    )

    assert result is None


def test_transition_risk_strong_contraction():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="toward_contraction",
            state="strong",
        )
    )

    assert result == "strong_contraction_transition"


def test_transition_risk_moderate_contraction():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="toward_contraction",
            state="moderate",
        )
    )

    assert result == "contraction_transition"


def test_transition_risk_weak_contraction():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="toward_contraction",
            state="weak",
        )
    )

    assert result == "contraction_transition"


def test_transition_risk_strong_slowdown():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="toward_slowdown",
            state="strong",
        )
    )

    assert result == "strong_slowdown_transition"


def test_transition_risk_moderate_slowdown():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="toward_slowdown",
            state="moderate",
        )
    )

    assert result == "slowdown_transition"


def test_transition_risk_strong_deterioration():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="toward_deterioration",
            state="strong",
        )
    )

    assert result == "strong_deterioration_transition"


def test_transition_risk_moderate_deterioration():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="toward_deterioration",
            state="moderate",
        )
    )

    assert result == "deterioration_transition"


def test_transition_risk_mixed():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="mixed",
            state="moderate",
        )
    )

    assert result == "mixed_transition"


def test_transition_toward_recovery_is_not_risk():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="toward_recovery",
            state="strong",
        )
    )

    assert result is None


def test_transition_toward_expansion_is_not_risk():
    result = RiskInterpreter._transition_risk(
        transition=_transition(
            detected=True,
            direction="toward_expansion",
            state="strong",
        )
    )

    assert result is None


# ---------------------------------------------------------------------------
# _regime_context
# ---------------------------------------------------------------------------


def test_regime_context_contraction():
    assert (
        RiskInterpreter._regime_context(regime="contraction")
        == "contraction_regime"
    )


def test_regime_context_slowdown():
    assert (
        RiskInterpreter._regime_context(regime="slowdown")
        == "slowdown_regime"
    )


def test_regime_context_stagnation():
    assert (
        RiskInterpreter._regime_context(regime="stagnation")
        == "stagnation_regime"
    )


def test_regime_context_non_risk_regime_returns_none():
    assert RiskInterpreter._regime_context(regime="expansion") is None
    assert RiskInterpreter._regime_context(regime="recovery") is None


# ---------------------------------------------------------------------------
# _classify_state - high
# ---------------------------------------------------------------------------


def test_classify_state_high_for_severe_growth_risk():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["negative_growth_deteriorating"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "high"


def test_classify_state_high_for_severe_trend_risk():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["bearish_trend_deteriorating"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "high"


def test_classify_state_high_for_severe_momentum_risk():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["negative_momentum_deteriorating"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "high"


def test_classify_state_high_for_extreme_volatility_stress():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["extreme_volatility_stress"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "high"


def test_classify_state_high_for_volatility_shock():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["volatility_shock"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "high"


def test_classify_state_high_for_severe_drawdown():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["severe_drawdown"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "high"


def test_classify_state_high_for_strong_contraction_transition():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["strong_contraction_transition"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "high"


def test_classify_state_contraction_with_moderate_risk_is_high():
    result = RiskInterpreter._classify_state(
        regime="contraction",
        risk_dimensions=["negative_growth"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "moderate"


def test_classify_state_contraction_with_severe_risk_is_high():
    result = RiskInterpreter._classify_state(
        regime="contraction",
        risk_dimensions=["negative_growth_deteriorating"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "high"


# ---------------------------------------------------------------------------
# _classify_state - elevated
# ---------------------------------------------------------------------------


def test_classify_state_elevated_with_two_moderate_conditions():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=[
            "negative_growth",
            "bearish_trend",
        ],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "elevated"


def test_classify_state_elevated_with_three_moderate_conditions():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=[
            "negative_growth",
            "bearish_trend",
            "negative_momentum",
        ],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "elevated"


def test_classify_state_single_moderate_condition_is_not_elevated():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["negative_growth"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "moderate"


# ---------------------------------------------------------------------------
# _classify_state - moderate
# ---------------------------------------------------------------------------


def test_classify_state_moderate_with_single_moderate_condition():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["growth_deteriorating"],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "moderate"


def test_classify_state_slowdown_is_moderate_without_dimensions():
    result = RiskInterpreter._classify_state(
        regime="slowdown",
        risk_dimensions=[],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "moderate"


def test_classify_state_stagnation_is_moderate_without_dimensions():
    result = RiskInterpreter._classify_state(
        regime="stagnation",
        risk_dimensions=[],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "moderate"


def test_classify_state_toward_deterioration_is_moderate():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=[],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(
            direction="toward_deterioration",
        ),
    )

    assert result == "moderate"


def test_classify_state_toward_deterioration_does_not_require_detected_flag():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=[],
        volatility=_volatility(),
        position=_position(),
        transition={
            "detected": False,
            "direction": "toward_deterioration",
            "state": "none",
        },
    )

    assert result == "moderate"


# ---------------------------------------------------------------------------
# _classify_state - low
# ---------------------------------------------------------------------------


def test_classify_state_low_without_risk_evidence():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=[],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "low"


def test_classify_state_ignores_unknown_dimensions():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=[
            "unknown_condition",
            "some_other_condition",
        ],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "low"


# ---------------------------------------------------------------------------
# Precedence
# ---------------------------------------------------------------------------


def test_high_takes_precedence_over_elevated():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=[
            "negative_growth",
            "bearish_trend",
            "volatility_shock",
        ],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
    )

    assert result == "high"


def test_elevated_takes_precedence_over_moderate():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=[
            "negative_growth",
            "bearish_trend",
        ],
        volatility=_volatility(),
        position=_position(),
        transition=_transition(
            direction="toward_deterioration",
        ),
    )

    assert result == "elevated"


def test_severe_drawdown_alone_is_high():
    result = RiskInterpreter._classify_state(
        regime="expansion",
        risk_dimensions=["severe_drawdown"],
        volatility=_volatility(),
        position=_position(
            drawdown_state="severe",
        ),
        transition=_transition(),
    )

    assert result == "high"


# ---------------------------------------------------------------------------
# Semantic invariants
# ---------------------------------------------------------------------------


def test_recovery_transition_does_not_create_risk():
    result = RiskInterpreter.interpret(
        growth=_growth(
            state="positive",
            direction="improving",
        ),
        trend=_trend(
            state="bullish",
            direction="strengthening",
        ),
        momentum=_momentum(
            state="positive",
            direction="improving",
        ),
        volatility=_volatility(),
        position=_position(),
        transition=_transition(
            detected=True,
            direction="toward_recovery",
            state="strong",
        ),
        regime="recovery",
    )

    assert result["dimensions"]["transition"] is None
    assert result["state"] == "low"


def test_expansion_transition_does_not_create_risk():
    result = RiskInterpreter.interpret(
        growth=_growth(
            state="positive",
            direction="improving",
        ),
        trend=_trend(
            state="bullish",
            direction="strengthening",
        ),
        momentum=_momentum(
            state="positive",
            direction="improving",
        ),
        volatility=_volatility(),
        position=_position(),
        transition=_transition(
            detected=True,
            direction="toward_expansion",
            state="strong",
        ),
        regime="expansion",
    )

    assert result["dimensions"]["transition"] is None
    assert result["state"] == "low"


def test_mixed_transition_is_risk_context_but_not_high_by_itself():
    result = RiskInterpreter.interpret(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        position=_position(),
        transition=_transition(
            detected=True,
            direction="mixed",
            state="moderate",
        ),
        regime="expansion",
    )

    assert result["dimensions"]["transition"] == "mixed_transition"
    assert result["state"] == "low"


def test_position_risk_is_not_based_on_low_position_alone():
    result = RiskInterpreter.interpret(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        position={
            "position": "lower",
            "direction": "stable",
            "drawdown_state": "none",
        },
        transition=_transition(),
        regime="expansion",
    )

    assert result["dimensions"]["position"] is None
    assert result["state"] == "low"


def test_minor_drawdown_only_when_falling_creates_moderate_risk():
    result = RiskInterpreter.interpret(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        position=_position(
            drawdown_state="minor",
            direction="falling",
        ),
        transition=_transition(),
        regime="expansion",
    )

    assert result["dimensions"]["position"] == "drawdown_falling"
    assert result["state"] == "moderate"


def test_two_independent_moderate_risks_create_elevated_state():
    result = RiskInterpreter.interpret(
        growth=_growth(
            state="negative",
            direction="stable",
        ),
        trend=_trend(
            state="bearish",
            direction="stable",
        ),
        momentum=_momentum(),
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
        regime="expansion",
    )

    assert result["dimensions"]["growth"] == "negative_growth"
    assert result["dimensions"]["trend"] == "bearish_trend"
    assert result["state"] == "elevated"