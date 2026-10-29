from __future__ import annotations

from app.services.interpretation.investment.signal_generator import SignalGenerator


def test_generate_returns_all_signal_groups():
    result = SignalGenerator.generate(
        growth={},
        trend={},
        momentum={},
        volatility={},
        position={},
        transition={},
        regime="unknown",
    )

    assert set(result) == {
        "growth",
        "trend",
        "momentum",
        "volatility",
        "position",
        "transition",
        "regime",
    }


def test_generate_uses_unknown_defaults():
    result = SignalGenerator.generate(
        growth={},
        trend={},
        momentum={},
        volatility={},
        position={},
        transition={},
        regime="unknown",
    )

    assert result["growth"] == {
        "positive": False,
        "negative": False,
        "flat": False,
        "improving": False,
        "deteriorating": False,
        "stable": False,
        "accelerating": False,
        "decelerating": False,
        "acceleration_positive": False,
        "acceleration_negative": False,
        "reversal": False,
    }

    assert result["trend"] == {
        "bullish": False,
        "bearish": False,
        "neutral": False,
        "mixed": False,
        "strengthening": False,
        "weakening": False,
        "stable": False,
        "strong": False,
        "moderate": False,
        "weak": False,
        "reversal": False,
    }

    assert result["momentum"] == {
        "positive": False,
        "negative": False,
        "neutral": False,
        "improving": False,
        "deteriorating": False,
        "stable": False,
        "acceleration_positive": False,
        "acceleration_negative": False,
    }

    assert result["volatility"] == {
        "normal": False,
        "high": False,
        "extreme": False,
        "rising": False,
        "falling": False,
        "stable": False,
        "stress_normal": False,
        "stress_elevated": False,
        "stress_extreme": False,
        "shock": False,
    }

    assert result["position"] == {
        "upper_extreme": False,
        "upper": False,
        "middle": False,
        "lower": False,
        "lower_extreme": False,
        "recovering": False,
        "falling": False,
        "mixed": False,
        "stable": False,
        "minor_drawdown": False,
        "significant_drawdown": False,
        "severe_drawdown": False,
        "no_drawdown": False,
        "extreme": False,
    }

    assert result["transition"] == {
        "detected": False,
        "toward_slowdown": False,
        "toward_contraction": False,
        "toward_recovery": False,
        "toward_expansion": False,
        "toward_improvement": False,
        "toward_deterioration": False,
        "mixed": False,
        "unknown": True,
        "early": False,
        "moderate": False,
        "strong": False,
        "none": True,
    }

    assert result["regime"] == {
        "expansion": False,
        "late_expansion": False,
        "slowdown": False,
        "stagnation": False,
        "recovery": False,
        "contraction": False,
        "neutral": False,
    }


def test_growth_signals_map_all_fields():
    result = SignalGenerator._growth_signals(
        growth={
            "state": "positive",
            "direction": "improving",
            "acceleration": "positive",
            "dynamic_state": "accelerating",
            "reversal": True,
        }
    )

    assert result == {
        "positive": True,
        "negative": False,
        "flat": False,
        "improving": True,
        "deteriorating": False,
        "stable": False,
        "accelerating": True,
        "decelerating": False,
        "acceleration_positive": True,
        "acceleration_negative": False,
        "reversal": True,
    }


def test_growth_signals_map_negative_decelerating_state():
    result = SignalGenerator._growth_signals(
        growth={
            "state": "negative",
            "direction": "deteriorating",
            "acceleration": "negative",
            "dynamic_state": "decelerating",
            "reversal": False,
        }
    )

    assert result["negative"] is True
    assert result["deteriorating"] is True
    assert result["decelerating"] is True
    assert result["acceleration_negative"] is True
    assert result["positive"] is False
    assert result["reversal"] is False


def test_growth_signals_are_exclusive_for_state_direction_and_acceleration():
    result = SignalGenerator._growth_signals(
        growth={
            "state": "flat",
            "direction": "stable",
            "acceleration": "positive",
            "dynamic_state": "accelerating",
        }
    )

    assert result["flat"] is True
    assert result["positive"] is False
    assert result["negative"] is False

    assert result["stable"] is True
    assert result["improving"] is False
    assert result["deteriorating"] is False

    assert result["acceleration_positive"] is True
    assert result["acceleration_negative"] is False


