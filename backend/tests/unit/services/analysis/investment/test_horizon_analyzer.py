from __future__ import annotations

from app.services.analysis.investment.horizon_analyzer import HorizonAnalyzer


def make_environment(
    *,
    state="unknown",
    directional_bias="unknown",
    coherence="unknown",
    volatility=None,
):
    return {
        "state": state,
        "directional_bias": directional_bias,
        "coherence": coherence,
        "context": {
            "volatility": volatility or {},
        },
    }


def make_risk(*, state="unknown"):
    return {
        "state": state,
    }


def make_opportunity():
    return {
        "state": "uncertain",
    }


def make_signals():
    return {}


def make_transition(
    *,
    direction="unknown",
    state="none",
):
    return {
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
    return HorizonAnalyzer.analyze(
        environment=environment or make_environment(),
        risk=risk or make_risk(),
        opportunity=opportunity or make_opportunity(),
        signals=signals or make_signals(),
        regime=regime,
        transition=transition or make_transition(),
    )


class TestHorizonAnalyzer:

    def test_returns_expected_horizons(self):
        result = analyze()

        assert set(result) == {
            "short_term",
            "medium_term",
            "long_term",
        }

    def test_all_horizons_return_strings(self):
        result = analyze()

        assert all(isinstance(value, str) for value in result.values())

    # ------------------------------------------------------------------
    # SHORT TERM
    # ------------------------------------------------------------------

    def test_short_term_deteriorating_on_moderate_slowdown_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_slowdown",
                state="moderate",
            )
        )

        assert result["short_term"] == "deteriorating"

    def test_short_term_deteriorating_on_strong_contraction_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_contraction",
                state="strong",
            )
        )

        assert result["short_term"] == "deteriorating"

    def test_short_term_deteriorating_on_deterioration_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_deterioration",
                state="moderate",
            )
        )

        assert result["short_term"] == "deteriorating"

    def test_short_term_improving_on_moderate_recovery_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_recovery",
                state="moderate",
            )
        )

        assert result["short_term"] == "improving"

    def test_short_term_improving_on_strong_expansion_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_expansion",
                state="strong",
            )
        )

        assert result["short_term"] == "improving"

    def test_short_term_improving_on_improvement_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_improvement",
                state="moderate",
            )
        )

        assert result["short_term"] == "improving"

    def test_short_term_volatility_is_detected(self):
        result = analyze(
            environment=make_environment(
                volatility={
                    "level": "high",
                    "direction": "stable",
                    "stress": "elevated",
                }
            )
        )

        assert result["short_term"] == "volatile"

    def test_short_term_extreme_volatility_is_detected(self):
        result = analyze(
            environment=make_environment(
                volatility={
                    "level": "extreme",
                    "direction": "stable",
                    "stress": "unknown",
                }
            )
        )

        assert result["short_term"] == "volatile"

    def test_short_term_rising_volatility_is_detected(self):
        result = analyze(
            environment=make_environment(
                volatility={
                    "level": "normal",
                    "direction": "rising",
                    "stress": "normal",
                }
            )
        )

        assert result["short_term"] == "volatile"

    def test_short_term_high_risk_is_fragile(self):
        result = analyze(
            risk=make_risk(state="high")
        )

        assert result["short_term"] == "fragile"

    def test_short_term_extreme_risk_is_fragile(self):
        result = analyze(
            risk=make_risk(state="extreme")
        )

        assert result["short_term"] == "fragile"

    def test_short_term_early_transition_is_transitioning(self):
        result = analyze(
            transition=make_transition(
                direction="toward_recovery",
                state="early",
            )
        )

        assert result["short_term"] == "transitioning"

    def test_short_term_defaults_to_stable(self):
        result = analyze()

        assert result["short_term"] == "stable"

    def test_short_term_transition_has_priority_over_volatility(self):
        result = analyze(
            environment=make_environment(
                volatility={
                    "level": "extreme",
                    "direction": "rising",
                    "stress": "extreme",
                }
            ),
            transition=make_transition(
                direction="toward_slowdown",
                state="strong",
            ),
        )

        assert result["short_term"] == "deteriorating"

    def test_short_term_transition_has_priority_over_high_risk(self):
        result = analyze(
            risk=make_risk(state="extreme"),
            transition=make_transition(
                direction="toward_recovery",
                state="strong",
            ),
        )

        assert result["short_term"] == "improving"

    # ------------------------------------------------------------------
    # MEDIUM TERM
    # ------------------------------------------------------------------

    def test_medium_term_deteriorating_on_slowdown_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_slowdown",
                state="moderate",
            )
        )

        assert result["medium_term"] == "deteriorating"

    def test_medium_term_deteriorating_on_contraction_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_contraction",
                state="strong",
            )
        )

        assert result["medium_term"] == "deteriorating"

    def test_medium_term_improving_on_recovery_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_recovery",
                state="moderate",
            )
        )

        assert result["medium_term"] == "improving"

    def test_medium_term_improving_on_expansion_transition(self):
        result = analyze(
            transition=make_transition(
                direction="toward_expansion",
                state="strong",
            )
        )

        assert result["medium_term"] == "improving"

    def test_medium_term_challenging_environment_is_weak(self):
        result = analyze(
            environment=make_environment(
                state="challenging"
            )
        )

        assert result["medium_term"] == "weak"

    def test_medium_term_supportive_environment_is_supportive(self):
        result = analyze(
            environment=make_environment(
                state="supportive"
            )
        )

        assert result["medium_term"] == "supportive"

    def test_medium_term_transitioning_environment_is_transitioning(self):
        result = analyze(
            environment=make_environment(
                state="transitioning"
            )
        )

        assert result["medium_term"] == "transitioning"

    def test_medium_term_improving_direction_is_improving(self):
        result = analyze(
            environment=make_environment(
                directional_bias="improving"
            )
        )

        assert result["medium_term"] == "improving"

    def test_medium_term_deteriorating_direction_is_deteriorating(self):
        result = analyze(
            environment=make_environment(
                directional_bias="deteriorating"
            )
        )

        assert result["medium_term"] == "deteriorating"

    def test_medium_term_defaults_to_stable(self):
        result = analyze()

        assert result["medium_term"] == "stable"

    def test_medium_term_transition_has_priority_over_environment_state(self):
        result = analyze(
            environment=make_environment(
                state="supportive"
            ),
            transition=make_transition(
                direction="toward_slowdown",
                state="strong",
            ),
        )

        assert result["medium_term"] == "deteriorating"

    # ------------------------------------------------------------------
    # LONG TERM
    # ------------------------------------------------------------------

    def test_long_term_contraction_regime_is_contracting(self):
        result = analyze(regime="contraction")

        assert result["long_term"] == "contracting"

    def test_long_term_slowdown_regime_is_slowing(self):
        result = analyze(regime="slowdown")

        assert result["long_term"] == "slowing"

    def test_long_term_stagnation_regime_is_stagnant(self):
        result = analyze(regime="stagnation")

        assert result["long_term"] == "stagnant"

    def test_long_term_recovery_regime_is_recovering(self):
        result = analyze(regime="recovery")

        assert result["long_term"] == "recovering"

    def test_long_term_expansion_regime_is_expanding(self):
        result = analyze(regime="expansion")

        assert result["long_term"] == "expanding"

    def test_long_term_late_expansion_regime_is_maturing(self):
        result = analyze(regime="late_expansion")

        assert result["long_term"] == "maturing"

    def test_long_term_challenging_environment_is_weak(self):
        result = analyze(
            environment=make_environment(
                state="challenging"
            )
        )

        assert result["long_term"] == "weak"

    def test_long_term_supportive_environment_is_supportive(self):
        result = analyze(
            environment=make_environment(
                state="supportive"
            )
        )

        assert result["long_term"] == "supportive"

    def test_long_term_low_coherence_is_uncertain(self):
        result = analyze(
            environment=make_environment(
                coherence="low"
            )
        )

        assert result["long_term"] == "uncertain"

    def test_long_term_defaults_to_stable(self):
        result = analyze()

        assert result["long_term"] == "stable"

    def test_long_term_regime_has_priority_over_environment_state(self):
        result = analyze(
            environment=make_environment(
                state="challenging",
                coherence="low",
            ),
            regime="expansion",
        )

        assert result["long_term"] == "expanding"