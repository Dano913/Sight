from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.analysis.macro_regime.macro_regime_service import (
    MacroRegimeService,
)


class TestMacroRegimeServiceClassify:

    def test_rejects_non_dict(self):
        with pytest.raises(
            TypeError,
            match="interpretations debe ser un dict",
        ):
            MacroRegimeService.classify([])

    def test_empty_interpretations_returns_neutral_result(self):
        result = MacroRegimeService.classify({})

        assert result == {
            "regime": "neutral",
            "conditions": [],
            "confidence": "low",
            "score": 0.0,
            "scores": {},
            "score_share": 0.0,
            "score_margin": 0.0,
            "evidence": [],
            "evidence_count": 0,
            "conflicting_evidence": [],
            "conflicting_evidence_count": 0,
            "indicator_count": 0,
            "indicators_supporting": [],
            "indicators_used": [],
            "multi_indicator": False,
            "families_supporting": [],
            "family_count": 0,
        }

    def test_no_evidence_returns_neutral_and_preserves_used_indicators(
        self,
    ):
        interpretations = {
            "GDP": {},
            "INFLATION": {},
        }

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=[],
        ):
            result = MacroRegimeService.classify(interpretations)

        assert result["regime"] == "neutral"
        assert result["conditions"] == []
        assert result["confidence"] == "low"
        assert result["score"] == 0.0
        assert result["scores"] == {}
        assert result["score_share"] == 0.0
        assert result["score_margin"] == 0.0
        assert result["evidence"] == []
        assert result["evidence_count"] == 0
        assert result["conflicting_evidence"] == []
        assert result["conflicting_evidence_count"] == 0
        assert result["indicator_count"] == 0
        assert result["indicators_supporting"] == []
        assert result["indicators_used"] == [
            "GDP",
            "INFLATION",
        ]
        assert result["multi_indicator"] is False
        assert result["families_supporting"] == []
        assert result["family_count"] == 0

    def test_no_scores_returns_neutral_and_preserves_used_indicators(
        self,
    ):
        interpretations = {
            "GDP": {
                "growth": {
                    "state": "flat",
                }
            }
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 0,
            }
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ):
            with patch.object(
                MacroRegimeService,
                "_aggregate_scores",
                return_value={},
            ):
                result = MacroRegimeService.classify(
                    interpretations
                )

        assert result["regime"] == "neutral"
        assert result["conditions"] == []
        assert result["confidence"] == "low"
        assert result["score"] == 0.0
        assert result["scores"] == {}
        assert result["score_share"] == 0.0
        assert result["score_margin"] == 0.0
        assert result["indicators_used"] == ["GDP"]
        assert result["families_supporting"] == []
        assert result["family_count"] == 0


class TestMacroRegimeServiceDominantRegime:

    def test_classifies_dominant_regime(self):
        interpretations = {
            "GDP": {},
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
                "reason": "test",
            },
            {
                "regime": "contraction",
                "weight": 2,
                "indicator": "UNEMPLOYMENT",
                "family": "employment",
                "reason": "test",
            },
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ):
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["regime"] == "expansion"
        assert result["score"] == 5.0
        assert result["scores"] == {
            "expansion": 5.0,
            "contraction": 2.0,
        }
        assert result["score_share"] == pytest.approx(5 / 7)
        assert result["score_margin"] == 3.0
        assert result["conditions"] == []
        assert result["evidence"] == [evidence[0]]
        assert result["evidence_count"] == 1
        assert result["indicator_count"] == 1
        assert result["indicators_supporting"] == ["GDP"]
        assert result["multi_indicator"] is False
        assert result["families_supporting"] == ["growth"]
        assert result["family_count"] == 1

    def test_score_share_is_dominant_score_over_total_score(self):
        interpretations = {
            "GDP": {},
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
                "reason": "test",
            },
            {
                "regime": "contraction",
                "weight": 3,
                "indicator": "UNEMPLOYMENT",
                "family": "employment",
                "reason": "test",
            },
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ):
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["score_share"] == pytest.approx(5 / 8)
        assert result["score_margin"] == 2.0

    def test_returns_only_dominant_evidence(self):
        interpretations = {
            "GDP": {},
        }

        expansion_evidence = {
            "regime": "expansion",
            "weight": 5,
            "indicator": "GDP",
            "family": "growth",
            "reason": "expansion",
        }

        contraction_evidence = {
            "regime": "contraction",
            "weight": 2,
            "indicator": "UNEMPLOYMENT",
            "family": "employment",
            "reason": "contraction",
        }

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=[
                expansion_evidence,
                contraction_evidence,
            ],
        ):
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["evidence"] == [
            expansion_evidence,
        ]
        assert result["evidence_count"] == 1
        assert result["families_supporting"] == ["growth"]
        assert result["family_count"] == 1

    def test_tie_is_resolved_deterministically(self):
        interpretations = {
            "GDP": {},
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 3,
                "indicator": "GDP",
                "family": "growth",
                "reason": "test",
            },
            {
                "regime": "contraction",
                "weight": 3,
                "indicator": "UNEMPLOYMENT",
                "family": "employment",
                "reason": "test",
            },
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ):
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["regime"] == "contraction"
        assert result["score"] == 3.0
        assert result["score_margin"] == 0.0


