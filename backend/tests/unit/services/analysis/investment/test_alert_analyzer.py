from app.services.analysis.investment.alert_analyzer import AlertAnalyzer


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
    signals=None,
    transition=None,
):
    return AlertAnalyzer.analyze(
        signals=signals or {},
        transition=transition or make_transition(),
    )


class TestAlertAnalyzer:
    def test_no_alerts_for_neutral_context(self):
        result = analyze()

        assert result == []

    # ----------------------------------------------------------
    # TRANSITION
    # ----------------------------------------------------------

    def test_slowdown_transition_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
            ),
        )

        assert result == [
            "transition_toward_slowdown",
        ]

    def test_contraction_transition_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_contraction",
            ),
        )

        assert result == [
            "transition_toward_contraction",
        ]

    def test_recovery_transition_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_recovery",
            ),
        )

        assert result == [
            "transition_toward_recovery",
        ]

    def test_expansion_transition_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
            ),
        )

        assert result == [
            "transition_toward_expansion",
        ]

    def test_improvement_transition_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_improvement",
            ),
        )

        assert result == [
            "transition_toward_improvement",
        ]

    def test_deterioration_transition_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_deterioration",
            ),
        )

        assert result == [
            "transition_toward_deterioration",
        ]

    def test_undetected_transition_generates_no_alert(self):
        result = analyze(
            transition=make_transition(
                detected=False,
                direction="toward_slowdown",
            ),
        )

        assert result == []

    def test_unknown_transition_direction_generates_no_direction_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="unknown",
            ),
        )

        assert result == []

    # ----------------------------------------------------------
    # TRANSITION INTENSITY
    # ----------------------------------------------------------

    def test_strong_transition_alert(self):
        result = analyze(
            transition=make_transition(
                detected=False,
                state="strong",
            ),
        )

        assert result == [
            "strong_macro_transition",
        ]

    def test_moderate_transition_alert(self):
        result = analyze(
            transition=make_transition(
                detected=False,
                state="moderate",
            ),
        )

        assert result == [
            "moderate_macro_transition",
        ]

    def test_weak_transition_generates_no_intensity_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="weak",
            ),
        )

        assert result == [
            "transition_toward_slowdown",
        ]

    # ----------------------------------------------------------
    # COMBINED TRANSITION CONDITIONS
    # ----------------------------------------------------------

    def test_strong_slowdown_generates_deterioration_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="strong",
            ),
        )

        assert result == [
            "transition_toward_slowdown",
            "strong_macro_transition",
            "macro_deterioration_transition",
        ]

    def test_moderate_slowdown_generates_deterioration_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="moderate",
            ),
        )

        assert result == [
            "transition_toward_slowdown",
            "moderate_macro_transition",
            "macro_deterioration_transition",
        ]

    def test_strong_contraction_generates_deterioration_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_contraction",
                state="strong",
            ),
        )

        assert result == [
            "transition_toward_contraction",
            "strong_macro_transition",
            "macro_deterioration_transition",
        ]

    def test_strong_recovery_generates_improvement_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_recovery",
                state="strong",
            ),
        )

        assert result == [
            "transition_toward_recovery",
            "strong_macro_transition",
            "macro_improvement_transition",
        ]

    def test_moderate_expansion_generates_improvement_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_expansion",
                state="moderate",
            ),
        )

        assert result == [
            "transition_toward_expansion",
            "moderate_macro_transition",
            "macro_improvement_transition",
        ]

    def test_improvement_transition_does_not_generate_improvement_group_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_improvement",
                state="strong",
            ),
        )

        assert result == [
            "transition_toward_improvement",
            "strong_macro_transition",
        ]

    def test_deterioration_transition_does_not_generate_deterioration_group_alert(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_deterioration",
                state="strong",
            ),
        )

        assert result == [
            "transition_toward_deterioration",
            "strong_macro_transition",
        ]

    # ----------------------------------------------------------
    # SIGNAL EVENTS
    # ----------------------------------------------------------

    def test_trend_reversal_alert(self):
        result = analyze(
            signals={
                "trend": {
                    "reversal": True,
                },
            },
        )

        assert result == [
            "trend_reversal",
        ]

    def test_trend_without_reversal_generates_no_alert(self):
        result = analyze(
            signals={
                "trend": {
                    "reversal": False,
                },
            },
        )

        assert result == []

    def test_volatility_shock_alert(self):
        result = analyze(
            signals={
                "volatility": {
                    "shock": True,
                },
            },
        )

        assert result == [
            "volatility_shock",
        ]

    def test_volatility_without_shock_generates_no_alert(self):
        result = analyze(
            signals={
                "volatility": {
                    "shock": False,
                },
            },
        )

        assert result == []

    def test_severe_drawdown_alert(self):
        result = analyze(
            signals={
                "position": {
                    "severe_drawdown": True,
                },
            },
        )

        assert result == [
            "severe_drawdown",
        ]

    def test_non_severe_drawdown_generates_no_alert(self):
        result = analyze(
            signals={
                "position": {
                    "severe_drawdown": False,
                },
            },
        )

        assert result == []

    # ----------------------------------------------------------
    # COMBINED SIGNALS
    # ----------------------------------------------------------

    def test_multiple_signal_events(self):
        result = analyze(
            signals={
                "trend": {
                    "reversal": True,
                },
                "volatility": {
                    "shock": True,
                },
                "position": {
                    "severe_drawdown": True,
                },
            },
        )

        assert result == [
            "trend_reversal",
            "volatility_shock",
            "severe_drawdown",
        ]

    # ----------------------------------------------------------
    # COMBINED TRANSITION AND SIGNALS
    # ----------------------------------------------------------

    def test_full_deterioration_context(self):
        result = analyze(
            signals={
                "trend": {
                    "reversal": True,
                },
                "volatility": {
                    "shock": True,
                },
                "position": {
                    "severe_drawdown": True,
                },
            },
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="strong",
            ),
        )

        assert result == [
            "transition_toward_slowdown",
            "strong_macro_transition",
            "macro_deterioration_transition",
            "trend_reversal",
            "volatility_shock",
            "severe_drawdown",
        ]

    # ----------------------------------------------------------
    # DEDUPLICATION
    # ----------------------------------------------------------

    def test_alerts_are_unique(self):
        result = analyze(
            signals={
                "trend": {
                    "reversal": True,
                },
            },
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="strong",
            ),
        )

        assert len(result) == len(set(result))