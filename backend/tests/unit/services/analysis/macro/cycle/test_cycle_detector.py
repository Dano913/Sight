from __future__ import annotations

from app.services.analysis.cycle.cycle_detector import (
    CycleDetector,
)


def make_period(
    period_years: float,
    power: float,
    relative_power: float = 0.25,
):
    return {
        "period_years": period_years,
        "power": power,
        "relative_power": relative_power,
    }


class TestGetValidPeriods:

    def test_filters_periods_below_two_years(self):
        periodogram = [
            make_period(1.5, 10.0),
            make_period(3.0, 5.0),
        ]

        result = CycleDetector.get_valid_periods(
            periodogram,
            sample_size=20,
            observations_per_year=1,
        )

        assert len(result) == 1
        assert result[0]["period_years"] == 3.0

    def test_filters_periods_longer_than_half_sample(self):
        periodogram = [
            make_period(8.0, 10.0),
            make_period(11.0, 20.0),
        ]

        result = CycleDetector.get_valid_periods(
            periodogram,
            sample_size=20,
            observations_per_year=1,
        )

        assert len(result) == 1
        assert result[0]["period_years"] == 8.0

    def test_returns_highest_power_periods_first(self):
        periodogram = [
            make_period(3.0, 1.0),
            make_period(4.0, 5.0),
            make_period(5.0, 3.0),
        ]

        result = CycleDetector.get_valid_periods(
            periodogram,
            sample_size=20,
            observations_per_year=1,
        )

        assert [
            item["power"]
            for item in result
        ] == [5.0, 3.0, 1.0]

    def test_handles_quarterly_sample_in_years(self):
        periodogram = [
            make_period(2.0, 10.0),
            make_period(6.0, 5.0),
            make_period(12.0, 20.0),
        ]

        result = CycleDetector.get_valid_periods(
            periodogram,
            sample_size=40,
            observations_per_year=4,
        )

        # 40 observaciones trimestrales = 10 años.
        # Máximo permitido = 5 años.
        assert [
            item["period_years"]
            for item in result
        ] == [2.0]


class TestPeriodsAreClose:

    def test_identifies_close_periods(self):
        assert CycleDetector.periods_are_close(
            10.0,
            10.33,
        )

    def test_rejects_distant_periods(self):
        assert not CycleDetector.periods_are_close(
            5.0,
            10.0,
        )

    def test_rejects_zero_mean_period(self):
        assert not CycleDetector.periods_are_close(
            0.0,
            0.0,
        )


class TestClusterPeriods:

    def test_groups_close_periods(self):
        method_results = {
            "growth": [
                make_period(
                    10.0,
                    1.0,
                    0.30,
                )
            ],
            "linear_detrend": [
                make_period(
                    10.33,
                    2.0,
                    0.40,
                )
            ],
            "hp": [
                make_period(
                    5.0,
                    1.0,
                    0.20,
                )
            ],
        }

        clusters = CycleDetector.cluster_periods(
            method_results
        )

        assert len(clusters) == 2

        assert len(clusters[0]) == 1
        assert len(clusters[1]) == 2

    def test_preserves_method_power_and_relative_power(self):
        method_results = {
            "growth": [
                make_period(
                    10.0,
                    4.0,
                    0.35,
                )
            ]
        }

        clusters = CycleDetector.cluster_periods(
            method_results
        )

        item = clusters[0][0]

        assert item["method"] == "growth"
        assert item["period"] == 10.0
        assert item["power"] == 4.0
        assert item["relative_power"] == 0.35


class TestScoreCluster:

    def test_multi_method_cluster_has_higher_method_coverage(
        self,
    ):
        single = [
            {
                "method": "growth",
                "period": 8.0,
                "power": 1.0,
                "relative_power": 0.30,
            }
        ]

        multiple = [
            {
                "method": "growth",
                "period": 8.0,
                "power": 1.0,
                "relative_power": 0.30,
            },
            {
                "method": "hp",
                "period": 8.2,
                "power": 1.0,
                "relative_power": 0.30,
            },
        ]

        single_result = CycleDetector.score_cluster(
            single,
            sample_size=40,
            observations_per_year=1,
        )

        multiple_result = CycleDetector.score_cluster(
            multiple,
            sample_size=40,
            observations_per_year=1,
        )

        assert (
            multiple_result["method_coverage"]
            > single_result["method_coverage"]
        )

    def test_representative_period_is_median(self):
        cluster = [
            {
                "method": "growth",
                "period": 7.0,
                "power": 1.0,
                "relative_power": 0.30,
            },
            {
                "method": "linear_detrend",
                "period": 8.0,
                "power": 1.0,
                "relative_power": 0.30,
            },
            {
                "method": "hp",
                "period": 9.0,
                "power": 1.0,
                "relative_power": 0.30,
            },
        ]

        result = CycleDetector.score_cluster(
            cluster,
            sample_size=40,
            observations_per_year=1,
        )

        assert result["period_years"] == 8.0

    def test_detected_cycle_contains_expected_fields(self):
        cluster = [
            {
                "method": "growth",
                "period": 8.0,
                "power": 1.0,
                "relative_power": 0.30,
            },
            {
                "method": "hp",
                "period": 8.2,
                "power": 1.0,
                "relative_power": 0.30,
            },
        ]

        result = CycleDetector.score_cluster(
            cluster,
            sample_size=40,
            observations_per_year=1,
        )

        expected_fields = {
            "period_years",
            "score",
            "confidence",
            "methods",
            "method_count",
            "method_coverage",
            "cycles_observable",
            "period_dispersion",
            "evidence",
        }

        assert expected_fields.issubset(
            result.keys()
        )

    def test_confidence_is_high_when_evidence_is_strong(self):
        cluster = [
            {
                "method": "growth",
                "period": 8.0,
                "power": 10.0,
                "relative_power": 0.50,
            },
            {
                "method": "linear_detrend",
                "period": 8.1,
                "power": 10.0,
                "relative_power": 0.50,
            },
            {
                "method": "hp",
                "period": 8.2,
                "power": 10.0,
                "relative_power": 0.50,
            },
        ]

        result = CycleDetector.score_cluster(
            cluster,
            sample_size=40,
            observations_per_year=1,
        )

        assert result["confidence"] == "ALTA"

    def test_single_method_cannot_have_high_confidence(self):
        cluster = [
            {
                "method": "growth",
                "period": 8.0,
                "power": 10.0,
                "relative_power": 0.50,
            }
        ]

        result = CycleDetector.score_cluster(
            cluster,
            sample_size=40,
            observations_per_year=1,
        )

        assert result["confidence"] != "ALTA"


class TestDetectRobustCycles:

    def test_returns_cycles_sorted_by_score(self):
        method_results = {
            "growth": [
                make_period(
                    8.0,
                    10.0,
                    0.50,
                ),
                make_period(
                    4.0,
                    1.0,
                    0.10,
                ),
            ],
            "linear_detrend": [
                make_period(
                    8.1,
                    10.0,
                    0.50,
                )
            ],
            "hp": [
                make_period(
                    8.2,
                    10.0,
                    0.50,
                )
            ],
        }

        result = CycleDetector.detect_robust_cycles(
            method_results,
            sample_size=40,
            observations_per_year=1,
        )

        assert result

        scores = [
            item["score"]
            for item in result
        ]

        assert scores == sorted(
            scores,
            reverse=True,
        )