class TestMacroRegimeServiceIndicatorsAndFamilies:

    def test_indicator_count_uses_distinct_indicators(self):
        interpretations = {
            "INFLATION": {},
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 2,
                "indicator": "INFLATION",
                "family": "inflation",
                "reason": "inflation_pressure",
            },
            {
                "regime": "expansion",
                "weight": 2,
                "indicator": "INFLATION",
                "family": "inflation",
                "reason": "inflation_volatility",
            },
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ):
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["indicator_count"] == 1
        assert result["indicators_supporting"] == [
            "INFLATION",
        ]
        assert result["multi_indicator"] is False
        assert result["families_supporting"] == [
            "inflation",
        ]
        assert result["family_count"] == 1

    def test_supporting_indicators_are_used_when_present(self):
        interpretations = {
            "INDUSTRIAL_PRODUCTION": {},
            "RETAIL_SALES": {},
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 3,
                "indicator": "ACTIVITY",
                "family": "activity",
                "supporting_indicators": [
                    "RETAIL_SALES",
                    "INDUSTRIAL_PRODUCTION",
                ],
                "reason": "test",
            }
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ):
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["indicators_supporting"] == [
            "INDUSTRIAL_PRODUCTION",
            "RETAIL_SALES",
        ]
        assert result["indicator_count"] == 2
        assert result["multi_indicator"] is True
        assert result["families_supporting"] == [
            "activity",
        ]
        assert result["family_count"] == 1

    def test_multiple_distinct_indicators_enable_multi_indicator(
        self,
    ):
        interpretations = {
            "GDP": {},
            "UNEMPLOYMENT": {},
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
                "reason": "growth",
            },
            {
                "regime": "expansion",
                "weight": 3,
                "indicator": "UNEMPLOYMENT",
                "family": "employment",
                "reason": "declining_unemployment",
            },
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ):
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["indicator_count"] == 2
        assert result["indicators_supporting"] == [
            "GDP",
            "UNEMPLOYMENT",
        ]
        assert result["multi_indicator"] is True
        assert result["families_supporting"] == [
            "employment",
            "growth",
        ]
        assert result["family_count"] == 2


