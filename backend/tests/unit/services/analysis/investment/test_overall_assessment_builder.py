from __future__ import annotations

from app.services.analysis.investment.overall_assessment_builder import (
    OverallAssessmentBuilder,
)


def make_environment(*, state="supportive"):
    return {
        "state": state,
    }


def make_risk(*, state="moderate"):
    return {
        "state": state,
    }


def make_opportunity(*, state="emerging"):
    return {
        "state": state,
    }


def make_confidence(*, state="high"):
    return {
        "state": state,
    }


def make_macro_bias(
    *,
    state="supportive",
    direction="improving",
    strength="moderate",
    coherence="high",
    reasons=None,
):
    return {
        "state": state,
        "direction": direction,
        "strength": strength,
        "coherence": coherence,
        "reasons": reasons if reasons is not None else [
            "supportive_environment",
            "emerging_macro_opportunity",
        ],
    }


def make_conviction(*, state="moderate"):
    return {
        "state": state,
    }


def make_transition(
    *,
    detected=True,
    direction="toward_recovery",
    state="moderate",
):
    return {
        "detected": detected,
        "direction": direction,
        "state": state,
    }


def build(
    *,
    environment=None,
    risk=None,
    opportunity=None,
    confidence=None,
    macro_bias=None,
    conviction=None,
    transition=None,
):
    return OverallAssessmentBuilder.build(
        environment=(
            make_environment()
            if environment is None
            else environment
        ),
        risk=(
            make_risk()
            if risk is None
            else risk
        ),
        opportunity=(
            make_opportunity()
            if opportunity is None
            else opportunity
        ),
        confidence=(
            make_confidence()
            if confidence is None
            else confidence
        ),
        macro_bias=(
            make_macro_bias()
            if macro_bias is None
            else macro_bias
        ),
        conviction=(
            make_conviction()
            if conviction is None
            else conviction
        ),
        transition=(
            make_transition()
            if transition is None
            else transition
        ),
    )


class TestOverallAssessmentBuilder:

    def test_returns_expected_structure(self):
        result = build()

        assert set(result) == {
            "assessment",
            "direction",
            "strength",
            "coherence",
            "macro_bias",
            "conviction",
            "confidence",
            "environment",
            "risk",
            "opportunity",
            "transition",
            "reasons",
        }

    def test_assembles_macro_bias_fields(self):
        result = build(
            macro_bias=make_macro_bias(
                state="cautious",
                direction="deteriorating",
                strength="strong",
                coherence="low",
            )
        )

        assert result["assessment"] == "cautious"
        assert result["direction"] == "deteriorating"
        assert result["strength"] == "strong"
        assert result["coherence"] == "low"
        assert result["macro_bias"] == "cautious"

    def test_assembles_interpretation_states(self):
        result = build(
            environment=make_environment(
                state="challenging",
            ),
            risk=make_risk(
                state="high",
            ),
            opportunity=make_opportunity(
                state="limited",
            ),
            confidence=make_confidence(
                state="moderate",
            ),
            conviction=make_conviction(
                state="low",
            ),
        )

        assert result["environment"] == "challenging"
        assert result["risk"] == "high"
        assert result["opportunity"] == "limited"
        assert result["confidence"] == "moderate"
        assert result["conviction"] == "low"

    def test_transition_is_assembled_as_nested_structure(self):
        result = build(
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="strong",
            )
        )

        assert result["transition"] == {
            "detected": True,
            "direction": "toward_slowdown",
            "state": "strong",
        }

    def test_transition_detected_is_normalized_to_bool(self):
        result = build(
            transition={
                "detected": 1,
                "direction": "toward_expansion",
                "state": "moderate",
            }
        )

        assert result["transition"]["detected"] is True

    def test_false_transition_detected_is_normalized_to_bool(self):
        result = build(
            transition={
                "detected": 0,
                "direction": "unknown",
                "state": "none",
            }
        )

        assert result["transition"]["detected"] is False

    def test_macro_bias_reasons_are_preserved(self):
        reasons = [
            "supportive_environment",
            "macro_transition",
            "macro_improvement_transition",
        ]

        result = build(
            macro_bias=make_macro_bias(
                reasons=reasons,
            )
        )

        assert result["reasons"] == reasons

    def test_macro_bias_reasons_are_deduplicated(self):
        result = build(
            macro_bias=make_macro_bias(
                reasons=[
                    "supportive_environment",
                    "macro_transition",
                    "supportive_environment",
                    "macro_transition",
                ]
            )
        )

        assert result["reasons"] == [
            "supportive_environment",
            "macro_transition",
        ]

    def test_empty_macro_bias_reasons_produce_empty_list(self):
        result = build(
            macro_bias=make_macro_bias(
                reasons=[],
            )
        )

        assert result["reasons"] == []

    def test_missing_macro_bias_reasons_produce_empty_list(self):
        result = build(
            macro_bias={
                "state": "neutral",
                "direction": "unknown",
                "strength": "unknown",
                "coherence": "unknown",
            }
        )

        assert result["reasons"] == []

    def test_missing_macro_bias_fields_use_unknown_defaults(self):
        result = build(
            macro_bias={},
        )

        assert result["assessment"] == "unknown"
        assert result["direction"] == "unknown"
        assert result["strength"] == "unknown"
        assert result["coherence"] == "unknown"
        assert result["macro_bias"] == "unknown"

    def test_missing_dimension_states_use_unknown_defaults(self):
        result = build(
            environment={},
            risk={},
            opportunity={},
            confidence={},
            conviction={},
        )

        assert result["environment"] == "unknown"
        assert result["risk"] == "unknown"
        assert result["opportunity"] == "unknown"
        assert result["confidence"] == "unknown"
        assert result["conviction"] == "unknown"

    def test_missing_transition_fields_use_defaults(self):
        result = build(
            transition={},
        )

        assert result["transition"] == {
            "detected": False,
            "direction": "unknown",
            "state": "none",
        }

    def test_builder_does_not_reinterpret_other_dimensions(self):
        result = build(
            environment={
                "state": "challenging",
                "extra": "ignored",
            },
            risk={
                "state": "extreme",
                "extra": "ignored",
            },
            opportunity={
                "state": "established",
                "extra": "ignored",
            },
            confidence={
                "state": "very_low",
                "extra": "ignored",
            },
            conviction={
                "state": "low",
                "extra": "ignored",
            },
            macro_bias=make_macro_bias(
                state="neutral",
                direction="deteriorating",
                strength="weak",
                coherence="low",
            ),
        )

        assert result["assessment"] == "neutral"
        assert result["environment"] == "challenging"
        assert result["risk"] == "extreme"
        assert result["opportunity"] == "established"
        assert result["confidence"] == "very_low"
        assert result["conviction"] == "low"

    def test_regime_or_signals_are_not_part_of_the_builder_contract(self):
        result = build()

        assert "regime" not in result
        assert "signals" not in result

    def test_output_is_independent_from_input_reasons_mutation(self):
        reasons = [
            "supportive_environment",
            "macro_transition",
        ]

        macro_bias = make_macro_bias(
            reasons=reasons,
        )

        result = build(
            macro_bias=macro_bias,
        )

        reasons.append("new_reason")

        assert result["reasons"] == [
            "supportive_environment",
            "macro_transition",
        ]