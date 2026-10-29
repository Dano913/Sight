from app.services.interpretation.investment.opportunity_interpreter import (
    OpportunityInterpreter,
)


def _growth(
    *,
    state: str = "unknown",
    direction: str = "unknown",
    dynamic_state: str = "unknown",
) -> dict:
    return {
        "state": state,
        "direction": direction,
        "dynamic_state": dynamic_state,
    }


def _trend(
    *,
    state: str = "unknown",
    direction: str = "unknown",
    strength: str = "unknown",
) -> dict:
    return {
        "state": state,
        "direction": direction,
        "strength": strength,
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
    position: str = "normal",
    direction: str = "stable",
    drawdown_state: str = "none",
    extreme: str = "none",
) -> dict:
    return {
        "position": position,
        "direction": direction,
        "drawdown_state": drawdown_state,
        "extreme": extreme,
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
    result = OpportunityInterpreter.interpret(
        growth=_growth(
            state="positive",
            direction="improving",
            dynamic_state="accelerating",
        ),
        trend=_trend(
            state="bullish",
            direction="strengthening",
            strength="strong",
        ),
        momentum=_momentum(
            state="positive",
            direction="improving",
        ),
        volatility=_volatility(
            level="normal",
            direction="falling",
            stress="none",
            shock=False,
        ),
        position=_position(),
        transition=_transition(
            detected=True,
            direction="toward_expansion",
            state="strong",
        ),
        regime="expansion",
    )

    assert result["state"] == "established"
    assert result["regime"] == "expansion"

    assert result["transition"] == {
        "detected": True,
        "direction": "toward_expansion",
        "state": "strong",
    }

    assert result["context"]["volatility"] == {
        "level": "normal",
        "direction": "falling",
        "stress": "none",
        "shock": False,
    }

    assert result["context"]["position"] == {
        "position": "normal",
        "direction": "stable",
        "drawdown_state": "none",
        "extreme": "none",
    }

    assert "evidence" in result
    assert "reasons" in result
    assert result["evidence"]
    assert result["reasons"]


def test_interpret_uses_defaults_for_missing_context():
    result = OpportunityInterpreter.interpret(
        growth={},
        trend={},
        momentum={},
        volatility={},
        position={},
        transition={},
        regime="stagnation",
    )

    assert result["state"] == "limited"

    assert result["transition"] == {
        "detected": False,
        "direction": "unknown",
        "state": "none",
    }

    assert result["context"]["volatility"] == {
        "level": "unknown",
        "direction": "unknown",
        "stress": "unknown",
        "shock": False,
    }

    assert result["context"]["position"] == {
        "position": "unknown",
        "direction": "unknown",
        "drawdown_state": "unknown",
        "extreme": "none",
    }

    assert result["evidence"] == []
    assert result["reasons"] == []


# ---------------------------------------------------------------------------
# _add_growth_evidence
# ---------------------------------------------------------------------------


def test_add_growth_evidence_positive_and_improving():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_growth_evidence(
        growth=_growth(
            state="positive",
            direction="improving",
            dynamic_state="stable",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["positive_growth_improving"]
    assert evidence == [
        {
            "type": "growth",
            "signal": "positive_growth_improving",
            "meaning": "positive growth with improving direction",
        }
    ]


def test_add_growth_evidence_positive_and_accelerating():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_growth_evidence(
        growth=_growth(
            state="positive",
            direction="stable",
            dynamic_state="accelerating",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["positive_growth_accelerating"]
    assert evidence == [
        {
            "type": "growth",
            "signal": "positive_growth_accelerating",
            "meaning": "positive growth with accelerating dynamics",
        }
    ]


def test_add_growth_evidence_negative_but_improving():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_growth_evidence(
        growth=_growth(
            state="negative",
            direction="improving",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["negative_growth_improving"]
    assert evidence == [
        {
            "type": "growth",
            "signal": "negative_growth_improving",
            "meaning": "negative growth but improving direction",
        }
    ]


def test_add_growth_evidence_ignores_non_opportunity_growth():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_growth_evidence(
        growth=_growth(
            state="negative",
            direction="deteriorating",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == []


# ---------------------------------------------------------------------------
# _add_trend_evidence
# ---------------------------------------------------------------------------


def test_add_trend_evidence_bullish_and_strengthening():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_trend_evidence(
        trend=_trend(
            state="bullish",
            direction="strengthening",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["bullish_trend_strengthening"]
    assert evidence == [
        {
            "type": "trend",
            "signal": "bullish_trend_strengthening",
            "meaning": "bullish trend with strengthening dynamics",
        }
    ]


def test_add_trend_evidence_bullish_and_stable_preserves_strength():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_trend_evidence(
        trend=_trend(
            state="bullish",
            direction="stable",
            strength="strong",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["bullish_trend_stable"]
    assert evidence == [
        {
            "type": "trend",
            "signal": "bullish_trend_stable",
            "meaning": "bullish trend remains stable",
            "strength": "strong",
        }
    ]


def test_add_trend_evidence_bearish_but_improving():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_trend_evidence(
        trend=_trend(
            state="bearish",
            direction="improving",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["bearish_trend_improving"]
    assert evidence == [
        {
            "type": "trend",
            "signal": "bearish_trend_improving",
            "meaning": "bearish trend showing improvement",
        }
    ]


def test_add_trend_evidence_ignores_non_matching_trend():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_trend_evidence(
        trend=_trend(
            state="bearish",
            direction="deteriorating",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == []


# ---------------------------------------------------------------------------
# _add_momentum_evidence
# ---------------------------------------------------------------------------


def test_add_momentum_evidence_positive_and_improving():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_momentum_evidence(
        momentum=_momentum(
            state="positive",
            direction="improving",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["positive_momentum_improving"]
    assert evidence == [
        {
            "type": "momentum",
            "signal": "positive_momentum_improving",
            "meaning": "positive momentum with improving dynamics",
        }
    ]


def test_add_momentum_evidence_negative_but_improving():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_momentum_evidence(
        momentum=_momentum(
            state="negative",
            direction="improving",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["negative_momentum_improving"]
    assert evidence == [
        {
            "type": "momentum",
            "signal": "negative_momentum_improving",
            "meaning": "negative momentum but improving dynamics",
        }
    ]


def test_add_momentum_evidence_ignores_deteriorating_momentum():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_momentum_evidence(
        momentum=_momentum(
            state="positive",
            direction="deteriorating",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == []


# ---------------------------------------------------------------------------
# _add_transition_evidence
# ---------------------------------------------------------------------------


def test_add_transition_evidence_returns_without_detected_transition():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_transition_evidence(
        transition=_transition(
            detected=False,
            direction="toward_expansion",
            state="strong",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == []


def test_add_transition_evidence_toward_recovery():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_transition_evidence(
        transition=_transition(
            detected=True,
            direction="toward_recovery",
            state="moderate",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["toward_recovery_transition"]
    assert evidence == [
        {
            "type": "transition",
            "signal": "toward_recovery_transition",
            "meaning": (
                "economic dynamics are moving toward a "
                "potentially more supportive state"
            ),
            "state": "moderate",
        }
    ]


def test_add_transition_evidence_toward_expansion():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_transition_evidence(
        transition=_transition(
            detected=True,
            direction="toward_expansion",
            state="strong",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["toward_expansion_transition"]
    assert evidence[0]["signal"] == "toward_expansion_transition"
    assert evidence[0]["state"] == "strong"


def test_add_transition_evidence_toward_improvement():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_transition_evidence(
        transition=_transition(
            detected=True,
            direction="toward_improvement",
            state="moderate",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["toward_improvement_transition"]
    assert evidence[0]["signal"] == "toward_improvement_transition"


def test_add_transition_evidence_mixed_is_context_only():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_transition_evidence(
        transition=_transition(
            detected=True,
            direction="mixed",
            state="moderate",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == [
        {
            "type": "transition",
            "signal": "mixed_transition",
            "meaning": "transition evidence is directionally mixed",
            "state": "moderate",
        }
    ]


def test_add_transition_evidence_unknown_direction_is_ignored():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_transition_evidence(
        transition=_transition(
            detected=True,
            direction="unknown",
            state="moderate",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == []


# ---------------------------------------------------------------------------
# _add_regime_evidence
# ---------------------------------------------------------------------------


def test_add_regime_evidence_recovery():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_regime_evidence(
        regime="recovery",
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["recovery_regime"]
    assert evidence == [
        {
            "type": "regime",
            "signal": "recovery_regime",
            "meaning": "current regime is classified as recovery",
        }
    ]


def test_add_regime_evidence_expansion():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_regime_evidence(
        regime="expansion",
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["expansion_regime"]
    assert evidence == [
        {
            "type": "regime",
            "signal": "expansion_regime",
            "meaning": "current regime is classified as expansion",
        }
    ]


def test_add_regime_evidence_late_expansion_is_context_only():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_regime_evidence(
        regime="late_expansion",
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == [
        {
            "type": "regime",
            "signal": "late_expansion_regime",
            "meaning": (
                "current regime is late expansion; "
                "opportunity context requires additional evidence"
            ),
        }
    ]


def test_add_regime_evidence_ignores_other_regimes():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_regime_evidence(
        regime="contraction",
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == []


# ---------------------------------------------------------------------------
# _add_volatility_context
# ---------------------------------------------------------------------------


def test_add_volatility_context_shock_has_priority():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_volatility_context(
        volatility=_volatility(
            level="extreme",
            direction="falling",
            stress="extreme",
            shock=True,
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == [
        {
            "type": "volatility",
            "signal": "volatility_shock",
            "meaning": (
                "volatility shock is present; opportunity "
                "interpretation requires additional context"
            ),
        }
    ]


def test_add_volatility_context_falling_volatility_adds_reason():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_volatility_context(
        volatility=_volatility(
            direction="falling",
            stress="none",
            shock=False,
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == ["falling_volatility"]
    assert evidence == [
        {
            "type": "volatility",
            "signal": "falling_volatility",
            "meaning": "volatility is decreasing",
        }
    ]


def test_add_volatility_context_elevated_stress_is_context_only():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_volatility_context(
        volatility=_volatility(
            level="high",
            direction="stable",
            stress="elevated",
            shock=False,
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == [
        {
            "type": "volatility",
            "signal": "volatility_stress",
            "meaning": (
                "volatility is historically elevated; "
                "this is contextual rather than inherently "
                "positive or negative"
            ),
            "level": "high",
            "stress": "elevated",
        }
    ]


def test_add_volatility_context_extreme_stress_is_context_only():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_volatility_context(
        volatility=_volatility(
            level="extreme",
            direction="stable",
            stress="extreme",
            shock=False,
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence[0]["signal"] == "volatility_stress"
    assert evidence[0]["level"] == "extreme"
    assert evidence[0]["stress"] == "extreme"


def test_add_volatility_context_ignores_normal_stable_volatility():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_volatility_context(
        volatility=_volatility(
            level="normal",
            direction="stable",
            stress="none",
            shock=False,
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == []


# ---------------------------------------------------------------------------
# _add_position_context
# ---------------------------------------------------------------------------


def test_add_position_context_lower_position():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_position_context(
        position=_position(
            position="lower",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == [
        {
            "type": "position",
            "signal": "lower_position",
            "meaning": (
                "the indicator is at a relatively low historical "
                "position; this does not by itself establish an "
                "investment opportunity"
            ),
            "position": "lower",
        }
    ]


def test_add_position_context_lower_extreme_position():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_position_context(
        position=_position(
            position="lower_extreme",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence[0]["signal"] == "lower_position"
    assert evidence[0]["position"] == "lower_extreme"


def test_add_position_context_significant_drawdown():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_position_context(
        position=_position(
            drawdown_state="significant",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == [
        {
            "type": "position",
            "signal": "drawdown_context",
            "meaning": (
                "the indicator is experiencing a material drawdown; "
                "this is contextual and requires interpretation "
                "alongside economic direction"
            ),
            "drawdown_state": "significant",
        }
    ]


def test_add_position_context_severe_drawdown():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_position_context(
        position=_position(
            drawdown_state="severe",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence[0]["signal"] == "drawdown_context"
    assert evidence[0]["drawdown_state"] == "severe"


def test_add_position_context_recovering():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_position_context(
        position=_position(
            direction="recovering",
            extreme="lower",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert evidence == [
        {
            "type": "position",
            "signal": "position_recovering",
            "meaning": "the indicator is recovering from a lower position",
            "extreme": "lower",
        }
    ]


def test_add_position_context_can_emit_multiple_context_items():
    reasons = []
    evidence = []

    OpportunityInterpreter._add_position_context(
        position=_position(
            position="lower",
            direction="recovering",
            drawdown_state="severe",
            extreme="lower",
        ),
        reasons=reasons,
        evidence=evidence,
    )

    assert reasons == []
    assert len(evidence) == 3
    assert [item["signal"] for item in evidence] == [
        "lower_position",
        "drawdown_context",
        "position_recovering",
    ]


# ---------------------------------------------------------------------------
# _classify_state
# ---------------------------------------------------------------------------


def test_classify_state_established_with_three_improving_evidence():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(
            direction="improving",
        ),
        trend=_trend(
            direction="strengthening",
        ),
        momentum=_momentum(
            direction="improving",
        ),
        volatility=_volatility(),
        transition=_transition(),
        regime="expansion",
    )

    assert result == "established"


def test_classify_state_established_can_use_growth_acceleration_as_second_growth_signal():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(
            direction="stable",
            dynamic_state="accelerating",
        ),
        trend=_trend(
            direction="strengthening",
        ),
        momentum=_momentum(
            direction="improving",
        ),
        volatility=_volatility(),
        transition=_transition(),
        regime="recovery",
    )

    assert result == "established"


def test_classify_state_established_with_transition_contribution():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(
            direction="improving",
        ),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        transition=_transition(
            direction="toward_recovery",
            state="moderate",
        ),
        regime="recovery",
    )

    assert result == "established"


def test_classify_state_transition_can_add_two_improving_evidence():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(
            direction="improving",
        ),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        transition=_transition(
            direction="toward_expansion",
            state="strong",
        ),
        regime="stagnation",
    )

    assert result == "emerging"


def test_classify_state_established_requires_supportive_regime():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(
            direction="improving",
        ),
        trend=_trend(
            direction="strengthening",
        ),
        momentum=_momentum(
            direction="improving",
        ),
        volatility=_volatility(),
        transition=_transition(),
        regime="stagnation",
    )

    assert result != "established"


def test_classify_state_established_blocked_by_volatility_shock():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(
            direction="improving",
        ),
        trend=_trend(
            direction="strengthening",
        ),
        momentum=_momentum(
            direction="improving",
        ),
        volatility=_volatility(
            shock=True,
        ),
        transition=_transition(),
        regime="expansion",
    )

    assert result != "established"


def test_classify_state_emerging_from_strong_recovery_transition():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        transition=_transition(
            direction="toward_recovery",
            state="strong",
        ),
        regime="contraction",
    )

    assert result == "emerging"


def test_classify_state_emerging_from_moderate_expansion_transition():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        transition=_transition(
            direction="toward_expansion",
            state="moderate",
        ),
        regime="stagnation",
    )

    assert result == "emerging"


def test_classify_state_emerging_from_improvement_transition():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        transition=_transition(
            direction="toward_improvement",
            state="moderate",
        ),
        regime="stagnation",
    )

    assert result == "emerging"


def test_classify_state_does_not_use_weak_transition_as_emerging():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        transition=_transition(
            direction="toward_recovery",
            state="weak",
        ),
        regime="stagnation",
    )

    assert result == "limited"


def test_classify_state_supportive_with_positive_growth_bullish_trend_positive_momentum():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(
            state="positive",
            direction="stable",
        ),
        trend=_trend(
            state="bullish",
            direction="stable",
        ),
        momentum=_momentum(
            state="positive",
            direction="stable",
        ),
        volatility=_volatility(),
        transition=_transition(),
        regime="stagnation",
    )

    assert result == "supportive"


def test_classify_state_supportive_blocked_by_volatility_shock():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(
            state="positive",
        ),
        trend=_trend(
            state="bullish",
        ),
        momentum=_momentum(
            state="positive",
        ),
        volatility=_volatility(
            shock=True,
        ),
        transition=_transition(),
        regime="stagnation",
    )

    assert result != "supportive"


def test_classify_state_emerging_from_improving_growth():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(
            direction="improving",
        ),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        transition=_transition(),
        regime="stagnation",
    )

    assert result == "emerging"


def test_classify_state_emerging_from_strengthening_trend():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(),
        trend=_trend(
            direction="strengthening",
        ),
        momentum=_momentum(),
        volatility=_volatility(),
        transition=_transition(),
        regime="stagnation",
    )

    assert result == "emerging"


def test_classify_state_emerging_from_improving_momentum():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(
            direction="improving",
        ),
        volatility=_volatility(),
        transition=_transition(),
        regime="stagnation",
    )

    assert result == "emerging"


def test_classify_state_uncertain_with_extreme_volatility_stress():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(
            stress="extreme",
            shock=False,
        ),
        transition=_transition(),
        regime="stagnation",
    )

    assert result == "uncertain"


def test_classify_state_uncertain_with_volatility_shock():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(
            stress="none",
            shock=True,
        ),
        transition=_transition(),
        regime="stagnation",
    )

    assert result == "uncertain"


def test_classify_state_returns_limited_when_no_opportunity_evidence_exists():
    result = OpportunityInterpreter._classify_state(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        transition=_transition(),
        regime="stagnation",
    )

    assert result == "limited"


# ---------------------------------------------------------------------------
# Important semantic invariants
# ---------------------------------------------------------------------------


def test_lower_position_alone_does_not_create_opportunity():
    result = OpportunityInterpreter.interpret(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        position=_position(
            position="lower",
            extreme="lower",
        ),
        transition=_transition(),
        regime="stagnation",
    )

    assert result["state"] == "limited"

    assert any(
        item["signal"] == "lower_position"
        for item in result["evidence"]
    )


def test_drawdown_alone_does_not_create_opportunity():
    result = OpportunityInterpreter.interpret(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        position=_position(
            drawdown_state="severe",
        ),
        transition=_transition(),
        regime="stagnation",
    )

    assert result["state"] == "limited"

    assert any(
        item["signal"] == "drawdown_context"
        for item in result["evidence"]
    )


def test_volatility_falling_does_not_create_opportunity_by_itself():
    result = OpportunityInterpreter.interpret(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(
            direction="falling",
        ),
        position=_position(),
        transition=_transition(),
        regime="stagnation",
    )

    assert result["state"] == "limited"
    assert "falling_volatility" in result["reasons"]


def test_volatility_shock_does_not_get_positive_opportunity_evidence():
    result = OpportunityInterpreter.interpret(
        growth=_growth(),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(
            direction="falling",
            shock=True,
        ),
        position=_position(),
        transition=_transition(),
        regime="stagnation",
    )

    assert result["state"] == "uncertain"
    assert "falling_volatility" not in result["reasons"]

    assert any(
        item["signal"] == "volatility_shock"
        for item in result["evidence"]
    )


def test_negative_growth_improving_can_create_emerging_state():
    result = OpportunityInterpreter.interpret(
        growth=_growth(
            state="negative",
            direction="improving",
        ),
        trend=_trend(),
        momentum=_momentum(),
        volatility=_volatility(),
        position=_position(),
        transition=_transition(),
        regime="stagnation",
    )

    assert result["state"] == "emerging"
    assert "negative_growth_improving" in result["reasons"]