class TestMacroRegimeServiceRealEndToEnd:
    """Verifica la clasificación con analizadores reales sin mockear _collect_evidence."""

    def test_real_expansion_scenario(self):
        interpretations = {
            "GDP": {
                "growth": {"state": "positive", "direction": "improving"},
                "trend": {"state": "bullish", "direction": "improving"},
                "momentum": {"state": "positive", "direction": "improving"},
            },
            "UNEMPLOYMENT": {
                "growth": {"state": "negative", "direction": "improving"},
                "trend": {"state": "bearish", "direction": "improving"},
            },
        }

        result = MacroRegimeService.classify(interpretations)

        assert result["regime"] == "expansion"
        assert result["score"] == 8.0
        assert result["scores"]["expansion"] == 8.0
        assert result["confidence"] == "high"
        assert result["indicator_count"] == 2
        assert "GDP" in result["indicators_supporting"]
        assert "UNEMPLOYMENT" in result["indicators_supporting"]

    def test_real_contraction_scenario(self):
        interpretations = {
            "GDP": {
                "growth": {"state": "negative", "direction": "deteriorating"},
                "trend": {"state": "bearish", "direction": "deteriorating"},
                "momentum": {"state": "negative", "direction": "deteriorating"},
            },
            "UNEMPLOYMENT": {
                "growth": {"state": "positive", "direction": "deteriorating"},
                "trend": {"state": "bullish", "direction": "deteriorating"},
            },
        }

        result = MacroRegimeService.classify(interpretations)

        assert result["regime"] == "contraction"
        assert result["score"] == 8.0
        assert result["scores"]["contraction"] == 8.0
        assert result["confidence"] == "high"

    def test_real_late_expansion_scenario(self):
        interpretations = {
            "GDP": {
                "growth": {"state": "positive", "direction": "stable"},
                "trend": {"state": "bullish", "direction": "stable"},
                "momentum": {"state": "positive", "direction": "stable"},
            },
            "UNEMPLOYMENT": {
                "growth": {"state": "negative", "direction": "stable"},
                "trend": {"state": "bearish", "direction": "stable"},
            },
            "INDUSTRIAL_PRODUCTION": {
                "growth": {"state": "negative"},
            },
            "RETAIL_SALES": {
                "growth": {"state": "negative"},
            },
        }

        result = MacroRegimeService.classify(interpretations)

        assert result["regime"] == "late_expansion"
        assert result["score"] == 8.0
        assert result["scores"] == {
            "expansion": 8.0,
            "contraction": 4.0,
        }
        assert result["confidence"] == "high"
        assert result["conflicting_evidence_count"] == 1


    def test_supporting_indicators_are_sorted(self):
        interpretations = {
            "GDP": {},
            "UNEMPLOYMENT": {},
            "INFLATION": {},
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 2,
                "indicator": "UNEMPLOYMENT",
                "family": "employment",
                "reason": "test",
            },
            {
                "regime": "expansion",
                "weight": 2,
                "indicator": "GDP",
                "family": "growth",
                "reason": "test",
            },
            {
                "regime": "expansion",
                "weight": 2,
                "indicator": "INFLATION",
                "family": "inflation",
                "reason": "test",
            },
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ):
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["indicators_supporting"] == [
            "GDP",
            "INFLATION",
            "UNEMPLOYMENT",
        ]

        assert result["families_supporting"] == [
            "employment",
            "growth",
            "inflation",
        ]


class TestMacroRegimeServiceConditions:

    def test_collects_inflation_stress_condition(self):
        evidence = [
            {
                "regime": "inflation_stress",
                "weight": 3,
                "indicator": "INFLATION",
                "family": "inflation",
            }
        ]

        assert MacroRegimeService._collect_conditions(
            evidence
        ) == ["inflation_stress"]

    def test_collects_financial_stress_condition(self):
        evidence = [
            {
                "regime": "financial_stress",
                "weight": 3,
                "indicator": "FINANCIAL_CONDITIONS",
                "family": "financial",
            }
        ]

        assert MacroRegimeService._collect_conditions(
            evidence
        ) == ["financial_stress"]

    def test_collects_multiple_conditions_without_duplicates(self):
        evidence = [
            {
                "regime": "inflation_stress",
                "weight": 2,
                "indicator": "INFLATION",
                "family": "inflation",
            },
            {
                "regime": "inflation_stress",
                "weight": 3,
                "indicator": "INFLATION",
                "family": "inflation",
            },
            {
                "regime": "financial_stress",
                "weight": 3,
                "indicator": "FINANCIAL_CONDITIONS",
                "family": "financial",
            },
        ]

        assert MacroRegimeService._collect_conditions(
            evidence
        ) == [
            "financial_stress",
            "inflation_stress",
        ]

    def test_conditions_do_not_enter_cyclical_scores(self):
        evidence = [
            {
                "regime": "inflation_stress",
                "weight": 5,
                "indicator": "INFLATION",
                "family": "inflation",
            },
            {
                "regime": "financial_stress",
                "weight": 5,
                "indicator": "FINANCIAL_CONDITIONS",
                "family": "financial",
            },
            {
                "regime": "expansion",
                "weight": 3,
                "indicator": "GDP",
                "family": "growth",
            },
        ]

        result = MacroRegimeService._aggregate_scores(
            evidence
        )

        assert result == {
            "expansion": 3.0,
        }


