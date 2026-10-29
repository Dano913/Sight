from unittest.mock import patch

import pytest

from app.services.interpretation.investment.investment_interpretation_service import (
    InvestmentInterpretationService,
)


def make_input():
    return {
        "indicator": "GDP",
        "region": "ES",
        "date": "2026-08-01",
        "growth": {
            "state": "positive",
            "accelerating": True,
        },
        "trend": {
            "state": "bullish",
            "reversal": False,
        },
        "momentum": {
            "state": "positive_accelerating",
        },
        "volatility": {
            "state": "stable",
        },
        "position": {
            "state": "neutral",
        },
        "transition": {
            "state": "none",
            "direction": None,
        },
        "regime": "expansion",
    }


def test_analyze_returns_expected_structure():
    interpretation = make_input()

    result = InvestmentInterpretationService.analyze(
        interpretation
    )

    assert set(result) == {
        "indicator",
        "region",
        "date",
        "regime",
        "transition",
        "environment",
        "risk",
        "opportunity",
        "signals",
        "confidence",
    }


def test_analyze_preserves_metadata():
    economic_interpretation = make_input()

    result = InvestmentInterpretationService.analyze(
        economic_interpretation
    )

    assert result["indicator"] == "GDP"
    assert result["region"] == "ES"
    assert result["date"] == "2026-08-01"
    assert result["regime"] == "expansion"


def test_analyze_calls_all_interpreters():
    economic_interpretation = make_input()

    with (
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.EnvironmentInterpreter.interpret"
        ) as environment,
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.RiskInterpreter.interpret"
        ) as risk,
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.OpportunityInterpreter.interpret"
        ) as opportunity,
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.SignalGenerator.generate"
        ) as signals,
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.ConfidenceEstimator.estimate"
        ) as confidence,
    ):
        environment.return_value = {
            "state": "favorable",
            "score": 5,
            "reasons": [],
        }

        risk.return_value = {
            "state": "low",
            "score": 0,
            "reasons": [],
        }

        opportunity.return_value = {
            "state": "moderate",
            "score": 4,
            "reasons": [],
        }

        signals.return_value = {
            "growth_supportive": True,
        }

        confidence.return_value = {
            "state": "high",
            "score": 8,
            "reasons": [],
        }

        result = InvestmentInterpretationService.analyze(
            economic_interpretation
        )

    environment.assert_called_once()
    risk.assert_called_once()
    opportunity.assert_called_once()
    signals.assert_called_once()
    confidence.assert_called_once()

    assert result["environment"]["state"] == "favorable"
    assert result["risk"]["state"] == "low"
    assert result["opportunity"]["state"] == "moderate"
    assert result["signals"]["growth_supportive"] is True
    assert result["confidence"]["state"] == "high"


def test_all_interpreters_receive_same_sections():
    economic_interpretation = make_input()

    with (
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.EnvironmentInterpreter.interpret"
        ) as environment,
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.RiskInterpreter.interpret"
        ) as risk,
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.OpportunityInterpreter.interpret"
        ) as opportunity,
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.SignalGenerator.generate"
        ) as signals,
        patch(
            "app.services.interpretation.investment."
            "investment_interpretation_service.ConfidenceEstimator.estimate"
        ) as confidence,
    ):
        environment.return_value = {}
        risk.return_value = {}
        opportunity.return_value = {}
        signals.return_value = {}
        confidence.return_value = {}

        InvestmentInterpretationService.analyze(
            economic_interpretation
        )

    expected = {
        "growth": economic_interpretation["growth"],
        "trend": economic_interpretation["trend"],
        "momentum": economic_interpretation["momentum"],
        "volatility": economic_interpretation["volatility"],
        "position": economic_interpretation["position"],
        "transition": economic_interpretation["transition"],
        "regime": economic_interpretation["regime"],
    }

    environment.assert_called_once_with(**expected)
    risk.assert_called_once_with(**expected)
    opportunity.assert_called_once_with(**expected)
    signals.assert_called_once_with(**expected)
    confidence.assert_called_once_with(**expected)


@pytest.mark.parametrize(
    "missing_section",
    [
        "growth",
        "trend",
        "momentum",
        "volatility",
        "position",
        "transition",
        "regime",
    ],
)
def test_missing_required_section_raises_error(
    missing_section,
):
    economic_interpretation = make_input()
    economic_interpretation.pop(missing_section)

    with pytest.raises(ValueError):
        InvestmentInterpretationService.analyze(
            economic_interpretation
        )


def test_invalid_input_type_raises_type_error():
    with pytest.raises(TypeError):
        InvestmentInterpretationService.analyze(
            None
        )


def test_invalid_input_list_raises_type_error():
    with pytest.raises(TypeError):
        InvestmentInterpretationService.analyze(
            []
        )


def test_missing_sections_are_reported():
    economic_interpretation = {}

    with pytest.raises(ValueError) as exc_info:
        InvestmentInterpretationService.analyze(
            economic_interpretation
        )

    message = str(exc_info.value)

    assert "growth" in message
    assert "trend" in message
    assert "momentum" in message
    assert "volatility" in message
    assert "position" in message
    assert "transition" in message
    assert "regime" in message


def test_transition_with_none_values_normalizes_to_canonical_strings():
    interpretation = make_input()
    interpretation["transition"] = {
        "detected": False,
        "direction": None,
        "state": None,
    }

    result = InvestmentInterpretationService.analyze(interpretation)

    # Verifica que en todos los submódulos transition.direction y transition.state sean strings
    assert result["environment"]["transition"]["direction"] == "unknown"
    assert result["environment"]["transition"]["state"] == "none"
    assert result["opportunity"]["transition"]["direction"] == "unknown"
    assert result["opportunity"]["transition"]["state"] == "none"
    assert result["risk"]["transition"]["direction"] == "unknown"
    assert result["risk"]["transition"]["state"] == "none"
    assert result["confidence"]["context"]["transition"]["direction"] == "unknown"
    assert result["confidence"]["context"]["transition"]["state"] == "none"