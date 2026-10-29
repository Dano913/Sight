from __future__ import annotations

import pytest

from app.services.analysis.macro_regime.regime_confidence import (
    RegimeConfidence,
)


class TestRegimeConfidence:
    @pytest.mark.parametrize(
        (
            "dominant_score",
            "total_score",
            "indicator_count",
            "score_margin",
            "expected",
        ),
        [
            # Invalid scores
            (10, 0, 3, 10, "low"),
            (10, -5, 3, 10, "low"),
            (0, 10, 3, 10, "low"),
            (-1, 10, 3, 10, "low"),

            # One indicator
            (4, 6, 1, 2, "medium"),
            (4, 7, 1, 2, "low"),
            (3, 6, 1, 3, "low"),
            (10, 20, 1, 10, "low"),
            (10, 16, 1, 4, "medium"),
            (4, 6, 1, 1.99, "low"),

            # indicator_count <= 1
            (4, 6, 0, 2, "medium"),
            (4, 6, -1, 2, "medium"),

            # Two indicators - high
            (8, 12, 2, 3, "high"),
            (8, 13, 2, 3, "medium"),
            (7, 10, 2, 3, "medium"),

            # Two indicators - medium
            (4, 8, 2, 1, "medium"),
            (4, 7, 2, 1, "medium"),
            (4, 9, 2, 1, "low"),
            (7, 14, 2, 1, "medium"),
            (4, 8, 2, 0.99, "low"),

            # Three or more indicators - high
            (8, 13, 3, 2, "high"),
            (8, 14, 3, 2, "medium"),
            (7, 10, 3, 3, "medium"),
            (12, 20, 4, 4, "high"),

            # Three or more indicators - medium
            (4, 9, 3, 1, "low"),
            (4, 8, 3, 1, "medium"),
            (4, 10, 3, 2, "low"),
            (7, 20, 3, 3, "low"),
            (3, 5, 3, 2, "low"),
            (4, 8, 3, 0.99, "low"),

            # More than three indicators
            (8, 13, 5, 2, "high"),
            (4, 9, 10, 1, "low"),
        ],
    )
    def test_calculate(
        self,
        dominant_score: float,
        total_score: float,
        indicator_count: int,
        score_margin: float,
        expected: str,
    ):
        result = RegimeConfidence.calculate(
            dominant_score=dominant_score,
            total_score=total_score,
            indicator_count=indicator_count,
            score_margin=score_margin,
        )

        assert result == expected

    def test_single_indicator_can_never_be_high(self):
        result = RegimeConfidence.calculate(
            dominant_score=100,
            total_score=100,
            indicator_count=1,
            score_margin=100,
        )

        assert result == "medium"

    def test_single_indicator_requires_score_margin_for_medium(self):
        result = RegimeConfidence.calculate(
            dominant_score=4,
            total_score=6,
            indicator_count=1,
            score_margin=1.99,
        )

        assert result == "low"

    def test_two_indicators_require_eight_score_for_high(self):
        result = RegimeConfidence.calculate(
            dominant_score=7.99,
            total_score=10,
            indicator_count=2,
            score_margin=3,
        )

        assert result == "medium"

    def test_two_indicators_require_three_point_margin_for_high(self):
        result = RegimeConfidence.calculate(
            dominant_score=8,
            total_score=12,
            indicator_count=2,
            score_margin=2.99,
        )

        assert result == "medium"

    def test_three_indicators_require_sixty_percent_for_high(self):
        result = RegimeConfidence.calculate(
            dominant_score=8,
            total_score=13.3333333333,
            indicator_count=3,
            score_margin=2,
        )

        assert result == "high"

    def test_three_indicators_below_sixty_percent_are_not_high(self):
        result = RegimeConfidence.calculate(
            dominant_score=8,
            total_score=13.34,
            indicator_count=3,
            score_margin=2,
        )

        assert result == "medium"

    def test_three_indicators_require_two_point_margin_for_high(self):
        result = RegimeConfidence.calculate(
            dominant_score=8,
            total_score=12,
            indicator_count=3,
            score_margin=1.99,
        )

        assert result == "medium"

    def test_medium_requires_one_point_margin(self):
        result = RegimeConfidence.calculate(
            dominant_score=4,
            total_score=8,
            indicator_count=3,
            score_margin=0.99,
        )

        assert result == "low"