class TestMacroRegimeServiceActivityAdjustment:

    def test_adjusts_expansion_to_late_expansion_when_activity_weakens(
        self,
    ):
        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
            },
            {
                "regime": "contraction",
                "weight": 4,
                "indicator": "ACTIVITY",
                "family": "activity",
                "supporting_indicators": [
                    "INDUSTRIAL_PRODUCTION",
                    "RETAIL_SALES",
                ],
            },
        ]

        result = MacroRegimeService._adjust_for_conflicting_activity(
            dominant_regime="expansion",
            scores={
                "expansion": 5.0,
                "contraction": 4.0,
            },
            evidence=evidence,
        )

        assert result == "late_expansion"

    def test_does_not_adjust_when_dominant_regime_is_not_expansion(
        self,
    ):
        evidence = [
            {
                "regime": "contraction",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
            },
            {
                "regime": "contraction",
                "weight": 4,
                "indicator": "ACTIVITY",
                "family": "activity",
            },
        ]

        result = MacroRegimeService._adjust_for_conflicting_activity(
            dominant_regime="contraction",
            scores={
                "contraction": 9.0,
            },
            evidence=evidence,
        )

        assert result == "contraction"

    def test_does_not_adjust_without_activity_contraction(self):
        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
            },
            {
                "regime": "contraction",
                "weight": 3,
                "indicator": "UNEMPLOYMENT",
                "family": "employment",
            },
        ]

        result = MacroRegimeService._adjust_for_conflicting_activity(
            dominant_regime="expansion",
            scores={
                "expansion": 5.0,
                "contraction": 3.0,
            },
            evidence=evidence,
        )

        assert result == "expansion"

    def test_does_not_adjust_when_activity_contraction_score_is_below_threshold(
        self,
    ):
        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
            },
            {
                "regime": "contraction",
                "weight": 3,
                "indicator": "ACTIVITY",
                "family": "activity",
            },
        ]

        result = MacroRegimeService._adjust_for_conflicting_activity(
            dominant_regime="expansion",
            scores={
                "expansion": 5.0,
                "contraction": 3.0,
            },
            evidence=evidence,
        )

        assert result == "expansion"

    def test_does_not_adjust_when_contraction_is_equal_to_expansion(
        self,
    ):
        evidence = [
            {
                "regime": "expansion",
                "weight": 4,
                "indicator": "GDP",
                "family": "growth",
            },
            {
                "regime": "contraction",
                "weight": 4,
                "indicator": "ACTIVITY",
                "family": "activity",
            },
        ]

        result = MacroRegimeService._adjust_for_conflicting_activity(
            dominant_regime="expansion",
            scores={
                "expansion": 4.0,
                "contraction": 4.0,
            },
            evidence=evidence,
        )

        assert result == "expansion"

    def test_does_not_adjust_when_contraction_exceeds_expansion(
        self,
    ):
        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
            },
            {
                "regime": "contraction",
                "weight": 6,
                "indicator": "ACTIVITY",
                "family": "activity",
            },
        ]

        result = MacroRegimeService._adjust_for_conflicting_activity(
            dominant_regime="expansion",
            scores={
                "expansion": 5.0,
                "contraction": 6.0,
            },
            evidence=evidence,
        )

        assert result == "expansion"


class TestMacroRegimeServiceConflictingEvidence:

    def test_get_conflicting_evidence_returns_activity_contraction(
        self,
    ):
        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
            },
            {
                "regime": "contraction",
                "weight": 4,
                "indicator": "ACTIVITY",
                "family": "activity",
            },
        ]

        result = MacroRegimeService._get_conflicting_evidence(
            dominant_regime="late_expansion",
            raw_dominant_regime="expansion",
            evidence=evidence,
        )

        assert result == [
            {
                "regime": "contraction",
                "weight": 4,
                "indicator": "ACTIVITY",
                "family": "activity",
            }
        ]

    def test_get_conflicting_evidence_returns_empty_for_normal_expansion(
        self,
    ):
        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
            },
            {
                "regime": "contraction",
                "weight": 4,
                "indicator": "ACTIVITY",
                "family": "activity",
            },
        ]

        result = MacroRegimeService._get_conflicting_evidence(
            dominant_regime="expansion",
            raw_dominant_regime="expansion",
            evidence=evidence,
        )

        assert result == []

    def test_get_conflicting_evidence_returns_empty_for_non_expansion_transition(
        self,
    ):
        evidence = [
            {
                "regime": "contraction",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
            }
        ]

        result = MacroRegimeService._get_conflicting_evidence(
            dominant_regime="contraction",
            raw_dominant_regime="contraction",
            evidence=evidence,
        )

        assert result == []


