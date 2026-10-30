from __future__ import annotations

from typing import Any


class CycleInterpretationService:
    """
    Interpreta los resultados producidos por CycleAnalysisService.

    Este servicio NO calcula ciclos, no modifica la evidencia
    estadística original y no determina el régimen económico actual.

    Su responsabilidad es describir:

        - si existe una periodicidad robusta,
        - cuál es el ciclo principal,
        - qué calidad tiene la evidencia,
        - cuántos ciclos son observables,
        - cuántos métodos apoyan la detección.

    El ciclo estadístico describe periodicidad histórica.
    No debe interpretarse como una predicción del próximo régimen.
    """

    MIN_CYCLES_FOR_STRONG_EVIDENCE = 3.0
    MIN_CYCLES_FOR_MODERATE_EVIDENCE = 2.0

    HIGH_SCORE = 70.0
    MEDIUM_SCORE = 55.0

    MIN_METHODS_FOR_STRONG_EVIDENCE = 3
    MIN_METHODS_FOR_MODERATE_EVIDENCE = 2

    @classmethod
    def interpret(
        cls,
        cycle_analysis: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(cycle_analysis, dict):
            raise TypeError(
                "cycle_analysis debe ser un diccionario"
            )

        cycles = cycle_analysis.get(
            "robust_cycles",
            [],
        )

        if not isinstance(cycles, list):
            raise TypeError(
                "robust_cycles debe ser una lista"
            )

        if not cycles:
            return cls._no_cycle_interpretation(
                cycle_analysis
            )

        best_cycle = cycles[0]
        if not isinstance(best_cycle, dict):
            return cls._no_cycle_interpretation(
                cycle_analysis
            )

        return {
            "cycle_detected": True,
            "best_cycle": cls._interpret_cycle(
                best_cycle
            ),
            "overall": cls._interpret_overall(
                cycles
            ),
            "caution": cls._build_caution(
                best_cycle
            ),
        }

    @classmethod
    def _interpret_cycle(
        cls,
        cycle: dict[str, Any],
    ) -> dict[str, Any]:

        score = float(
            cycle.get("score") or 0.0
        )

        confidence = cycle.get(
            "confidence"
        ) or "BAJA"

        period = float(
            cycle.get("period_years") or 0.0
        )

        cycles_observable = float(
            cycle.get(
                "cycles_observable"
            ) or 0.0
        )

        method_count = int(
            cycle.get(
                "method_count"
            ) or 0
        )

        evidence_level = cls._classify_evidence_level(
            score=score,
            confidence=confidence,
        )

        sample_quality = cls._classify_sample_quality(
            cycles_observable
        )

        method_support = cls._classify_method_support(
            method_count
        )

        robustness = cls._classify_robustness(
            evidence_level=evidence_level,
            sample_quality=sample_quality,
            method_support=method_support,
        )

        return {
            "period_years": period,
            "score": score,
            "confidence": confidence,
            "evidence_level": evidence_level,
            "method_count": method_count,
            "method_support": method_support,
            "cycles_observable": cycles_observable,
            "sample_quality": sample_quality,
            "robustness": robustness,
            "description": cls._describe_period(
                period
            ),
        }

    @classmethod
    def _classify_evidence_level(
        cls,
        *,
        score: float,
        confidence: str,
    ) -> str:

        if (
            confidence == "ALTA"
            and score >= cls.HIGH_SCORE
        ):
            return "strong"

        if (
            confidence in {"ALTA", "MEDIA"}
            and score >= cls.MEDIUM_SCORE
        ):
            return "moderate"

        return "weak"

    @classmethod
    def _classify_sample_quality(
        cls,
        cycles_observable: float,
    ) -> str:

        if (
            cycles_observable
            >= cls.MIN_CYCLES_FOR_STRONG_EVIDENCE
        ):
            return "strong"

        if (
            cycles_observable
            >= cls.MIN_CYCLES_FOR_MODERATE_EVIDENCE
        ):
            return "moderate"

        return "limited"

    @classmethod
    def _classify_method_support(
        cls,
        method_count: int,
    ) -> str:

        if (
            method_count
            >= cls.MIN_METHODS_FOR_STRONG_EVIDENCE
        ):
            return "strong"

        if (
            method_count
            >= cls.MIN_METHODS_FOR_MODERATE_EVIDENCE
        ):
            return "moderate"

        return "limited"

    @staticmethod
    def _classify_robustness(
        *,
        evidence_level: str,
        sample_quality: str,
        method_support: str,
    ) -> str:

        if (
            evidence_level == "strong"
            and sample_quality == "strong"
            and method_support == "strong"
        ):
            return "strong"

        if (
            evidence_level in {"strong", "moderate"}
            and sample_quality in {"strong", "moderate"}
            and method_support in {"strong", "moderate"}
        ):
            return "moderate"

        return "limited"

    @staticmethod
    def _describe_period(
        period: float,
    ) -> str:

        if period < 3:
            return "ciclo relativamente corto"

        if period < 5:
            return "ciclo de duración corta-media"

        if period < 8:
            return "ciclo de duración media"

        if period < 12:
            return "ciclo de duración larga"

        return "ciclo de duración muy larga"

    @classmethod
    def _interpret_overall(
        cls,
        cycles: list[dict[str, Any]],
    ) -> dict[str, Any]:

        best = cycles[0]

        score = float(
            best.get("score") or 0.0
        )

        confidence = best.get(
            "confidence"
        ) or "BAJA"

        evidence_level = cls._classify_evidence_level(
            score=score,
            confidence=confidence,
        )

        cycles_observable = float(
            best.get(
                "cycles_observable"
            ) or 0.0
        )

        method_count = int(
            best.get(
                "method_count"
            ) or 0
        )

        sample_quality = cls._classify_sample_quality(
            cycles_observable
        )

        method_support = cls._classify_method_support(
            method_count
        )

        robustness = cls._classify_robustness(
            evidence_level=evidence_level,
            sample_quality=sample_quality,
            method_support=method_support,
        )

        return {
            "assessment": cls._overall_assessment(
                robustness
            ),
            "robustness": robustness,
            "cycles_detected": len(cycles),
            "best_score": score,
            "best_confidence": confidence,
            "best_evidence_level": evidence_level,
            "best_sample_quality": sample_quality,
            "best_method_support": method_support,
        }

    @staticmethod
    def _overall_assessment(
        robustness: str,
    ) -> str:

        if robustness == "strong":
            return "strong_evidence"

        if robustness == "moderate":
            return "moderate_evidence"

        return "weak_evidence"

    @staticmethod
    def _no_cycle_interpretation(
        cycle_analysis: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "cycle_detected": False,
            "best_cycle": None,
            "overall": {
                "assessment": "no_sufficient_evidence",
                "robustness": "limited",
                "cycles_detected": 0,
            },
            "caution": (
                "No se ha encontrado evidencia suficiente "
                "para identificar una periodicidad robusta."
            ),
        }

    @staticmethod
    def _build_caution(
        cycle: dict[str, Any],
    ) -> str:

        cycles_observable = float(
            cycle.get(
                "cycles_observable"
            ) or 0.0
        )

        method_count = int(
            cycle.get(
                "method_count"
            ) or 0
        )

        if cycles_observable < 2:
            return (
                "La muestra contiene menos de dos ciclos "
                "observables. La periodicidad debe "
                "interpretarse con mucha cautela."
            )

        if cycles_observable < 3:
            return (
                "La muestra contiene menos de tres ciclos "
                "completos observables. Existe evidencia "
                "estadística, pero la estabilidad del ciclo "
                "no puede considerarse demostrada."
            )

        if method_count < 3:
            return (
                "La periodicidad no ha sido identificada "
                "por los tres métodos utilizados. "
                "La evidencia es parcial."
            )

        return (
            "La periodicidad presenta evidencia consistente "
            "entre métodos. Aun así, la detección estadística "
            "no demuestra causalidad ni garantiza que el ciclo "
            "se mantenga en el futuro."
        )