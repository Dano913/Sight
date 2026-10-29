from app.services.interpretation.investment.environment_interpreter import (
    EnvironmentInterpreter,
)


def _component(direction: str) -> dict:
    return {"direction": direction}


def _transition(
    *,
    detected: bool = False,
    direction: str = "unknown",
    state: str = "none",
    confidence: str = "low",
) -> dict:
    return {
        "detected": detected,
        "direction": direction,
        "state": state,
        "confidence": confidence,
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


# ---------------------------------------------------------------------------
# interpret
# ---------------------------------------------------------------------------


def test_interpret_returns_expected_environment_structure():
    result = EnvironmentInterpreter.interpret(
        growth=_component("improving"),
        trend=_component("improving"),
        momentum=_component("stable"),
        volatility=_volatility(),
        position=_position(),
        transition=_transition(
            detected=True,
            direction="toward_expansion",
            state="moderate",
            confidence="high",
        ),
        regime="expansion",
    )

    assert result["state"] == "supportive"
    assert result["regime"] == "expansion"
    assert result["directional_bias"] == "improving"
    assert result["coherence"] == "medium"

    assert result["transition"] == {
        "detected": True,
        "direction": "toward_expansion",
        "state": "moderate",
        "confidence": "high",
    }

    assert result["context"]["volatility"] == {
        "level": "normal",
        "direction": "stable",
        "stress": "none",
        "shock": False,
    }

    assert result["context"]["position"] == {
        "position": "normal",
        "direction": "stable",
        "drawdown_state": "none",
        "extreme": "none",
    }


def test_interpret_uses_defaults_for_missing_transition_values():
    result = EnvironmentInterpreter.interpret(
        growth=_component("stable"),
        trend=_component("stable"),
        momentum=_component("stable"),
        volatility={},
        position={},
        transition={},
        regime="stagnation",
    )

    assert result["transition"] == {
        "detected": False,
        "direction": "unknown",
        "state": "none",
        "confidence": "low",
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


# ---------------------------------------------------------------------------
# _get_directional_bias
# ---------------------------------------------------------------------------


def test_get_directional_bias_returns_unknown_when_all_directions_unknown():
    result = EnvironmentInterpreter._get_directional_bias(
        growth={"direction": "unknown"},
        trend={"direction": None},
        momentum={},
    )

    assert result == "unknown"


def test_get_directional_bias_returns_improving_for_two_improving():
    result = EnvironmentInterpreter._get_directional_bias(
        growth={"direction": "improving"},
        trend={"direction": "improving"},
        momentum={"direction": "stable"},
    )

    assert result == "improving"


def test_get_directional_bias_returns_deteriorating_for_two_deteriorating():
    result = EnvironmentInterpreter._get_directional_bias(
        growth={"direction": "deteriorating"},
        trend={"direction": "deteriorating"},
        momentum={"direction": "stable"},
    )

    assert result == "deteriorating"


def test_get_directional_bias_returns_stable_for_two_stable():
    result = EnvironmentInterpreter._get_directional_bias(
        growth={"direction": "stable"},
        trend={"direction": "stable"},
        momentum={"direction": "improving"},
    )

    assert result == "stable"


def test_get_directional_bias_returns_mixed_when_improving_and_deteriorating():
    result = EnvironmentInterpreter._get_directional_bias(
        growth={"direction": "improving"},
        trend={"direction": "deteriorating"},
        momentum={"direction": "stable"},
    )

    assert result == "mixed"


def test_get_directional_bias_returns_improving_when_only_one_known_direction():
    result = EnvironmentInterpreter._get_directional_bias(
        growth={"direction": "improving"},
        trend={"direction": "unknown"},
        momentum={},
    )

    assert result == "improving"


def test_get_directional_bias_returns_deteriorating_when_only_one_known_direction():
    result = EnvironmentInterpreter._get_directional_bias(
        growth={"direction": "unknown"},
        trend={"direction": "deteriorating"},
        momentum={},
    )

    assert result == "deteriorating"


def test_get_directional_bias_returns_stable_when_only_one_known_direction():
    result = EnvironmentInterpreter._get_directional_bias(
        growth={"direction": "stable"},
        trend={"direction": None},
        momentum={"direction": "unknown"},
    )

    assert result == "stable"


def test_get_directional_bias_ignores_unknown_and_none():
    result = EnvironmentInterpreter._get_directional_bias(
        growth={"direction": "improving"},
        trend={"direction": "unknown"},
        momentum={"direction": None},
    )

    assert result == "improving"


# ---------------------------------------------------------------------------
# _get_coherence
# ---------------------------------------------------------------------------


def test_get_coherence_returns_unknown_when_no_direction_is_known():
    result = EnvironmentInterpreter._get_coherence(
        growth={"direction": "unknown"},
        trend={"direction": None},
        momentum={},
    )

    assert result == "unknown"


def test_get_coherence_returns_high_when_all_known_directions_are_equal():
    result = EnvironmentInterpreter._get_coherence(
        growth={"direction": "improving"},
        trend={"direction": "improving"},
        momentum={"direction": "improving"},
    )

    assert result == "high"


def test_get_coherence_returns_high_when_only_one_known_direction_exists():
    result = EnvironmentInterpreter._get_coherence(
        growth={"direction": "improving"},
        trend={"direction": "unknown"},
        momentum={},
    )

    assert result == "high"


def test_get_coherence_returns_low_when_improving_and_deteriorating_coexist():
    result = EnvironmentInterpreter._get_coherence(
        growth={"direction": "improving"},
        trend={"direction": "deteriorating"},
        momentum={"direction": "improving"},
    )

    assert result == "low"


def test_get_coherence_returns_medium_for_non_conflicting_mixed_directions():
    result = EnvironmentInterpreter._get_coherence(
        growth={"direction": "improving"},
        trend={"direction": "stable"},
        momentum={"direction": "improving"},
    )

    assert result == "medium"


# ---------------------------------------------------------------------------
# _classify_environment
# ---------------------------------------------------------------------------


def test_classify_environment_returns_challenging_for_contraction():
    result = EnvironmentInterpreter._classify_environment(
        regime="contraction",
        directional_bias="improving",
        transition_direction="unknown",
        transition_state="none",
    )

    assert result == "challenging"


def test_classify_environment_returns_challenging_for_slowdown():
    result = EnvironmentInterpreter._classify_environment(
        regime="slowdown",
        directional_bias="stable",
        transition_direction="unknown",
        transition_state="none",
    )

    assert result == "challenging"


def test_classify_environment_returns_supportive_for_expansion():
    result = EnvironmentInterpreter._classify_environment(
        regime="expansion",
        directional_bias="improving",
        transition_direction="unknown",
        transition_state="none",
    )

    assert result == "supportive"


def test_classify_environment_returns_supportive_for_recovery():
    result = EnvironmentInterpreter._classify_environment(
        regime="recovery",
        directional_bias="stable",
        transition_direction="unknown",
        transition_state="none",
    )

    assert result == "supportive"


def test_classify_environment_returns_transitioning_for_expansion_deterioration():
    result = EnvironmentInterpreter._classify_environment(
        regime="expansion",
        directional_bias="deteriorating",
        transition_direction="toward_slowdown",
        transition_state="moderate",
    )

    assert result == "transitioning"


def test_classify_environment_returns_transitioning_for_recovery_deterioration():
    result = EnvironmentInterpreter._classify_environment(
        regime="recovery",
        directional_bias="deteriorating",
        transition_direction="toward_slowdown",
        transition_state="strong",
    )

    assert result == "transitioning"


def test_classify_environment_does_not_transition_for_weak_transition():
    result = EnvironmentInterpreter._classify_environment(
        regime="expansion",
        directional_bias="deteriorating",
        transition_direction="toward_slowdown",
        transition_state="weak",
    )

    assert result == "supportive"


def test_classify_environment_returns_supportive_for_late_expansion_without_slowdown_transition():
    result = EnvironmentInterpreter._classify_environment(
        regime="late_expansion",
        directional_bias="stable",
        transition_direction="unknown",
        transition_state="none",
    )

    assert result == "supportive"


def test_classify_environment_returns_transitioning_for_late_expansion_toward_slowdown():
    result = EnvironmentInterpreter._classify_environment(
        regime="late_expansion",
        directional_bias="stable",
        transition_direction="toward_slowdown",
        transition_state="moderate",
    )

    assert result == "transitioning"


def test_classify_environment_returns_transitioning_for_late_expansion_strong_transition():
    result = EnvironmentInterpreter._classify_environment(
        regime="late_expansion",
        directional_bias="improving",
        transition_direction="toward_slowdown",
        transition_state="strong",
    )

    assert result == "transitioning"


def test_classify_environment_returns_neutral_for_stagnation():
    result = EnvironmentInterpreter._classify_environment(
        regime="stagnation",
        directional_bias="improving",
        transition_direction="toward_expansion",
        transition_state="strong",
    )

    assert result == "neutral"


def test_classify_environment_returns_neutral_for_unknown_regime():
    result = EnvironmentInterpreter._classify_environment(
        regime="unknown_regime",
        directional_bias="improving",
        transition_direction="toward_expansion",
        transition_state="strong",
    )

    assert result == "neutral"


# ---------------------------------------------------------------------------
# Volatility / position are descriptive context only
# ---------------------------------------------------------------------------


def test_volatility_does_not_change_environment_classification():
    base = EnvironmentInterpreter.interpret(
        growth=_component("improving"),
        trend=_component("improving"),
        momentum=_component("stable"),
        volatility=_volatility(
            level="normal",
            direction="stable",
            stress="none",
            shock=False,
        ),
        position=_position(),
        transition=_transition(),
        regime="expansion",
    )

    stressed = EnvironmentInterpreter.interpret(
        growth=_component("improving"),
        trend=_component("improving"),
        momentum=_component("stable"),
        volatility=_volatility(
            level="extreme",
            direction="rising",
            stress="high",
            shock=True,
        ),
        position=_position(),
        transition=_transition(),
        regime="expansion",
    )

    assert base["state"] == "supportive"
    assert stressed["state"] == "supportive"


def test_position_does_not_change_environment_classification():
    base = EnvironmentInterpreter.interpret(
        growth=_component("improving"),
        trend=_component("improving"),
        momentum=_component("stable"),
        volatility=_volatility(),
        position=_position(
            position="normal",
            direction="stable",
            drawdown_state="none",
            extreme="none",
        ),
        transition=_transition(),
        regime="expansion",
    )

    extreme_position = EnvironmentInterpreter.interpret(
        growth=_component("improving"),
        trend=_component("improving"),
        momentum=_component("stable"),
        volatility=_volatility(),
        position=_position(
            position="extreme",
            direction="deteriorating",
            drawdown_state="deep",
            extreme="high",
        ),
        transition=_transition(),
        regime="expansion",
    )

    assert base["state"] == "supportive"
    assert extreme_position["state"] == "supportive"


def test_volatility_and_position_are_preserved_as_context():
    result = EnvironmentInterpreter.interpret(
        growth=_component("stable"),
        trend=_component("stable"),
        momentum=_component("stable"),
        volatility={
            "level": "high",
            "direction": "rising",
            "stress": "elevated",
            "shock": True,
        },
        position={
            "position": "extended",
            "direction": "deteriorating",
            "drawdown_state": "deep",
            "extreme": "upper",
        },
        transition=_transition(),
        regime="stagnation",
    )

    assert result["context"]["volatility"] == {
        "level": "high",
        "direction": "rising",
        "stress": "elevated",
        "shock": True,
    }

    assert result["context"]["position"] == {
        "position": "extended",
        "direction": "deteriorating",
        "drawdown_state": "deep",
        "extreme": "upper",
    }