def test_trend_signals_map_all_fields():
    result = SignalGenerator._trend_signals(
        trend={
            "state": "bullish",
            "direction": "strengthening",
            "strength": "strong",
            "reversal": True,
        }
    )

    assert result == {
        "bullish": True,
        "bearish": False,
        "neutral": False,
        "mixed": False,
        "strengthening": True,
        "weakening": False,
        "stable": False,
        "strong": True,
        "moderate": False,
        "weak": False,
        "reversal": True,
    }


def test_trend_signals_map_bearish_weakening():
    result = SignalGenerator._trend_signals(
        trend={
            "state": "bearish",
            "direction": "weakening",
            "strength": "weak",
        }
    )

    assert result["bearish"] is True
    assert result["weakening"] is True
    assert result["weak"] is True

    assert result["bullish"] is False
    assert result["strengthening"] is False
    assert result["strong"] is False


def test_momentum_signals_map_all_fields():
    result = SignalGenerator._momentum_signals(
        momentum={
            "state": "positive",
            "direction": "improving",
            "acceleration": "positive",
        }
    )

    assert result == {
        "positive": True,
        "negative": False,
        "neutral": False,
        "improving": True,
        "deteriorating": False,
        "stable": False,
        "acceleration_positive": True,
        "acceleration_negative": False,
    }


def test_momentum_signals_map_negative_deteriorating():
    result = SignalGenerator._momentum_signals(
        momentum={
            "state": "negative",
            "direction": "deteriorating",
            "acceleration": "negative",
        }
    )

    assert result["negative"] is True
    assert result["deteriorating"] is True
    assert result["acceleration_negative"] is True

    assert result["positive"] is False
    assert result["improving"] is False
    assert result["acceleration_positive"] is False


def test_volatility_signals_map_all_fields():
    result = SignalGenerator._volatility_signals(
        volatility={
            "level": "high",
            "direction": "rising",
            "stress": "elevated",
            "shock": True,
        }
    )

    assert result == {
        "normal": False,
        "high": True,
        "extreme": False,
        "rising": True,
        "falling": False,
        "stable": False,
        "stress_normal": False,
        "stress_elevated": True,
        "stress_extreme": False,
        "shock": True,
    }


def test_volatility_signals_map_extreme_stable_stress():
    result = SignalGenerator._volatility_signals(
        volatility={
            "level": "extreme",
            "direction": "stable",
            "stress": "extreme",
            "shock": False,
        }
    )

    assert result["extreme"] is True
    assert result["stable"] is True
    assert result["stress_extreme"] is True
    assert result["shock"] is False


def test_position_signals_map_all_fields():
    result = SignalGenerator._position_signals(
        position={
            "position": "lower_extreme",
            "direction": "recovering",
            "drawdown_state": "significant",
            "extreme": "lower",
        }
    )

    assert result == {
        "upper_extreme": False,
        "upper": False,
        "middle": False,
        "lower": False,
        "lower_extreme": True,
        "recovering": True,
        "falling": False,
        "mixed": False,
        "stable": False,
        "minor_drawdown": False,
        "significant_drawdown": True,
        "severe_drawdown": False,
        "no_drawdown": False,
        "extreme": True,
    }


def test_position_signals_map_no_drawdown_and_non_extreme_position():
    result = SignalGenerator._position_signals(
        position={
            "position": "middle",
            "direction": "stable",
            "drawdown_state": "none",
            "extreme": "none",
        }
    )

    assert result["middle"] is True
    assert result["stable"] is True
    assert result["no_drawdown"] is True
    assert result["extreme"] is False


def test_position_extreme_is_derived_from_extreme_field():
    result = SignalGenerator._position_signals(
        position={
            "position": "upper_extreme",
            "direction": "falling",
            "drawdown_state": "minor",
            "extreme": "upper",
        }
    )

    assert result["upper_extreme"] is True
    assert result["falling"] is True
    assert result["minor_drawdown"] is True
    assert result["extreme"] is True


def test_transition_signals_map_all_fields():
    result = SignalGenerator._transition_signals(
        transition={
            "detected": True,
            "direction": "toward_contraction",
            "state": "strong",
        }
    )

    assert result == {
        "detected": True,
        "toward_slowdown": False,
        "toward_contraction": True,
        "toward_recovery": False,
        "toward_expansion": False,
        "toward_improvement": False,
        "toward_deterioration": False,
        "mixed": False,
        "unknown": False,
        "early": False,
        "moderate": False,
        "strong": True,
        "none": False,
    }


