from __future__ import annotations

from typing import Any

from .regime_analyzers import (
    ActivityRegimeAnalyzer,
    EmploymentRegimeAnalyzer,
    FinancialRegimeAnalyzer,
    GrowthRegimeAnalyzer,
    InflationRegimeAnalyzer,
)
from .regime_confidence import RegimeConfidence


class MacroRegimeService:
    """
    Clasifica el régimen macroeconómico agregado.

    Consume las interpretaciones producidas por
    EconomicInterpretationService y combina la evidencia
    procedente de múltiples indicadores.

    No calcula features ni interpreta indicadores individuales.
    """

    CYCLICAL_REGIMES = frozenset({
        "expansion",
        "late_expansion",
        "slowdown",
        "stagnation",
        "recovery",
        "contraction",
        "neutral",
    })

    CONDITION_REGIMES = frozenset({
        "inflation_stress",
        "financial_stress",
    })

    # ==============================================================
    # PUBLIC API
    # ==============================================================

    @classmethod
    def classify(
        cls,
        interpretations: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:

        if not isinstance(interpretations, dict):
            raise TypeError("interpretations debe ser un dict")

        if not interpretations:
            return cls._empty_result()

        evidence = cls._collect_evidence(interpretations)

        if not evidence:
            return cls._empty_result(
                indicators_used=list(interpretations)
            )

        conditions = cls._collect_conditions(evidence)

        scores = cls._aggregate_scores(evidence)

        if not scores:
            return cls._empty_result(
                indicators_used=list(interpretations),
                conditions=conditions,
            )

        ordered_scores = sorted(
            scores.items(),
            key=lambda item: (-item[1], item[0]),
        )

        raw_dominant_regime, raw_dominant_score = ordered_scores[0]

        total_score = sum(scores.values())

        second_score = (
            ordered_scores[1][1]
            if len(ordered_scores) > 1
            else 0.0
        )

        score_margin = raw_dominant_score - second_score

        # ----------------------------------------------------------
        # Detectar desaceleración dentro de una expansión.
        #
        # Si el crecimiento y el empleo siguen apoyando expansión,
        # pero varios indicadores de actividad muestran debilidad,
        # el escenario se clasifica como late_expansion.
        # ----------------------------------------------------------

        dominant_regime = cls._adjust_for_conflicting_activity(
            dominant_regime=raw_dominant_regime,
            scores=scores,
            evidence=evidence,
        )

        # El score representa la fuerza de la señal macro que
        # originó el régimen dominante.
        dominant_score = raw_dominant_score

        # Evidencia que respalda el régimen macro base.
        dominant_evidence = [
            item
            for item in evidence
            if item.get("regime") == raw_dominant_regime
        ]

        # Evidencia que explica el conflicto que produjo
        # el régimen derivado, por ejemplo late_expansion.
        conflicting_evidence = cls._get_conflicting_evidence(
            dominant_regime=dominant_regime,
            raw_dominant_regime=raw_dominant_regime,
            evidence=evidence,
        )

        dominant_indicators = cls._get_supporting_indicators(
            dominant_evidence
        )

        indicator_count = len(dominant_indicators)

        dominant_families = cls._get_supporting_families(
            dominant_evidence
        )

        family_count = len(dominant_families)

        confidence = RegimeConfidence.calculate(
            dominant_score=dominant_score,
            total_score=total_score,
            indicator_count=indicator_count,
            score_margin=score_margin,
        )

        score_share = (
            dominant_score / total_score
            if total_score > 0
            else 0.0
        )

        return {
            "regime": dominant_regime,
            "conditions": conditions,
            "confidence": confidence,
            "score": dominant_score,
            "scores": scores,
            "score_share": score_share,
            "score_margin": score_margin,
            "evidence": dominant_evidence,
            "evidence_count": len(dominant_evidence),
            "conflicting_evidence": conflicting_evidence,
            "conflicting_evidence_count": len(conflicting_evidence),
            "indicator_count": indicator_count,
            "indicators_supporting": dominant_indicators,
            "indicators_used": list(interpretations),
            "multi_indicator": indicator_count > 1,
            "families_supporting": dominant_families,
            "family_count": family_count,
        }

    # ==============================================================
    # REGIME ADJUSTMENT
    # ==============================================================

    @staticmethod
    def _adjust_for_conflicting_activity(
        *,
        dominant_regime: str,
        scores: dict[str, float],
        evidence: list[dict[str, Any]],
    ) -> str:
        """
        Ajusta el régimen cuando existe una contradicción relevante
        entre crecimiento agregado y actividad económica.

        Una expansión respaldada por GDP/empleo, pero acompañada por
        debilidad confirmada en varios indicadores de actividad,
        se clasifica como late_expansion.

        La regla no se aplica a cualquier señal aislada:
        requiere evidencia agregada de ACTIVITY con peso suficiente.
        """

        if dominant_regime != "expansion":
            return dominant_regime

        activity_contraction = any(
            item.get("regime") == "contraction"
            and (
                item.get("indicator") == "ACTIVITY"
                or item.get("family") == "activity"
            )
            for item in evidence
        )

        if not activity_contraction:
            return dominant_regime

        contraction_score = scores.get(
            "contraction",
            0.0,
        )

        if contraction_score < 4.0:
            return dominant_regime

        expansion_score = scores.get(
            "expansion",
            0.0,
        )

        if expansion_score <= contraction_score:
            return dominant_regime

        return "late_expansion"

    # ==============================================================
    # CONFLICTING EVIDENCE
    # ==============================================================

    @staticmethod
    def _get_conflicting_evidence(
        *,
        dominant_regime: str,
        raw_dominant_regime: str,
        evidence: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Devuelve la evidencia que contradice el régimen dominante
        cuando este ha sido transformado en un régimen derivado.

        Actualmente se utiliza para explicar late_expansion:
        expansión respaldada por crecimiento/empleo + debilidad
        agregada de actividad.
        """

        if (
            dominant_regime != "late_expansion"
            or raw_dominant_regime != "expansion"
        ):
            return []

        return [
            item
            for item in evidence
            if (
                item.get("regime") == "contraction"
                and (
                    item.get("indicator") == "ACTIVITY"
                    or item.get("family") == "activity"
                )
            )
        ]

    # ==============================================================
    # EVIDENCE COLLECTION
    # ==============================================================

    @staticmethod
    def _collect_evidence(
        interpretations: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        evidence: list[dict[str, Any]] = []

        GrowthRegimeAnalyzer.analyze(
            interpretations.get("GDP"),
            evidence,
        )

        ActivityRegimeAnalyzer.analyze(
            interpretations,
            evidence,
        )

        EmploymentRegimeAnalyzer.analyze(
            interpretations.get("UNEMPLOYMENT"),
            evidence,
        )

        InflationRegimeAnalyzer.analyze(
            interpretations.get("INFLATION"),
            evidence,
        )

        FinancialRegimeAnalyzer.analyze(
            interpretations,
            evidence,
        )

        return evidence

    @classmethod
    def _collect_conditions(
        cls,
        evidence: list[dict[str, Any]],
    ) -> list[str]:
        conditions: set[str] = set()

        for item in evidence:
            regime = item.get("regime")
            if regime in cls.CONDITION_REGIMES:
                conditions.add(regime)

        return sorted(conditions)

    # ==============================================================
    # SUPPORTING INDICATORS
    # ==============================================================

    @staticmethod
    def _get_supporting_indicators(
        evidence: list[dict[str, Any]],
    ) -> list[str]:
        indicators: set[str] = set()

        for item in evidence:
            supporting = (
                item.get("supporting_indicators")
                or item.get("indicators")
            )

            if supporting:
                indicators.update(supporting)
                continue

            indicator = item.get("indicator")

            if indicator:
                indicators.add(indicator)

        return sorted(indicators)

    @staticmethod
    def _get_supporting_families(
        evidence: list[dict[str, Any]],
    ) -> list[str]:
        families: set[str] = set()

        for item in evidence:
            family = item.get("family")

            if family:
                families.add(family)

        return sorted(families)

    # ==============================================================
    # SCORE AGGREGATION
    # ==============================================================

    @classmethod
    def _aggregate_scores(
        cls,
        evidence: list[dict[str, Any]],
    ) -> dict[str, float]:
        scores: dict[str, float] = {}

        for item in evidence:
            regime = item.get("regime")

            if regime not in cls.CYCLICAL_REGIMES:
                continue

            try:
                weight = float(item["weight"])
            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

            if weight <= 0:
                continue

            scores[regime] = (
                scores.get(regime, 0.0)
                + weight
            )

        return scores

    # ==============================================================
    # EMPTY RESULT
    # ==============================================================

    @staticmethod
    def _empty_result(
        indicators_used: list[str] | None = None, conditions: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "regime": "neutral",
            "conditions": conditions or [],
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
            "indicators_used": indicators_used or [],
            "multi_indicator": False,
            "families_supporting": [],
            "family_count": 0,
        }