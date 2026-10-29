from __future__ import annotations

import pytest

from app.services.interpretation.macro.cycle_interpretation_service import (
    CycleInterpretationService,
)


def make_cycle(
    *,
    score: float = 80.0,
    confidence: str = "ALTA",
    period_years: float = 6.0,
    cycles_observable: float = 4.0,
    method_count: int = 3,
) -> dict:
    return {
        "score": score,
        "confidence": confidence,
        "period_years": period_years,
        "cycles_observable": cycles_observable,
        "method_count": method_count,
    }


def make_analysis(
    *,
    cycles: list[dict] | None = None,
) -> dict:
    return {
        "robust_cycles": cycles if cycles is not None else [make_cycle()],
    }


# ============================================================================
# interpret()
# ============================================================================


def test_interpret_requires_dictionary():
    with pytest.raises(
        TypeError,
        match="cycle_analysis debe ser un diccionario",
    ):
        CycleInterpretationService.interpret(None)


def test_interpret_requires_robust_cycles_to_be_a_list():
    with pytest.raises(
        TypeError,
        match="robust_cycles debe ser una lista",
    ):
        CycleInterpretationService.interpret(
            {"robust_cycles": {}}
        )


def test_interpret_with_no_cycles_returns_no_cycle_interpretation():
    result = CycleInterpretationService.interpret(
        {"robust_cycles": []}
    )

    assert result["cycle_detected"] is False
    assert result["best_cycle"] is None
    assert result["overall"]["assessment"] == "no_sufficient_evidence"
    assert result["overall"]["robustness"] == "limited"
    assert result["overall"]["cycles_detected"] == 0
    assert "No se ha encontrado evidencia suficiente" in result["caution"]


def test_interpret_detects_cycle_when_robust_cycle_exists():
    result = CycleInterpretationService.interpret(
        make_analysis()
    )

    assert result["cycle_detected"] is True
    assert result["best_cycle"] is not None
    assert result["overall"] is not None
    assert result["caution"]


def test_interpret_uses_first_cycle_as_best_cycle():
    first = make_cycle(
        score=90.0,
        period_years=7.0,
    )
    second = make_cycle(
        score=60.0,
        period_years=4.0,
    )

    result = CycleInterpretationService.interpret(
        make_analysis(cycles=[first, second])
    )

    assert result["best_cycle"]["score"] == 90.0
    assert result["best_cycle"]["period_years"] == 7.0


# ============================================================================
# _classify_evidence_level()
# ============================================================================


@pytest.mark.parametrize(
    ("score", "confidence", "expected"),
    [
        (70.0, "ALTA", "strong"),
        (80.0, "ALTA", "strong"),
        (69.99, "ALTA", "moderate"),
        (55.0, "ALTA", "moderate"),
        (70.0, "MEDIA", "moderate"),
        (55.0, "MEDIA", "moderate"),
        (54.99, "MEDIA", "weak"),
        (90.0, "BAJA", "weak"),
        (54.0, "ALTA", "weak"),
    ],
)
def test_classify_evidence_level(
    score: float,
    confidence: str,
    expected: str,
):
    result = CycleInterpretationService._classify_evidence_level(
        score=score,
        confidence=confidence,
    )

    assert result == expected


# ============================================================================
# _classify_sample_quality()
# ============================================================================


@pytest.mark.parametrize(
    ("cycles_observable", "expected"),
    [
        (3.0, "strong"),
        (4.0, "strong"),
        (2.0, "moderate"),
        (2.99, "moderate"),
        (1.99, "limited"),
        (0.0, "limited"),
    ],
)
def test_classify_sample_quality(
    cycles_observable: float,
    expected: str,
):
    result = CycleInterpretationService._classify_sample_quality(
        cycles_observable
    )

    assert result == expected


# ============================================================================
# _classify_method_support()
# ============================================================================


@pytest.mark.parametrize(
    ("method_count", "expected"),
    [
        (3, "strong"),
        (4, "strong"),
        (2, "moderate"),
        (1, "limited"),
        (0, "limited"),
    ],
)
def test_classify_method_support(
    method_count: int,
    expected: str,
):
    result = CycleInterpretationService._classify_method_support(
        method_count
    )

    assert result == expected