def test_transition_signals_map_recovery():
    result = SignalGenerator._transition_signals(
        transition={
            "detected": True,
            "direction": "toward_recovery",
            "state": "early",
        }
    )

    assert result["detected"] is True
    assert result["toward_recovery"] is True
    assert result["early"] is True

    assert result["toward_contraction"] is False
    assert result["toward_deterioration"] is False
    assert result["strong"] is False


def test_transition_signals_map_mixed_and_moderate():
    result = SignalGenerator._transition_signals(
        transition={
            "detected": True,
            "direction": "mixed",
            "state": "moderate",
        }
    )

    assert result["detected"] is True
    assert result["mixed"] is True
    assert result["moderate"] is True
    assert result["unknown"] is False


def test_transition_direction_and_state_are_independent():
    result = SignalGenerator._transition_signals(
        transition={
            "detected": True,
            "direction": "toward_expansion",
            "state": "strong",
        }
    )

    assert result["toward_expansion"] is True
    assert result["strong"] is True
    assert result["toward_contraction"] is False
    assert result["toward_slowdown"] is False


def test_regime_signals_map_each_regime():
    regimes = (
        "expansion",
        "late_expansion",
        "slowdown",
        "stagnation",
        "recovery",
        "contraction",
        "neutral",
    )

    for regime in regimes:
        result = SignalGenerator._regime_signals(regime)

        assert result[regime] is True

        for other_regime in regimes:
            if other_regime != regime:
                assert result[other_regime] is False


def test_regime_signals_unknown_regime_has_no_positive_flag():
    result = SignalGenerator._regime_signals("unknown")

    assert all(value is False for value in result.values())


def test_generate_preserves_each_dimension_independently():
    result = SignalGenerator.generate(
        growth={
            "state": "negative",
            "direction": "deteriorating",
        },
        trend={
            "state": "bullish",
            "direction": "strengthening",
        },
        momentum={
            "state": "positive",
            "direction": "improving",
        },
        volatility={
            "level": "high",
            "direction": "rising",
            "stress": "elevated",
            "shock": True,
        },
        position={
            "position": "lower",
            "direction": "recovering",
            "drawdown_state": "minor",
            "extreme": "none",
        },
        transition={
            "detected": True,
            "direction": "toward_recovery",
            "state": "moderate",
        },
        regime="recovery",
    )

    assert result["growth"]["negative"] is True
    assert result["growth"]["deteriorating"] is True

    assert result["trend"]["bullish"] is True
    assert result["trend"]["strengthening"] is True

    assert result["momentum"]["positive"] is True
    assert result["momentum"]["improving"] is True

    assert result["volatility"]["high"] is True
    assert result["volatility"]["rising"] is True
    assert result["volatility"]["stress_elevated"] is True
    assert result["volatility"]["shock"] is True

    assert result["position"]["lower"] is True
    assert result["position"]["recovering"] is True
    assert result["position"]["minor_drawdown"] is True
    assert result["position"]["extreme"] is False

    assert result["transition"]["detected"] is True
    assert result["transition"]["toward_recovery"] is True
    assert result["transition"]["moderate"] is True

    assert result["regime"]["recovery"] is True


def test_generate_handles_explicit_none_values_gracefully():
    result = SignalGenerator.generate(
        growth={"state": None, "direction": None, "dynamic_state": None},
        trend={"state": None, "direction": None, "strength": None},
        momentum={"state": None, "direction": None},
        volatility={"level": None, "direction": None, "stress": None},
        position={"position": None, "direction": None, "drawdown_state": None},
        transition={"detected": False, "direction": None, "state": None},
        regime="unknown",
    )

    # Verifica que None se normalice a "unknown" y "none" en transition
    assert result["transition"]["unknown"] is True
    assert result["transition"]["none"] is True
    assert result["transition"]["detected"] is False

    # Verifica que los estados indefinidos no activen señales de riesgo o tendencia
    assert result["growth"]["positive"] is False
    assert result["trend"]["bullish"] is False
    assert result["momentum"]["positive"] is False
    assert result["volatility"]["high"] is False
    assert result["position"]["extreme"] is False