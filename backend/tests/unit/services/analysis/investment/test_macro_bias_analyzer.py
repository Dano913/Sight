from __future__ import annotations

from app.services.analysis.investment.macro_bias_analyzer import (
    MacroBiasAnalyzer,
)


def make_environment(
    *,
    state="unknown",
    directional_bias="unknown",
    coherence="unknown",
):
    return {
        "state": state,
        "directional_bias": directional_bias,
        "coherence": coherence,
    }


def make_risk(*, state="unknown"):
    return {
        "state": state,
    }


def make_opportunity(*, state="uncertain"):
    return {
        "state": state,
    }


def make_transition(
    *,
    detected=False,
    direction="unknown",
    state="none",
):
    return {
        "detected": detected,
        "direction": direction,
        "state": state,
    }


def analyze(
    *,
    environment=None,
    risk=None,
    opportunity=None,
    signals=None,
    regime="unknown",
    transition=None,
):
    return MacroBiasAnalyzer.analyze(
        environment=environment or make_environment(),
        risk=risk or make_risk(),
        opportunity=opportunity or make_opportunity(),
        signals=signals or {},
        regime=regime,
        transition=transition or make_transition(),
    )


class TestMacroBiasAnalyzer:

    def test_returns_expected_structure(self):
        result = analyze()

        assert set(result) == {
            "state",
            "direction",
            "strength",
            "coherence",
            "reasons",
        }

    def test_reasons_are_unique(self):
        result = analyze(
            environment=make_environment(
                state="supportive",
                directional_bias="improving",
                coherence="high",
            ),
            opportunity=make_opportunity(
                state="established",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="strong",
            ),
        )

        assert len(result["reasons"]) == len(
            set(result["reasons"])
        )

    # ------------------------------------------------------------------
    # ENVIRONMENT / STATE
    # ------------------------------------------------------------------

    def test_supportive_environment_produces_supportive_state(self):
        result = analyze(
            environment=make_environment(
                state="supportive",
            )
        )

        assert result["state"] == "supportive"
        assert "supportive_environment" in result["reasons"]

    def test_challenging_environment_with_low_risk_is_cautious(self):
        result = analyze(
            environment=make_environment(
                state="challenging",
            ),
            risk=make_risk(
                state="moderate",
            ),
        )

        assert result["state"] == "cautious"
        assert "challenging_environment" in result["reasons"]

    def test_challenging_environment_with_high_risk_is_defensive(self):
        result = analyze(
            environment=make_environment(
                state="challenging",
            ),
            risk=make_risk(
                state="high",
            ),
        )

        assert result["state"] == "defensive"
        assert "high_macro_risk" in result["reasons"]

    def test_challenging_environment_with_extreme_risk_is_defensive(self):
        result = analyze(
            environment=make_environment(
                state="challenging",
            ),
            risk=make_risk(
                state="extreme",
            )
        )

        assert result["state"] == "defensive"
        assert "extreme_macro_risk" in result["reasons"]

    def test_challenging_environment_with_deteriorating_transition_is_defensive(
        self,
    ):
        result = analyze(
            environment=make_environment(
                state="challenging",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="moderate",
            ),
        )

        assert result["state"] == "defensive"

    def test_supportive_environment_with_deteriorating_transition_is_cautious(
        self,
    ):
        result = analyze(
            environment=make_environment(
                state="supportive",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_deterioration",
                state="strong",
            ),
        )

        assert result["state"] == "cautious"

    def test_supportive_environment_without_deterioration_is_supportive(
        self,
    ):
        result = analyze(
            environment=make_environment(
                state="supportive",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="moderate",
            ),
        )

        assert result["state"] == "supportive"

    def test_transitioning_environment_with_improving_transition_is_improving(
        self,
    ):
        result = analyze(
            environment=make_environment(
                state="transitioning",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_recovery",
                state="moderate",
            ),
        )

        assert result["state"] == "improving"

    def test_transitioning_environment_with_deteriorating_transition_is_deteriorating(
        self,
    ):
        result = analyze(
            environment=make_environment(
                state="transitioning",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_contraction",
                state="moderate",
            ),
        )

        assert result["state"] == "deteriorating"

    def test_transitioning_environment_without_direction_remains_transitioning(
        self,
    ):
        result = analyze(
            environment=make_environment(
                state="transitioning",
            )
        )

        assert result["state"] == "transitioning"

    def test_established_opportunity_without_high_risk_is_constructive(
        self,
    ):
        result = analyze(
            opportunity=make_opportunity(
                state="established",
            ),
            risk=make_risk(
                state="moderate",
            ),
        )

        assert result["state"] == "constructive"
        assert "established_macro_opportunity" in result["reasons"]

    def test_emerging_opportunity_without_high_risk_is_constructive(
        self,
    ):
        result = analyze(
            opportunity=make_opportunity(
                state="emerging",
            )
        )

        assert result["state"] == "constructive"
        assert "emerging_macro_opportunity" in result["reasons"]

    def test_high_risk_without_environmental_state_is_cautious(self):
        result = analyze(
            risk=make_risk(
                state="high",
            )
        )

        assert result["state"] == "cautious"

    def test_extreme_risk_without_environmental_state_is_cautious(self):
        result = analyze(
            risk=make_risk(
                state="extreme",
            )
        )

        assert result["state"] == "cautious"

    def test_neutral_context_without_opportunity_or_high_risk_is_neutral(
        self,
    ):
        result = analyze()

        assert result["state"] == "neutral"

    # ------------------------------------------------------------------
    # REASONS
    # ------------------------------------------------------------------

    def test_environment_reasons_are_generated(self):
        assert "supportive_environment" in analyze(
            environment=make_environment(
                state="supportive",
            )
        )["reasons"]

        assert "challenging_environment" in analyze(
            environment=make_environment(
                state="challenging",
            )
        )["reasons"]

        assert "transitioning_environment" in analyze(
            environment=make_environment(
                state="transitioning",
            )
        )["reasons"]

        assert "neutral_environment" in analyze(
            environment=make_environment(
                state="neutral",
            )
        )["reasons"]

    def test_risk_reasons_are_generated(self):
        assert "high_macro_risk" in analyze(
            risk=make_risk(state="high")
        )["reasons"]

        assert "elevated_macro_risk" in analyze(
            risk=make_risk(state="elevated")
        )["reasons"]

        assert "extreme_macro_risk" in analyze(
            risk=make_risk(state="extreme")
        )["reasons"]

        assert "moderate_macro_risk" in analyze(
            risk=make_risk(state="moderate")
        )["reasons"]

    def test_opportunity_reasons_are_generated(self):
        assert "established_macro_opportunity" in analyze(
            opportunity=make_opportunity(
                state="established"
            )
        )["reasons"]

        assert "emerging_macro_opportunity" in analyze(
            opportunity=make_opportunity(
                state="emerging"
            )
        )["reasons"]

        assert "supportive_macro_conditions" in analyze(
            opportunity=make_opportunity(
                state="supportive"
            )
        )["reasons"]

        assert "limited_macro_opportunity" in analyze(
            opportunity=make_opportunity(
                state="limited"
            )
        )["reasons"]

    # ------------------------------------------------------------------
    # TRANSITION
    # ------------------------------------------------------------------

    def test_detected_transition_adds_macro_transition_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="unknown",
                state="moderate",
            )
        )

        assert "macro_transition" in result["reasons"]

    def test_deteriorating_transition_adds_deterioration_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="moderate",
            )
        )

        assert "macro_deterioration_transition" in result["reasons"]

    def test_contraction_transition_adds_deterioration_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_contraction",
                state="moderate",
            )
        )

        assert "macro_deterioration_transition" in result["reasons"]

    def test_deterioration_transition_adds_deterioration_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_deterioration",
                state="moderate",
            )
        )

        assert "macro_deterioration_transition" in result["reasons"]

    def test_recovery_transition_adds_improvement_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_recovery",
                state="moderate",
            )
        )

        assert "macro_improvement_transition" in result["reasons"]

    def test_expansion_transition_adds_improvement_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="moderate",
            )
        )

        assert "macro_improvement_transition" in result["reasons"]

    def test_improvement_transition_adds_improvement_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_improvement",
                state="moderate",
            )
        )

        assert "macro_improvement_transition" in result["reasons"]

    def test_strong_transition_adds_strength_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="strong",
            )
        )

        assert "strong_macro_transition" in result["reasons"]

    def test_undetected_transition_does_not_add_transition_reason(self):
        result = analyze(
            transition=make_transition(
                detected=False,
                direction="toward_expansion",
                state="strong",
            )
        )

        assert "macro_transition" not in result["reasons"]
        assert "macro_improvement_transition" not in result["reasons"]
        assert "strong_macro_transition" not in result["reasons"]

    # ------------------------------------------------------------------
    # DIRECTION
    # ------------------------------------------------------------------

    def test_improving_transition_produces_improving_direction(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_recovery",
                state="moderate",
            )
        )

        assert result["direction"] == "improving"

    def test_deteriorating_transition_produces_deteriorating_direction(
        self,
    ):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="moderate",
            )
        )

        assert result["direction"] == "deteriorating"

    def test_environment_direction_is_used_without_transition(self):
        result = analyze(
            environment=make_environment(
                directional_bias="improving",
            )
        )

        assert result["direction"] == "improving"

    def test_deteriorating_environment_direction_is_used(self):
        result = analyze(
            environment=make_environment(
                directional_bias="deteriorating",
            )
        )

        assert result["direction"] == "deteriorating"

    def test_stable_environment_direction_is_used(self):
        result = analyze(
            environment=make_environment(
                directional_bias="stable",
            )
        )

        assert result["direction"] == "stable"

    def test_unknown_direction_is_returned_when_no_directional_information_exists(
        self,
    ):
        result = analyze()

        assert result["direction"] == "unknown"

    def test_transition_direction_has_priority_over_environment_direction(
        self,
    ):
        result = analyze(
            environment=make_environment(
                directional_bias="improving",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="moderate",
            ),
        )

        assert result["direction"] == "deteriorating"

    # ------------------------------------------------------------------
    # STRENGTH
    # ------------------------------------------------------------------

    def test_strong_transition_produces_strong_strength(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="strong",
            )
        )

        assert result["strength"] == "strong"

    def test_moderate_transition_produces_moderate_strength(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="moderate",
            )
        )

        assert result["strength"] == "moderate"

    def test_early_transition_produces_weak_strength(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="early",
            )
        )

        assert result["strength"] == "weak"

    def test_detected_transition_with_unknown_state_produces_weak_strength(
        self,
    ):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="unknown",
                state="unknown",
            )
        )

        assert result["strength"] == "weak"

    def test_no_transition_produces_unknown_strength(self):
        result = analyze()

        assert result["strength"] == "unknown"

    # ------------------------------------------------------------------
    # COHERENCE
    # ------------------------------------------------------------------

    def test_high_environment_coherence_is_preserved(self):
        result = analyze(
            environment=make_environment(
                coherence="high",
            )
        )

        assert result["coherence"] == "high"

    def test_medium_environment_coherence_is_preserved(self):
        result = analyze(
            environment=make_environment(
                coherence="medium",
            )
        )

        assert result["coherence"] == "medium"

    def test_low_environment_coherence_is_preserved(self):
        result = analyze(
            environment=make_environment(
                coherence="low",
            )
        )

        assert result["coherence"] == "low"

    def test_unknown_environment_coherence_becomes_unknown(self):
        result = analyze(
            environment=make_environment(
                coherence="invalid",
            )
        )

        assert result["coherence"] == "unknown"

    def test_regime_does_not_change_macro_bias(self):
        result_without_regime = analyze(
            regime="unknown",
        )

        result_with_regime = analyze(
            regime="expansion",
        )

        assert result_with_regime == result_without_regime

    def test_signals_do_not_change_macro_bias(self):
        result_without_signals = analyze(
            signals={},
        )

        result_with_signals = analyze(
            signals={
                "trend": {
                    "reversal": True,
                },
                "volatility": {
                    "shock": True,
                },
            },
        )

        assert result_with_signals == result_without_signals