from __future__ import annotations

import pytest

from app.services.interpretation.investment.confidence_estimator import (
    ConfidenceEstimator,
)


def make_growth(
    *,
    state: str = "positive",
    direction: str = "improving",
    dynamic_state: str = "accelerating",
) -> dict:
    return {
        "state": state,
        "direction": direction,
        "dynamic_state": dynamic_state,
    }


def make_trend(
    *,
    state: str = "bullish",
    direction: str = "improving",
    strength: str = "strong",
) -> dict:
    return {
        "state": state,
        "direction": direction,
        "strength": strength,
    }


def make_momentum(
    *,
    state: str = "positive",
    direction: str = "improving",
) -> dict:
    return {
        "state": state,
        "direction": direction,
    }


def make_volatility(
    *,
    level: str = "normal",
    stress: str = "normal",
    direction: str = "stable",
) -> dict:
    return {
        "level": level,
        "stress": stress,
        "direction": direction,
    }


def make_position(
    *,
    position: str = "neutral",
    direction: str = "stable",
) -> dict:
    return {
        "position": position,
        "direction": direction,
    }


def make_transition(
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


def estimate(
    *,
    growth: dict | None = None,
    trend: dict | None = None,
    momentum: dict | None = None,
    volatility: dict | None = None,
    position: dict | None = None,
    transition: dict | None = None,
    regime: str = "expansion",
) -> dict:
    return ConfidenceEstimator.estimate(
        growth=make_growth() if growth is None else growth,
        trend=make_trend() if trend is None else trend,
        momentum=make_momentum() if momentum is None else momentum,
        volatility=(
            make_volatility()
            if volatility is None
            else volatility
        ),
        position=(
            make_position()
            if position is None
            else position
        ),
        transition=(
            make_transition()
            if transition is None
            else transition
        ),
        regime=regime,
    )


class TestConfidenceEstimator:

    def test_returns_expected_structure(self):
        result = estimate()

        assert set(result) == {
            "state",
            "coherence",
            "reasons",
            "supporting_evidence",
            "contradictions",
            "uncertainty",
            "context",
        }

        assert isinstance(result["state"], str)
        assert isinstance(result["coherence"], str)
        assert isinstance(result["reasons"], list)
        assert isinstance(result["supporting_evidence"], list)
        assert isinstance(result["contradictions"], list)
        assert isinstance(result["uncertainty"], list)

    def test_returns_regime_and_transition_context(self):
        transition = make_transition(
            detected=True,
            direction="toward_expansion",
            state="moderate",
        )

        result = estimate(
            transition=transition,
            regime="recovery",
        )

        assert result["context"] == {
            "regime": "recovery",
            "transition": {
                "detected": True,
                "direction": "toward_expansion",
                "state": "moderate",
            },
        }

    def test_coherent_complete_interpretation_has_high_confidence(self):
        result = estimate()

        assert result["state"] == "high"
        assert result["coherence"] == "high"
        assert result["contradictions"] == []
        assert result["uncertainty"] == ["transition_direction_unknown"]

        assert "growth_state_and_direction_available" in (
            result["supporting_evidence"]
        )
        assert "trend_state_and_direction_available" in (
            result["supporting_evidence"]
        )
        assert "momentum_state_and_direction_available" in (
            result["supporting_evidence"]
        )

    def test_unknown_growth_state_creates_uncertainty(self):
        result = estimate(
            growth=make_growth(state="unknown"),
        )

        assert "unknown_growth_state" in result["uncertainty"]

    def test_unknown_growth_direction_creates_uncertainty(self):
        result = estimate(
            growth=make_growth(direction="unknown"),
        )

        assert "unknown_growth_direction" in result["uncertainty"]

    def test_unknown_growth_dynamic_state_creates_uncertainty(self):
        result = estimate(
            growth=make_growth(dynamic_state="unknown"),
        )

        assert "unknown_growth_dynamic_state" in result["uncertainty"]

    def test_unknown_trend_state_creates_uncertainty(self):
        result = estimate(
            trend=make_trend(state="unknown"),
        )

        assert "unknown_trend_state" in result["uncertainty"]

    def test_mixed_trend_creates_uncertainty(self):
        result = estimate(
            trend=make_trend(state="mixed"),
        )

        assert "mixed_trend_structure" in result["uncertainty"]

    def test_unknown_trend_direction_creates_uncertainty(self):
        result = estimate(
            trend=make_trend(direction="unknown"),
        )

        assert "unknown_trend_direction" in result["uncertainty"]

    def test_unknown_trend_strength_creates_uncertainty(self):
        result = estimate(
            trend=make_trend(strength="unknown"),
        )

        assert "unknown_trend_strength" in result["uncertainty"]

    def test_unknown_momentum_state_creates_uncertainty(self):
        result = estimate(
            momentum=make_momentum(state="unknown"),
        )

        assert "unknown_momentum_state" in result["uncertainty"]

    def test_unknown_momentum_direction_creates_uncertainty(self):
        result = estimate(
            momentum=make_momentum(direction="unknown"),
        )

        assert "unknown_momentum_direction" in result["uncertainty"]

    @pytest.mark.parametrize(
        ("growth_state", "trend_state", "expected"),
        [
            (
                "positive",
                "bearish",
                "positive_growth_vs_bearish_trend",
            ),
            (
                "negative",
                "bullish",
                "negative_growth_vs_bullish_trend",
            ),
        ],
    )
    def test_detects_growth_trend_contradictions(
        self,
        growth_state,
        trend_state,
        expected,
    ):
        result = estimate(
            growth=make_growth(state=growth_state),
            trend=make_trend(state=trend_state),
        )

        assert expected in result["contradictions"]

    @pytest.mark.parametrize(
        ("growth_state", "momentum_state", "expected"),
        [
            (
                "positive",
                "negative",
                "positive_growth_vs_negative_momentum",
            ),
            (
                "negative",
                "positive",
                "negative_growth_vs_positive_momentum",
            ),
        ],
    )
    def test_detects_growth_momentum_contradictions(
        self,
        growth_state,
        momentum_state,
        expected,
    ):
        result = estimate(
            growth=make_growth(state=growth_state),
            momentum=make_momentum(state=momentum_state),
        )

        assert expected in result["contradictions"]

    @pytest.mark.parametrize(
        ("trend_state", "momentum_state", "expected"),
        [
            (
                "bullish",
                "negative",
                "bullish_trend_vs_negative_momentum",
            ),
            (
                "bearish",
                "positive",
                "bearish_trend_vs_positive_momentum",
            ),
        ],
    )
    def test_detects_trend_momentum_contradictions(
        self,
        trend_state,
        momentum_state,
        expected,
    ):
        result = estimate(
            trend=make_trend(state=trend_state),
            momentum=make_momentum(state=momentum_state),
        )

        assert expected in result["contradictions"]

    def test_non_detected_transition_with_unknown_direction_creates_uncertainty(
        self,
    ):
        result = estimate(
            transition=make_transition(
                detected=False,
                direction="unknown",
            ),
        )

        assert "transition_direction_unknown" in result["uncertainty"]

    def test_detected_transition_without_direction_creates_uncertainty(
        self,
    ):
        result = estimate(
            transition=make_transition(
                detected=True,
                direction="unknown",
                state="moderate",
            ),
        )

        assert "detected_transition_without_direction" in (
            result["uncertainty"]
        )

    def test_detected_transition_without_state_creates_uncertainty(self):
        result = estimate(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="none",
            ),
        )

        assert "detected_transition_without_state" in (
            result["uncertainty"]
        )

    def test_mixed_transition_direction_creates_uncertainty(self):
        result = estimate(
            transition=make_transition(
                detected=True,
                direction="mixed",
                state="moderate",
            ),
        )

        assert "mixed_transition_direction" in result["uncertainty"]

    @pytest.mark.parametrize("state", ["early", "moderate", "strong"])
    def test_detected_transition_adds_transition_reason(self, state):
        result = estimate(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state=state,
            ),
        )

        assert f"{state}_transition_detected" in result["reasons"]

    def test_unknown_regime_creates_uncertainty_and_very_low_confidence(
        self,
    ):
        result = estimate(regime="unknown_regime")

        assert "unknown_regime" in result["uncertainty"]
        assert result["state"] == "very_low"

    def test_neutral_regime_creates_uncertainty(self):
        result = estimate(regime="neutral")

        assert "neutral_regime" in result["uncertainty"]

    @pytest.mark.parametrize(
        "regime",
        [
            "expansion",
            "late_expansion",
            "slowdown",
            "stagnation",
            "recovery",
            "contraction",
            "neutral",
        ],
    )
    def test_valid_regimes_are_recognized(self, regime):
        result = estimate(regime=regime)

        assert f"regime_{regime}" in result["reasons"]
        assert "unknown_regime" not in result["uncertainty"]

    @pytest.mark.parametrize(
        ("field", "value", "expected"),
        [
            (
                "level",
                "unknown",
                "unknown_volatility_level",
            ),
            (
                "stress",
                "unknown",
                "unknown_volatility_stress",
            ),
            (
                "direction",
                "unknown",
                "unknown_volatility_direction",
            ),
        ],
    )
    def test_unknown_volatility_context_creates_uncertainty(
        self,
        field,
        value,
        expected,
    ):
        volatility = make_volatility()
        volatility[field] = value

        result = estimate(volatility=volatility)

        assert expected in result["uncertainty"]

    @pytest.mark.parametrize(
        ("field", "value", "expected"),
        [
            (
                "position",
                "unknown",
                "unknown_position",
            ),
            (
                "direction",
                "unknown",
                "unknown_position_direction",
            ),
        ],
    )
    def test_unknown_position_context_creates_uncertainty(
        self,
        field,
        value,
        expected,
    ):
        position = make_position()
        position[field] = value

        result = estimate(position=position)

        assert expected in result["uncertainty"]

    def test_one_contradiction_can_reduce_coherence_to_medium(
        self,
    ):
        result = estimate(
            growth=make_growth(state="positive"),
            trend=make_trend(state="bearish"),
            momentum=make_momentum(state="neutral"),
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="moderate",
            ),
        )

        assert "positive_growth_vs_bearish_trend" in (
            result["contradictions"]
        )
        assert len(result["contradictions"]) == 1
        assert result["coherence"] == "medium"

    def test_multiple_contradictions_reduce_coherence_to_low(self):
        result = estimate(
            growth=make_growth(state="positive"),
            trend=make_trend(state="bearish"),
            momentum=make_momentum(state="negative"),
        )

        assert len(result["contradictions"]) >= 2
        assert result["coherence"] == "low"
        assert result["state"] == "low"

    def test_three_or_more_contradictions_keep_coherence_low(self):
        result = estimate(
            growth=make_growth(state="positive"),
            trend=make_trend(state="bearish"),
            momentum=make_momentum(state="negative"),
        )

        assert len(result["contradictions"]) == 2
        assert result["coherence"] == "low"
        assert result["state"] == "low"

    def test_high_confidence_does_not_require_no_transition(self):
        result = estimate(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="strong",
            ),
        )

        assert result["state"] == "high"
        assert result["coherence"] == "high"
        assert "strong_transition_detected" in result["reasons"]

    def test_mixed_transition_prevents_high_confidence(self):
        result = estimate(
            transition=make_transition(
                detected=True,
                direction="mixed",
                state="moderate",
            ),
        )

        assert result["state"] != "high"
        assert "mixed_transition_direction" in result["uncertainty"]

    def test_unknown_core_state_reduces_confidence_to_low(self):
        result = estimate(
            growth=make_growth(state="unknown"),
        )

        assert result["state"] == "low"

    def test_many_uncertainties_reduce_confidence_to_low(self):
        result = estimate(
            growth=make_growth(
                direction="unknown",
                dynamic_state="unknown",
            ),
            trend=make_trend(
                direction="unknown",
                strength="unknown",
            ),
            momentum=make_momentum(direction="unknown"),
        )

        assert len(result["uncertainty"]) >= 5
        assert result["state"] == "low"

    def test_medium_coherence_without_strong_support_produces_low_confidence(
        self,
    ):
        result = estimate(
            growth=make_growth(direction="unknown"),
            trend=make_trend(direction="unknown"),
        )

        assert result["coherence"] == "medium"
        assert result["state"] == "moderate"

    def test_context_does_not_lower_confidence_just_because_volatility_is_high(
        self,
    ):
        result = estimate(
            volatility=make_volatility(
                level="extreme",
                stress="extreme",
                direction="rising",
            ),
        )

        assert result["state"] == "high"
        assert result["coherence"] == "high"

    def test_context_does_not_lower_confidence_just_because_position_is_extreme(
        self,
    ):
        result = estimate(
            position=make_position(
                position="extreme",
                direction="falling",
            ),
        )

        assert result["state"] == "high"
        assert result["coherence"] == "high"

    def test_reasons_include_supporting_dimension_count(self):
        result = estimate()

        assert "3_supporting_dimensions" in result["reasons"]

    def test_reasons_include_contradiction_count(self):
        result = estimate(
            trend=make_trend(state="bearish"),
        )

        assert any(
            reason.endswith("_cross_signal_contradictions")
            for reason in result["reasons"]
        )

    def test_reasons_include_uncertainty_count(self):
        result = estimate(
            growth=make_growth(
                direction="unknown",
                dynamic_state="unknown",
            ),
        )

        assert any(
            reason.endswith("_uncertainty_factors")
            for reason in result["reasons"]
        )

    def test_repeated_evidence_is_not_duplicated(self):
        result = estimate()

        evidence = result["supporting_evidence"]

        assert len(evidence) == len(set(evidence))

    def test_repeated_uncertainty_is_not_duplicated(self):
        result = estimate(
            growth=make_growth(state="unknown"),
        )

        uncertainty = result["uncertainty"]

        assert len(uncertainty) == len(set(uncertainty))

    def test_repeated_contradictions_are_not_duplicated(self):
        result = estimate(
            growth=make_growth(state="positive"),
            trend=make_trend(state="bearish"),
        )

        contradictions = result["contradictions"]

        assert len(contradictions) == len(set(contradictions))