class TestMacroRegimeServiceCollectEvidence:

    def test_collect_evidence_delegates_to_all_analyzers(self):
        interpretations = {
            "GDP": {
                "gdp": "value",
            },
            "UNEMPLOYMENT": {
                "unemployment": "value",
            },
            "INFLATION": {
                "inflation": "value",
            },
        }

        evidence = []

        with patch(
            "app.services.analysis.macro_regime.macro_regime_service.GrowthRegimeAnalyzer.analyze"
        ) as growth, patch(
            "app.services.analysis.macro_regime.macro_regime_service.ActivityRegimeAnalyzer.analyze"
        ) as activity, patch(
            "app.services.analysis.macro_regime.macro_regime_service.EmploymentRegimeAnalyzer.analyze"
        ) as employment, patch(
            "app.services.analysis.macro_regime.macro_regime_service.InflationRegimeAnalyzer.analyze"
        ) as inflation, patch(
            "app.services.analysis.macro_regime.macro_regime_service.FinancialRegimeAnalyzer.analyze"
        ) as financial:
            result = MacroRegimeService._collect_evidence(
                interpretations
            )

        assert result == evidence

        growth.assert_called_once_with(
            interpretations["GDP"],
            evidence,
        )

        activity.assert_called_once_with(
            interpretations,
            evidence,
        )

        employment.assert_called_once_with(
            interpretations["UNEMPLOYMENT"],
            evidence,
        )

        inflation.assert_called_once_with(
            interpretations["INFLATION"],
            evidence,
        )

        financial.assert_called_once_with(
            interpretations,
            evidence,
        )

    def test_collect_evidence_passes_none_for_missing_indicators(
        self,
    ):
        interpretations = {}

        with patch(
            "app.services.analysis.macro_regime.macro_regime_service.GrowthRegimeAnalyzer.analyze"
        ) as growth, patch(
            "app.services.analysis.macro_regime.macro_regime_service.ActivityRegimeAnalyzer.analyze"
        ), patch(
            "app.services.analysis.macro_regime.macro_regime_service.EmploymentRegimeAnalyzer.analyze"
        ) as employment, patch(
            "app.services.analysis.macro_regime.macro_regime_service.InflationRegimeAnalyzer.analyze"
        ) as inflation, patch(
            "app.services.analysis.macro_regime.macro_regime_service.FinancialRegimeAnalyzer.analyze"
        ):
            evidence = MacroRegimeService._collect_evidence(
                interpretations
            )

        growth.assert_called_once_with(
            None,
            evidence,
        )

        employment.assert_called_once_with(
            None,
            evidence,
        )

        inflation.assert_called_once_with(
            None,
            evidence,
        )