# ============================================================================
# _classify_robustness()
# ============================================================================


def test_classify_robustness_is_strong_when_all_dimensions_are_strong():
    result = CycleInterpretationService._classify_robustness(
        evidence_level="strong",
        sample_quality="strong",
        method_support="strong",
    )

    assert result == "strong"


@pytest.mark.parametrize(
    ("evidence", "sample", "methods"),
    [
        ("strong", "strong", "moderate"),
        ("strong", "moderate", "strong"),
        ("moderate", "strong", "strong"),
        ("moderate", "moderate", "moderate"),
        ("strong", "moderate", "moderate"),
        ("moderate", "strong", "moderate"),
    ],
)
def test_classify_robustness_is_moderate_when_evidence_is_sufficient(
    evidence: str,
    sample: str,
    methods: str,
):
    result = CycleInterpretationService._classify_robustness(
        evidence_level=evidence,
        sample_quality=sample,
        method_support=methods,
    )

    assert result == "moderate"


@pytest.mark.parametrize(
    ("evidence", "sample", "methods"),
    [
        ("weak", "strong", "strong"),
        ("strong", "limited", "strong"),
        ("strong", "strong", "limited"),
        ("weak", "limited", "limited"),
        ("moderate", "limited", "strong"),
    ],
)
def test_classify_robustness_is_limited_when_one_dimension_is_insufficient(
    evidence: str,
    sample: str,
    methods: str,
):
    result = CycleInterpretationService._classify_robustness(
        evidence_level=evidence,
        sample_quality=sample,
        method_support=methods,
    )

    assert result == "limited"


# ============================================================================
# _describe_period()
# ============================================================================


@pytest.mark.parametrize(
    ("period", "expected"),
    [
        (2.99, "ciclo relativamente corto"),
        (3.0, "ciclo de duración corta-media"),
        (4.99, "ciclo de duración corta-media"),
        (5.0, "ciclo de duración media"),
        (7.99, "ciclo de duración media"),
        (8.0, "ciclo de duración larga"),
        (11.99, "ciclo de duración larga"),
        (12.0, "ciclo de duración muy larga"),
        (20.0, "ciclo de duración muy larga"),
    ],
)
def test_describe_period(
    period: float,
    expected: str,
):
    result = CycleInterpretationService._describe_period(period)

    assert result == expected


# ============================================================================
# _interpret_cycle()
# ============================================================================


def test_interpret_cycle_preserves_cycle_values_and_adds_semantic_fields():
    cycle = make_cycle(
        score=85.5,
        confidence="ALTA",
        period_years=6.5,
        cycles_observable=4.0,
        method_count=3,
    )

    result = CycleInterpretationService._interpret_cycle(cycle)

    assert result["period_years"] == 6.5
    assert result["score"] == 85.5
    assert result["confidence"] == "ALTA"
    assert result["evidence_level"] == "strong"
    assert result["method_count"] == 3
    assert result["method_support"] == "strong"
    assert result["cycles_observable"] == 4.0
    assert result["sample_quality"] == "strong"
    assert result["robustness"] == "strong"
    assert result["description"] == "ciclo de duración media"


def test_interpret_cycle_uses_defaults_for_missing_values():
    result = CycleInterpretationService._interpret_cycle({})

    assert result["period_years"] == 0.0
    assert result["score"] == 0.0
    assert result["confidence"] == "BAJA"
    assert result["method_count"] == 0
    assert result["cycles_observable"] == 0.0
    assert result["evidence_level"] == "weak"
    assert result["sample_quality"] == "limited"
    assert result["method_support"] == "limited"
    assert result["robustness"] == "limited"
    assert result["description"] == "ciclo relativamente corto"


# ============================================================================
# _interpret_overall()
# ============================================================================


