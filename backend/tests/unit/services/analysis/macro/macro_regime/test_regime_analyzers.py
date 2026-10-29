from __future__ import annotations

import pytest

from app.services.analysis.macro_regime.regime_analyzers import (
    ActivityRegimeAnalyzer,
    EmploymentRegimeAnalyzer,
    FinancialRegimeAnalyzer,
    GrowthRegimeAnalyzer,
    InflationRegimeAnalyzer,
)


class TestGrowthRegimeAnalyzer:
    def test_empty_interpretation_does_nothing(self):
        evidence = []
        GrowthRegimeAnalyzer.analyze(None, evidence)
        assert evidence == []

    def test_expansion(self):
        evidence = []
        GrowthRegimeAnalyzer.analyze(
            {
                "growth": {"state": "positive"},
                "trend": {"state": "bullish"},
                "momentum": {
                    "state": "positive",
                    "direction": "stable",
                },
            },
            evidence,
        )
        assert evidence[0]["regime"] == "expansion"
        assert evidence[0]["indicator"] == "GDP"
        assert evidence[0]["family"] == "growth"

    def test_late_expansion_from_deteriorating_trend(self):
        evidence = []
        GrowthRegimeAnalyzer.analyze(
            {
                "growth": {"state": "positive"},
                "trend": {
                    "state": "bullish",
                    "direction": "deteriorating",
                },
                "momentum": {"state": "positive"},
            },
            evidence,
        )
        assert evidence[0]["regime"] == "late_expansion"

    def test_late_expansion_from_deteriorating_momentum(self):
        evidence = []
        GrowthRegimeAnalyzer.analyze(
            {
                "growth": {"state": "positive"},
                "trend": {"state": "bullish"},
                "momentum": {
                    "state": "positive",
                    "direction": "deteriorating",
                },
            },
            evidence,
        )
        assert evidence[0]["regime"] == "late_expansion"

    def test_contraction(self):
        evidence = []
        GrowthRegimeAnalyzer.analyze(
            {
                "growth": {"state": "negative"},
                "trend": {"state": "bearish"},
            },
            evidence,
        )
        assert evidence[0]["regime"] == "contraction"

    def test_recovery_from_improving_trend(self):
        evidence = []
        GrowthRegimeAnalyzer.analyze(
            {
                "growth": {"state": "negative"},
                "trend": {
                    "state": "bearish",
                    "direction": "improving",
                },
            },
            evidence,
        )
        assert evidence[0]["regime"] == "recovery"

    def test_stagnation(self):
        evidence = []
        GrowthRegimeAnalyzer.analyze(
            {"growth": {"state": "flat"}},
            evidence,
        )
        assert evidence[0]["regime"] == "stagnation"

    @pytest.mark.parametrize(
        "interpretation",
        [
            {},
            {"growth": {"state": "positive"}},
            {
                "growth": {"state": "positive"},
                "trend": {"state": "bullish"},
            },
            {
                "growth": {"state": "negative"},
                "trend": {"state": "bullish"},
            },
        ],
    )
    def test_unmatched_state_produces_no_evidence(self, interpretation):
        evidence = []
        GrowthRegimeAnalyzer.analyze(interpretation, evidence)
        assert evidence == []


class TestActivityRegimeAnalyzer:
    def test_no_interpretations_does_nothing(self):
        evidence = []
        ActivityRegimeAnalyzer.analyze({}, evidence)
        assert evidence == []

    def test_two_positive_growth_indicators_produce_expansion(self):
        evidence = []
        interpretations = {
            "INDUSTRIAL_PRODUCTION": {
                "growth": {"state": "positive"},
            },
            "RETAIL_SALES": {
                "growth": {"state": "positive"},
            },
        }
        ActivityRegimeAnalyzer.analyze(interpretations, evidence)
        assert len(evidence) == 1
        assert evidence[0]["regime"] == "expansion"
        assert evidence[0]["family"] == "activity"

    def test_two_negative_growth_indicators_produce_contraction(self):
        evidence = []
        interpretations = {
            "INDUSTRIAL_PRODUCTION": {
                "growth": {"state": "negative"},
            },
            "RETAIL_SALES": {
                "growth": {"state": "negative"},
            },
        }
        ActivityRegimeAnalyzer.analyze(interpretations, evidence)
        assert len(evidence) == 1
        assert evidence[0]["regime"] == "contraction"

    def test_growth_direction_is_not_used_as_series_direction(self):
        evidence = []
        interpretations = {
            "INDUSTRIAL_PRODUCTION": {
                "growth": {"direction": "improving"},
            },
            "RETAIL_SALES": {
                "growth": {"direction": "deteriorating"},
            },
        }
        ActivityRegimeAnalyzer.analyze(interpretations, evidence)
        assert evidence == []

    def test_one_indicator_is_not_enough(self):
        evidence = []
        ActivityRegimeAnalyzer.analyze(
            {
                "INDUSTRIAL_PRODUCTION": {
                    "growth": {"state": "positive"},
                },
            },
            evidence,
        )
        assert evidence == []

    def test_unknown_indicator_is_ignored(self):
        evidence = []
        ActivityRegimeAnalyzer.analyze(
            {
                "UNKNOWN": {
                    "growth": {"state": "positive"},
                },
                "INDUSTRIAL_PRODUCTION": None,
            },
            evidence,
        )
        assert evidence == []