class TestMacroRegimeServiceAggregateScores:

    def test_empty_evidence_returns_empty_scores(self):
        assert MacroRegimeService._aggregate_scores([]) == {}

    def test_aggregates_weights_by_regime(self):
        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
            },
            {
                "regime": "expansion",
                "weight": 2,
            },
            {
                "regime": "contraction",
                "weight": 3,
            },
        ]

        result = MacroRegimeService._aggregate_scores(
            evidence
        )

        assert result == {
            "expansion": 7.0,
            "contraction": 3.0,
        }

    def test_converts_integer_weights_to_float(self):
        result = MacroRegimeService._aggregate_scores(
            [
                {
                    "regime": "expansion",
                    "weight": 5,
                }
            ]
        )

        assert result == {
            "expansion": 5.0,
        }

    def test_supports_float_weights(self):
        result = MacroRegimeService._aggregate_scores(
            [
                {
                    "regime": "expansion",
                    "weight": 2.5,
                }
            ]
        )

        assert result == {
            "expansion": 2.5,
        }

    def test_ignores_invalid_regimes(self):
        result = MacroRegimeService._aggregate_scores(
            [
                {
                    "regime": "invalid",
                    "weight": 10,
                },
                {
                    "regime": "expansion",
                    "weight": 5,
                },
            ]
        )

        assert result == {
            "expansion": 5.0,
        }

    def test_ignores_condition_regimes(self):
        result = MacroRegimeService._aggregate_scores(
            [
                {
                    "regime": "inflation_stress",
                    "weight": 5,
                },
                {
                    "regime": "financial_stress",
                    "weight": 5,
                },
                {
                    "regime": "expansion",
                    "weight": 3,
                },
            ]
        )

        assert result == {
            "expansion": 3.0,
        }

    def test_ignores_non_positive_weights(self):
        result = MacroRegimeService._aggregate_scores(
            [
                {
                    "regime": "expansion",
                    "weight": 0,
                },
                {
                    "regime": "contraction",
                    "weight": -2,
                },
                {
                    "regime": "financial_stress",
                    "weight": 3,
                },
            ]
        )

        assert result == {}

    def test_ignores_invalid_weights(self):
        result = MacroRegimeService._aggregate_scores(
            [
                {
                    "regime": "expansion",
                    "weight": "invalid",
                },
                {
                    "regime": "contraction",
                },
                {
                    "regime": "financial_stress",
                    "weight": 2,
                },
            ]
        )

        assert result == {}


class TestMacroRegimeServiceEmptyResult:

    def test_default_empty_result(self):
        result = MacroRegimeService._empty_result()

        assert result == {
            "regime": "neutral",
            "conditions": [],
            "confidence": "low",
            "score": 0.0,
            "scores": {},
            "score_share": 0.0,
            "score_margin": 0.0,
            "evidence": [],
            "evidence_count": 0,
            "conflicting_evidence": [],
            "conflicting_evidence_count": 0,
            "indicator_count": 0,
            "indicators_supporting": [],
            "indicators_used": [],
            "multi_indicator": False,
            "families_supporting": [],
            "family_count": 0,
        }

    def test_empty_result_preserves_indicators_used(self):
        result = MacroRegimeService._empty_result(
            indicators_used=[
                "GDP",
                "INFLATION",
            ]
        )

        assert result["indicators_used"] == [
            "GDP",
            "INFLATION",
        ]

        assert result["regime"] == "neutral"
        assert result["confidence"] == "low"
        assert result["score_margin"] == 0.0
        assert result["conditions"] == []
        assert result["families_supporting"] == []
        assert result["family_count"] == 0

    def test_empty_result_preserves_conditions(self):
        result = MacroRegimeService._empty_result(
            indicators_used=["INFLATION"],
            conditions=["inflation_stress"],
        )

        assert result["regime"] == "neutral"
        assert result["conditions"] == [
            "inflation_stress",
        ]
        assert result["indicators_used"] == [
            "INFLATION",
        ]


class TestMacroRegimeServiceConfidence:

    def test_confidence_receives_score_margin(self):
        interpretations = {
            "GDP": {},
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
                "reason": "test",
            },
            {
                "regime": "contraction",
                "weight": 2,
                "indicator": "UNEMPLOYMENT",
                "family": "employment",
                "reason": "test",
            },
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ), patch(
            "app.services.analysis.macro_regime.macro_regime_service.RegimeConfidence.calculate",
            return_value="medium",
        ) as mock_confidence:
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["confidence"] == "medium"

        mock_confidence.assert_called_once_with(
            dominant_score=5.0,
            total_score=7.0,
            indicator_count=1,
            score_margin=3.0,
        )


