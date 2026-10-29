from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.analysis.investment.investment_analysis_service import (
    InvestmentAnalysisService,
)


def make_environment():
    return {
        "state": "supportive",
        "directional_bias": "improving",
        "coherence": "high",
    }


def make_risk():
    return {
        "state": "moderate",
    }


def make_opportunity():
    return {
        "state": "emerging",
    }


def make_transition():
    return {
        "detected": True,
        "direction": "toward_expansion",
        "state": "moderate",
    }


def make_signals():
    return {
        "trend": {
            "reversal": False,
        },
        "volatility": {
            "shock": False,
        },
        "position": {
            "severe_drawdown": False,
        },
    }


def make_confidence():
    return {
        "state": "high",
        "coherence": "high",
    }


def make_interpretation():
    return {
        "indicator": "GDP",
        "region": "DE",
        "date": "2026-09-01",
        "regime": "expansion",
        "environment": make_environment(),
        "risk": make_risk(),
        "opportunity": make_opportunity(),
        "transition": make_transition(),
        "signals": make_signals(),
        "confidence": make_confidence(),
    }


def test_returns_expected_top_level_structure():
    result = InvestmentAnalysisService.analyze(
        make_interpretation()
    )

    assert set(result) == {
        "indicator",
        "region",
        "date",
        "regime",
        "overall",
        "environment",
        "risk",
        "opportunity",
        "macro_bias",
        "transition",
        "horizon",
        "conviction",
        "alerts",
        "signals",
        "confidence",
    }


def test_preserves_original_context():
    interpretation = make_interpretation()

    result = InvestmentAnalysisService.analyze(
        interpretation
    )

    assert result["indicator"] == "GDP"
    assert result["region"] == "DE"
    assert result["date"] == "2026-09-01"
    assert result["regime"] == "expansion"

    assert result["environment"] is interpretation["environment"]
    assert result["risk"] is interpretation["risk"]
    assert result["opportunity"] is interpretation["opportunity"]
    assert result["transition"] is interpretation["transition"]
    assert result["signals"] is interpretation["signals"]
    assert result["confidence"] is interpretation["confidence"]


def test_orchestrates_all_components():
    interpretation = make_interpretation()

    macro_bias = {
        "state": "supportive",
        "direction": "improving",
        "strength": "moderate",
        "coherence": "high",
        "reasons": ["supportive_environment"],
    }

    horizon = {
        "short_term": "improving",
        "medium_term": "supportive",
        "long_term": "expanding",
    }

    alerts = [
        "transition_toward_expansion",
        "moderate_macro_transition",
        "macro_improvement_transition",
    ]

    conviction = {
        "state": "high",
        "coherence": "high",
        "reasons": ["high_interpretation_clarity"],
        "contradictions": [],
    }

    overall = {
        "assessment": "supportive",
        "direction": "improving",
        "strength": "moderate",
        "coherence": "high",
        "macro_bias": "supportive",
        "conviction": "high",
        "confidence": "high",
        "environment": "supportive",
        "risk": "moderate",
        "opportunity": "emerging",
        "transition": {
            "detected": True,
            "direction": "toward_expansion",
            "state": "moderate",
        },
        "reasons": ["supportive_environment"],
    }

    with (
        patch(
            "app.services.analysis.investment.investment_analysis_service."
            "MacroBiasAnalyzer.analyze",
            return_value=macro_bias,
        ) as mock_macro_bias,
        patch(
            "app.services.analysis.investment.investment_analysis_service."
            "HorizonAnalyzer.analyze",
            return_value=horizon,
        ) as mock_horizon,
        patch(
            "app.services.analysis.investment.investment_analysis_service."
            "AlertAnalyzer.analyze",
            return_value=alerts,
        ) as mock_alerts,
        patch(
            "app.services.analysis.investment.investment_analysis_service."
            "ConvictionAnalyzer.analyze",
            return_value=conviction,
        ) as mock_conviction,
        patch(
            "app.services.analysis.investment.investment_analysis_service."
            "OverallAssessmentBuilder.build",
            return_value=overall,
        ) as mock_overall,
    ):
        result = InvestmentAnalysisService.analyze(
            interpretation
        )

    mock_macro_bias.assert_called_once_with(
        environment=interpretation["environment"],
        risk=interpretation["risk"],
        opportunity=interpretation["opportunity"],
        signals=interpretation["signals"],
        regime=interpretation["regime"],
        transition=interpretation["transition"],
    )

    mock_horizon.assert_called_once_with(
        environment=interpretation["environment"],
        risk=interpretation["risk"],
        opportunity=interpretation["opportunity"],
        signals=interpretation["signals"],
        regime=interpretation["regime"],
        transition=interpretation["transition"],
    )

    mock_alerts.assert_called_once_with(
        signals=interpretation["signals"],
        transition=interpretation["transition"],
    )

    mock_conviction.assert_called_once_with(
        environment=interpretation["environment"],
        risk=interpretation["risk"],
        opportunity=interpretation["opportunity"],
        confidence=interpretation["confidence"],
        transition=interpretation["transition"],
    )

    mock_overall.assert_called_once_with(
        environment=interpretation["environment"],
        risk=interpretation["risk"],
        opportunity=interpretation["opportunity"],
        confidence=interpretation["confidence"],
        macro_bias=macro_bias,
        conviction=conviction,
        transition=interpretation["transition"],
    )

    assert result["macro_bias"] is macro_bias
    assert result["horizon"] is horizon
    assert result["alerts"] is alerts
    assert result["conviction"] is conviction
    assert result["overall"] is overall


def test_optional_metadata_can_be_missing():
    interpretation = make_interpretation()

    interpretation.pop("indicator")
    interpretation.pop("region")
    interpretation.pop("date")

    result = InvestmentAnalysisService.analyze(
        interpretation
    )

    assert result["indicator"] is None
    assert result["region"] is None
    assert result["date"] is None


def test_validation_rejects_non_dict():
    with pytest.raises(
        TypeError,
        match="investment_interpretation debe ser un dict",
    ):
        InvestmentAnalysisService.analyze(None)


def test_validation_requires_all_sections():
    interpretation = make_interpretation()

    interpretation.pop("transition")

    with pytest.raises(
        ValueError,
        match="Faltan secciones necesarias",
    ):
        InvestmentAnalysisService.analyze(
            interpretation
        )


@pytest.mark.parametrize(
    "section",
    [
        "environment",
        "risk",
        "opportunity",
        "transition",
        "signals",
        "confidence",
    ],
)
def test_validation_requires_dictionary_sections(section):
    interpretation = make_interpretation()
    interpretation[section] = "invalid"

    with pytest.raises(
        TypeError,
        match=rf"La sección '{section}' debe ser un dict",
    ):
        InvestmentAnalysisService.analyze(
            interpretation
        )


def test_validation_requires_regime_to_be_string():
    interpretation = make_interpretation()
    interpretation["regime"] = {
        "state": "expansion",
    }

    with pytest.raises(
        TypeError,
        match="La sección 'regime' debe ser un str",
    ):
        InvestmentAnalysisService.analyze(
            interpretation
        )


def test_validation_accepts_extra_sections():
    interpretation = make_interpretation()
    interpretation["extra"] = {
        "value": 123,
    }

    result = InvestmentAnalysisService.analyze(
        interpretation
    )

    assert result["regime"] == "expansion"