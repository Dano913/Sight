from app.services.analysis.investment.conviction_analyzer import ConvictionAnalyzer


def make_environment(
    *,
    state="unknown",
    coherence="unknown",
):
    return {
        "state": state,
        "coherence": coherence,
    }


def make_risk(
    *,
    state="unknown",
):
    return {
        "state": state,
    }


def make_opportunity(
    *,
    state="uncertain",
):
    return {
        "state": state,
    }


def make_confidence(
    *,
    state="very_low",
    coherence="medium",
):
    return {
        "state": state,
        "coherence": coherence,
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
    confidence=None,
    transition=None,
):
    return ConvictionAnalyzer.analyze(
        environment=environment or make_environment(),
        risk=risk or make_risk(),
        opportunity=opportunity or make_opportunity(),
        confidence=confidence or make_confidence(),
        transition=transition or make_transition(),
    )


class TestConvictionAnalyzer:
    # ----------------------------------------------------------
    # BASIC CONTRACT
    # ----------------------------------------------------------

    def test_returns_expected_structure(self):
        result = analyze()

        assert set(result) == {
            "state",
            "coherence",
            "reasons",
            "contradictions",
        }

        assert isinstance(result["state"], str)
        assert isinstance(result["coherence"], str)
        assert isinstance(result["reasons"], list)
        assert isinstance(result["contradictions"], list)

    def test_neutral_context_has_very_low_conviction(self):
        result = analyze()

        assert result["state"] == "very_low"
    # ----------------------------------------------------------
    # CONFIDENCE / COHERENCE
    # ----------------------------------------------------------

    def test_high_confidence_and_high_coherence_produce_high_conviction(self):
        result = analyze(
            confidence=make_confidence(
                state="high",
                coherence="high",
            ),
            environment=make_environment(
                state="supportive",
                coherence="high",
            ),
            risk=make_risk(
                state="low",
            ),
            opportunity=make_opportunity(
                state="established",
            ),
        )

        assert result["state"] == "high"
        assert "high_interpretation_clarity" in result["reasons"]
        assert "high_cross_dimension_coherence" in result["reasons"]
        assert "coherent_environment" in result["reasons"]

    def test_moderate_confidence_and_high_coherence_produce_moderate_conviction(self):
        result = analyze(
            confidence=make_confidence(
                state="moderate",
                coherence="high",
            ),
            environment=make_environment(
                state="supportive",
                coherence="medium",
            ),
        )

        assert result["state"] == "moderate"

    def test_low_confidence_produces_low_conviction(self):
        result = analyze(
            confidence=make_confidence(
                state="low",
                coherence="medium",
            ),
            environment=make_environment(
                coherence="medium",
            ),
        )

        assert result["state"] == "low"
        assert "limited_interpretation_clarity" in result["reasons"]

    def test_very_low_confidence_produces_very_low_conviction_without_contradictions(self):
        result = analyze(
            confidence=make_confidence(
                state="very_low",
                coherence="medium",
            ),
            environment=make_environment(
                coherence="medium",
            ),
        )

        assert result["state"] == "very_low"
        assert result["contradictions"] == []

    # ----------------------------------------------------------
    # CROSS-DIMENSION COHERENCE
    # ----------------------------------------------------------

    def test_medium_coherence_produces_moderate_coherence_reason(self):
        result = analyze(
            confidence=make_confidence(
                state="moderate",
                coherence="medium",
            ),
        )

        assert "moderate_cross_dimension_coherence" in result["reasons"]

    def test_low_coherence_creates_contradiction(self):
        result = analyze(
            confidence=make_confidence(
                state="high",
                coherence="low",
            ),
        )

        assert "low_cross_dimension_coherence" in result["contradictions"]
        assert result["state"] == "low"

    # ----------------------------------------------------------
    # ENVIRONMENT
    # ----------------------------------------------------------

    def test_high_environment_coherence_adds_reason(self):
        result = analyze(
            confidence=make_confidence(
                state="moderate",
                coherence="high",
            ),
            environment=make_environment(
                coherence="high",
            ),
        )

        assert "coherent_environment" in result["reasons"]

    def test_low_environment_coherence_creates_contradiction(self):
        result = analyze(
            confidence=make_confidence(
                state="high",
                coherence="high",
            ),
            environment=make_environment(
                coherence="low",
            ),
        )

        assert "environment_uncertainty" in result["contradictions"]
        assert result["state"] == "low"

    # ----------------------------------------------------------
    # ENVIRONMENT / RISK / OPPORTUNITY
    # ----------------------------------------------------------

    def test_supportive_environment_aligns_with_low_risk(self):
        result = analyze(
            environment=make_environment(
                state="supportive",
                coherence="high",
            ),
            risk=make_risk(
                state="low",
            ),
            opportunity=make_opportunity(
                state="established",
            ),
            confidence=make_confidence(
                state="moderate",
                coherence="high",
            ),
        )

        assert "environment_risk_alignment" in result["reasons"]

    def test_challenging_environment_aligns_with_high_risk(self):
        result = analyze(
            environment=make_environment(
                state="challenging",
                coherence="high",
            ),
            risk=make_risk(
                state="high",
            ),
            confidence=make_confidence(
                state="moderate",
                coherence="high",
            ),
        )

        assert "environment_risk_alignment" in result["reasons"]

    def test_challenging_environment_aligns_with_extreme_risk(self):
        result = analyze(
            environment=make_environment(
                state="challenging",
                coherence="high",
            ),
            risk=make_risk(
                state="extreme",
            ),
            confidence=make_confidence(
                state="moderate",
                coherence="high",
            ),
        )

        assert "environment_risk_alignment" in result["reasons"]

    def test_supportive_environment_with_extreme_risk_creates_contradiction(self):
        result = analyze(
            environment=make_environment(
                state="supportive",
                coherence="high",
            ),
            risk=make_risk(
                state="extreme",
            ),
            confidence=make_confidence(
                state="high",
                coherence="high",
            ),
        )

        assert (
            "supportive_environment_with_extreme_risk"
            in result["contradictions"]
        )

        assert result["state"] == "low"

    def test_challenging_environment_with_supportive_opportunity_creates_contradiction(
        self,
    ):
        result = analyze(
            environment=make_environment(
                state="challenging",
                coherence="high",
            ),
            opportunity=make_opportunity(
                state="supportive",
            ),
            confidence=make_confidence(
                state="high",
                coherence="high",
            ),
        )

        assert (
            "challenging_environment_with_supportive_opportunity"
            in result["contradictions"]
        )

        assert result["state"] == "low"

    # ----------------------------------------------------------
    # TRANSITION
    # ----------------------------------------------------------

    def test_strong_transition_adds_clear_transition_reason(self):
        result = analyze(
            confidence=make_confidence(
                state="moderate",
                coherence="high",
            ),
            environment=make_environment(
                coherence="high",
            ),
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="strong",
            ),
        )

        assert "clear_transition_evidence" in result["reasons"]

    def test_moderate_transition_adds_moderate_transition_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_slowdown",
                state="moderate",
            ),
        )

        assert "moderate_transition_evidence" in result["reasons"]

    def test_early_transition_adds_early_transition_reason(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="toward_recovery",
                state="early",
            ),
        )

        assert "early_transition_evidence" in result["reasons"]

    def test_unknown_transition_direction_creates_contradiction(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="unknown",
                state="moderate",
            ),
        )

        assert "transition_direction_unclear" in result["contradictions"]
        assert result["state"] == "low"

    def test_mixed_transition_direction_creates_contradiction(self):
        result = analyze(
            transition=make_transition(
                detected=True,
                direction="mixed",
                state="moderate",
            ),
        )

        assert "mixed_transition_direction" in result["contradictions"]
        assert result["state"] == "low"

    def test_undetected_transition_adds_no_transition_reason(self):
        result = analyze(
            transition=make_transition(
                detected=False,
                direction="toward_slowdown",
                state="strong",
            ),
        )

        assert "clear_transition_evidence" not in result["reasons"]
        assert "moderate_transition_evidence" not in result["reasons"]
        assert "early_transition_evidence" not in result["reasons"]

    # ----------------------------------------------------------
    # RISK / OPPORTUNITY SEPARATION
    # ----------------------------------------------------------

    def test_high_risk_does_not_reduce_interpretation_clarity(self):
        result = analyze(
            risk=make_risk(
                state="high",
            ),
            confidence=make_confidence(
                state="moderate",
                coherence="high",
            ),
        )

        assert (
            "high_risk_does_not_reduce_interpretation_clarity"
            in result["reasons"]
        )

    def test_extreme_risk_does_not_reduce_interpretation_clarity(self):
        result = analyze(
            risk=make_risk(
                state="extreme",
            ),
            confidence=make_confidence(
                state="moderate",
                coherence="high",
            ),
        )

        assert (
            "high_risk_does_not_reduce_interpretation_clarity"
            in result["reasons"]
        )

    def test_established_opportunity_adds_opportunity_evidence(self):
        result = analyze(
            opportunity=make_opportunity(
                state="established",
            ),
        )

        assert (
            "macro_opportunity_evidence_present"
            in result["reasons"]
        )

    def test_emerging_opportunity_adds_opportunity_evidence(self):
        result = analyze(
            opportunity=make_opportunity(
                state="emerging",
            ),
        )

        assert (
            "macro_opportunity_evidence_present"
            in result["reasons"]
        )

    # ----------------------------------------------------------
    # STATE PRIORITY
    # ----------------------------------------------------------

    def test_contradictions_force_low_state(self):
        result = analyze(
            confidence=make_confidence(
                state="high",
                coherence="low",
            ),
            environment=make_environment(
                coherence="low",
            ),
        )

        assert result["state"] == "low"
        assert result["contradictions"]

    def test_high_state_requires_high_confidence_high_coherence_and_good_environment(
        self,
    ):
        result = analyze(
            confidence=make_confidence(
                state="high",
                coherence="high",
            ),
            environment=make_environment(
                coherence="high",
            ),
        )

        assert result["state"] == "high"

    # ----------------------------------------------------------
    # DEDUPLICATION
    # ----------------------------------------------------------

    def test_reasons_are_unique(self):
        result = analyze(
            confidence=make_confidence(
                state="high",
                coherence="high",
            ),
            environment=make_environment(
                state="supportive",
                coherence="high",
            ),
            risk=make_risk(
                state="low",
            ),
            opportunity=make_opportunity(
                state="established",
            ),
        )

        assert len(result["reasons"]) == len(
            set(result["reasons"])
        )

    def test_contradictions_are_unique(self):
        result = analyze(
            confidence=make_confidence(
                state="high",
                coherence="low",
            ),
            environment=make_environment(
                coherence="low",
            ),
        )

        assert len(result["contradictions"]) == len(
            set(result["contradictions"])
        )