class TestMacroRegimeServiceLateExpansion:

    def test_classify_returns_late_expansion_when_activity_conflicts(
        self,
    ):
        interpretations = {
            "GDP": {},
            "UNEMPLOYMENT": {},
            "INDUSTRIAL_PRODUCTION": {},
            "RETAIL_SALES": {},
        }

        evidence = [
            {
                "regime": "expansion",
                "weight": 5,
                "indicator": "GDP",
                "family": "growth",
                "reason": "growth",
            },
            {
                "regime": "expansion",
                "weight": 3,
                "indicator": "UNEMPLOYMENT",
                "family": "employment",
                "reason": "declining_unemployment",
            },
            {
                "regime": "contraction",
                "weight": 4,
                "indicator": "ACTIVITY",
                "family": "activity",
                "reason": "activity_weakness",
                "supporting_indicators": [
                    "INDUSTRIAL_PRODUCTION",
                    "RETAIL_SALES",
                ],
            },
        ]

        with patch.object(
            MacroRegimeService,
            "_collect_evidence",
            return_value=evidence,
        ):
            result = MacroRegimeService.classify(
                interpretations
            )

        assert result["regime"] == "late_expansion"
        assert result["score"] == 8.0
        assert result["scores"] == {
            "expansion": 8.0,
            "contraction": 4.0,
        }
        assert result["score_margin"] == 4.0
        assert result["evidence"] == [
            evidence[0],
            evidence[1],
        ]
        assert result["evidence_count"] == 2
        assert result["conflicting_evidence"] == [
            evidence[2],
        ]
        assert result["conflicting_evidence_count"] == 1
        assert result["indicator_count"] == 2
        assert result["indicators_supporting"] == [
            "GDP",
            "UNEMPLOYMENT",
        ]
        assert result["multi_indicator"] is True
        assert result["families_supporting"] == [
            "employment",
            "growth",
        ]
        assert result["family_count"] == 2


class TestMacroRegimeServiceRealEndToEnd:
    """Verifica la clasificación con analizadores reales sin mockear _collect_evidence."""

    def test_real_expansion_scenario(self):
        interpretations = {
            "GDP": {
                "growth": {"state": "positive", "direction": "improving"},
                "trend": {"state": "bullish", "direction": "improving"},
                "momentum": {"state": "positive", "direction": "improving"},
            },
            "UNEMPLOYMENT": {
                "growth": {"state": "negative", "direction": "improving"},
                "trend": {"state": "bearish", "direction": "improving"},
            },
        }

        result = MacroRegimeService.classify(interpretations)

        assert result["regime"] == "expansion"
        assert result["score"] == 8.0
        assert result["scores"]["expansion"] == 8.0
        assert result["confidence"] == "high"
        assert result["indicator_count"] == 2
        assert "GDP" in result["indicators_supporting"]
        assert "UNEMPLOYMENT" in result["indicators_supporting"]

    def test_real_contraction_scenario(self):
        interpretations = {
            "GDP": {
                "growth": {"state": "negative", "direction": "deteriorating"},
                "trend": {"state": "bearish", "direction": "deteriorating"},
                "momentum": {"state": "negative", "direction": "deteriorating"},
            },
            "UNEMPLOYMENT": {
                "growth": {"state": "positive", "direction": "deteriorating"},
                "trend": {"state": "bullish", "direction": "deteriorating"},
            },
        }

        result = MacroRegimeService.classify(interpretations)

        assert result["regime"] == "contraction"
        assert result["score"] == 8.0
        assert result["scores"]["contraction"] == 8.0
        assert result["confidence"] == "high"

    def test_real_late_expansion_scenario(self):
        interpretations = {
            "GDP": {
                "growth": {"state": "positive", "direction": "stable"},
                "trend": {"state": "bullish", "direction": "stable"},
                "momentum": {"state": "positive", "direction": "stable"},
            },
            "UNEMPLOYMENT": {
                "growth": {"state": "negative", "direction": "stable"},
                "trend": {"state": "bearish", "direction": "stable"},
            },
            "INDUSTRIAL_PRODUCTION": {
                "growth": {"state": "negative"},
            },
            "RETAIL_SALES": {
                "growth": {"state": "negative"},
            },
        }

        result = MacroRegimeService.classify(interpretations)

        assert result["regime"] == "late_expansion"
        assert result["score"] == 8.0
        assert result["scores"] == {
            "expansion": 8.0,
            "contraction": 4.0,
        }
        assert result["confidence"] == "high"
        assert result["conflicting_evidence_count"] == 1