def test_interpret_overall_summarizes_best_cycle():
    cycles = [
        make_cycle(
            score=90.0,
            confidence="ALTA",
            cycles_observable=4.0,
            method_count=3,
        ),
        make_cycle(
            score=60.0,
            confidence="MEDIA",
        ),
    ]

    result = CycleInterpretationService._interpret_overall(cycles)

    assert result["assessment"] == "strong_evidence"
    assert result["robustness"] == "strong"
    assert result["cycles_detected"] == 2
    assert result["best_score"] == 90.0
    assert result["best_confidence"] == "ALTA"
    assert result["best_evidence_level"] == "strong"
    assert result["best_sample_quality"] == "strong"
    assert result["best_method_support"] == "strong"


def test_interpret_overall_returns_moderate_evidence_when_best_cycle_is_moderate():
    cycles = [
        make_cycle(
            score=60.0,
            confidence="MEDIA",
            cycles_observable=2.0,
            method_count=2,
        )
    ]

    result = CycleInterpretationService._interpret_overall(cycles)

    assert result["assessment"] == "moderate_evidence"
    assert result["robustness"] == "moderate"


def test_interpret_overall_returns_weak_evidence_when_best_cycle_is_limited():
    cycles = [
        make_cycle(
            score=40.0,
            confidence="BAJA",
            cycles_observable=1.0,
            method_count=1,
        )
    ]

    result = CycleInterpretationService._interpret_overall(cycles)

    assert result["assessment"] == "weak_evidence"
    assert result["robustness"] == "limited"


# ============================================================================
# _overall_assessment()
# ============================================================================


@pytest.mark.parametrize(
    ("robustness", "expected"),
    [
        ("strong", "strong_evidence"),
        ("moderate", "moderate_evidence"),
        ("limited", "weak_evidence"),
        ("unknown", "weak_evidence"),
    ],
)
def test_overall_assessment(
    robustness: str,
    expected: str,
):
    assert (
        CycleInterpretationService._overall_assessment(robustness)
        == expected
    )


# ============================================================================
# _build_caution()
# ============================================================================


def test_build_caution_warns_when_fewer_than_two_cycles_are_observable():
    result = CycleInterpretationService._build_caution(
        make_cycle(
            cycles_observable=1.5,
            method_count=3,
        )
    )

    assert "menos de dos ciclos" in result
    assert "mucha cautela" in result


def test_build_caution_warns_when_fewer_than_three_cycles_are_observable():
    result = CycleInterpretationService._build_caution(
        make_cycle(
            cycles_observable=2.5,
            method_count=3,
        )
    )

    assert "menos de tres ciclos" in result
    assert "estabilidad del ciclo" in result


def test_build_caution_warns_when_fewer_than_three_methods_support_cycle():
    result = CycleInterpretationService._build_caution(
        make_cycle(
            cycles_observable=4.0,
            method_count=2,
        )
    )

    assert "tres métodos" in result
    assert "evidencia es parcial" in result


def test_build_caution_reports_consistent_evidence_when_all_conditions_are_met():
    result = CycleInterpretationService._build_caution(
        make_cycle(
            cycles_observable=4.0,
            method_count=3,
        )
    )

    assert "evidencia consistente" in result
    assert "no demuestra causalidad" in result
    assert "ni garantiza" in result


# ============================================================================
# Output contract
# ============================================================================


def test_interpret_returns_expected_top_level_structure():
    result = CycleInterpretationService.interpret(
        make_analysis()
    )

    assert set(result) == {
        "cycle_detected",
        "best_cycle",
        "overall",
        "caution",
    }


def test_interpret_cycle_returns_expected_structure():
    result = CycleInterpretationService._interpret_cycle(
        make_cycle()
    )

    assert set(result) == {
        "period_years",
        "score",
        "confidence",
        "evidence_level",
        "method_count",
        "method_support",
        "cycles_observable",
        "sample_quality",
        "robustness",
        "description",
    }


def test_interpret_does_not_change_original_cycle_data():
    cycle = make_cycle()
    original = cycle.copy()

    CycleInterpretationService._interpret_cycle(cycle)

    assert cycle == original