class TestEmploymentRegimeAnalyzer:
    def test_empty_interpretation_does_nothing(self):
        evidence = []
        EmploymentRegimeAnalyzer.analyze(None, evidence)
        assert evidence == []

    def test_falling_unemployment_produces_expansion(self):
        evidence = []
        EmploymentRegimeAnalyzer.analyze(
            {
                "growth": {"state": "negative"},
                "trend": {"direction": "down"},
            },
            evidence,
        )
        assert evidence[0]["regime"] == "expansion"
        assert evidence[0]["indicator"] == "UNEMPLOYMENT"

    def test_rising_unemployment_produces_contraction(self):
        evidence = []
        EmploymentRegimeAnalyzer.analyze(
            {
                "growth": {"state": "positive"},
                "trend": {"direction": "up"},
            },
            evidence,
        )
        assert evidence[0]["regime"] == "contraction"

    def test_interpreter_direction_without_series_direction_is_ignored(self):
        evidence = []
        EmploymentRegimeAnalyzer.analyze(
            {
                "growth": {"state": "flat"},
                "trend": {"direction": "improving"},
            },
            evidence,
        )
        assert evidence == []

    def test_trend_state_alone_does_not_trigger_evidence(self):
        evidence = []
        EmploymentRegimeAnalyzer.analyze(
            {"trend": {"state": "bearish"}},
            evidence,
        )
        assert evidence == []


class TestInflationRegimeAnalyzer:
    def test_empty_interpretation_does_nothing(self):
        evidence = []
        InflationRegimeAnalyzer.analyze(None, evidence)
        assert evidence == []

    def test_increasing_inflation_pressure(self):
        evidence = []
        InflationRegimeAnalyzer.analyze(
            {
                "growth": {"state": "positive"},
                "trend": {"state": "bullish"},
            },
            evidence,
        )
        assert evidence[0]["regime"] == "inflation_stress"
        assert evidence[0]["family"] == "inflation"

    @pytest.mark.parametrize(
        "volatility",
        [
            {"stress": "elevated", "shock": False},
            {"stress": "extreme", "shock": False},
            {"stress": "normal", "shock": True},
        ],
    )
    def test_increasing_inflation_volatility(self, volatility):
        evidence = []
        InflationRegimeAnalyzer.analyze(
            {"volatility": volatility},
            evidence,
        )
        assert evidence[0]["regime"] == "inflation_stress"

    def test_non_stress_states_produce_no_evidence(self):
        evidence = []
        InflationRegimeAnalyzer.analyze(
            {
                "growth": {"state": "flat"},
                "trend": {"state": "bearish"},
                "volatility": {
                    "stress": "normal",
                    "shock": False,
                },
            },
            evidence,
        )
        assert evidence == []


class TestFinancialRegimeAnalyzer:
    def test_no_interpretations_does_nothing(self):
        evidence = []
        FinancialRegimeAnalyzer.analyze({}, evidence)
        assert evidence == []

    @pytest.mark.parametrize(
        "volatility",
        [
            {"stress": "elevated", "shock": False},
            {"stress": "extreme", "shock": False},
            {"stress": "normal", "shock": True},
        ],
    )
    def test_financial_volatility_stress(self, volatility):
        evidence = []
        FinancialRegimeAnalyzer.analyze(
            {
                "INTEREST_RATE": {
                    "volatility": volatility,
                },
            },
            evidence,
        )
        assert evidence[0]["regime"] == "financial_stress"
        assert evidence[0]["indicator"] == "INTEREST_RATE"

    def test_severe_drawdown(self):
        evidence = []
        FinancialRegimeAnalyzer.analyze(
            {
                "FINANCIAL_CONDITIONS": {
                    "position": {
                        "drawdown_state": "severe_drawdown",
                        "severe_drawdown": True,
                    },
                },
            },
            evidence,
        )
        assert evidence[0]["regime"] == "financial_stress"

    def test_volatility_and_drawdown_produce_single_evidence(self):
        evidence = []
        FinancialRegimeAnalyzer.analyze(
            {
                "FINANCIAL_CONDITIONS": {
                    "volatility": {
                        "stress": "extreme",
                        "shock": True,
                    },
                    "position": {
                        "drawdown_state": "severe_drawdown",
                        "severe_drawdown": True,
                    },
                },
            },
            evidence,
        )
        assert len(evidence) == 1
        assert evidence[0]["regime"] == "financial_stress"

    def test_multiple_financial_indicators_are_analyzed(self):
        evidence = []
        FinancialRegimeAnalyzer.analyze(
            {
                "INTEREST_RATE": {
                    "volatility": {
                        "stress": "extreme",
                        "shock": True,
                    },
                },
                "FINANCIAL_CONDITIONS": {
                    "position": {
                        "drawdown_state": "severe_drawdown",
                        "severe_drawdown": True,
                    },
                },
            },
            evidence,
        )
        assert len(evidence) == 2
        assert {
            item["indicator"] for item in evidence
        } == {"INTEREST_RATE", "FINANCIAL_CONDITIONS"}

    def test_non_stress_states_produce_no_evidence(self):
        evidence = []
        FinancialRegimeAnalyzer.analyze(
            {
                "INTEREST_RATE": {
                    "volatility": {
                        "stress": "normal",
                        "shock": False,
                    },
                    "position": {
                        "drawdown_state": "normal",
                        "severe_drawdown": False,
                    },
                },
                "FINANCIAL_CONDITIONS": {
                    "volatility": {
                        "stress": "normal",
                        "shock": False,
                    },
                    "position": {
                        "drawdown_state": "normal",
                        "severe_drawdown": False,
                    },
                },
            },
            evidence,
        )
        assert evidence == []