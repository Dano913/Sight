from __future__ import annotations

from typing import Any

from app.services.analysis.investment.alert_analyzer import AlertAnalyzer
from app.services.analysis.investment.horizon_analyzer import HorizonAnalyzer
from app.services.analysis.investment.macro_bias_analyzer import MacroBiasAnalyzer
from app.services.analysis.investment.overall_assessment_builder import (
    OverallAssessmentBuilder,
)
from app.services.analysis.investment.conviction_analyzer import (
    ConvictionAnalyzer,
)


class InvestmentAnalysisService:
    """
    Orquesta la síntesis final de la interpretación macroeconómica
    desde una perspectiva de inversión.

    Este servicio NO vuelve a interpretar la transición económica.

    La transición recibida desde InvestmentInterpretationService
    constituye la fuente canónica de información sobre transición.

    Su función es combinar:

        environment
        risk
        opportunity
        transition
        confidence

    para construir las capas superiores de análisis:

        macro_bias
        horizon
        alerts
        conviction
        overall

    Este servicio tampoco:

        - calcula features,
        - obtiene datos,
        - selecciona activos,
        - genera órdenes,
        - realiza valoración fundamental.
    """

    REQUIRED_SECTIONS = {
        "environment",
        "risk",
        "opportunity",
        "transition",
        "signals",
        "confidence",
        "regime",
    }

    @staticmethod
    def analyze(
        investment_interpretation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Genera la síntesis final del análisis de inversión.

        La transición utilizada por todos los componentes procede
        directamente de InvestmentInterpretationService.
        """

        InvestmentAnalysisService._validate(
            investment_interpretation
        )

        environment = investment_interpretation["environment"]
        risk = investment_interpretation["risk"]
        opportunity = investment_interpretation["opportunity"]
        transition = investment_interpretation["transition"]
        signals = investment_interpretation["signals"]
        confidence = investment_interpretation["confidence"]
        regime = investment_interpretation["regime"]

        macro_bias = MacroBiasAnalyzer.analyze(
            environment=environment,
            risk=risk,
            opportunity=opportunity,
            signals=signals,
            regime=regime,
            transition=transition,
        )

        horizon = HorizonAnalyzer.analyze(
            environment=environment,
            risk=risk,
            opportunity=opportunity,
            signals=signals,
            regime=regime,
            transition=transition,
        )

        alerts = AlertAnalyzer.analyze(
            signals=signals,
            transition=transition,
        )

        conviction = ConvictionAnalyzer.analyze(
            environment=environment,
            risk=risk,
            opportunity=opportunity,
            confidence=confidence,
            transition=transition,
        )

        overall = OverallAssessmentBuilder.build(
            environment=environment,
            risk=risk,
            opportunity=opportunity,
            confidence=confidence,
            macro_bias=macro_bias,
            conviction=conviction,
            transition=transition,
        )

        return {
            "indicator": investment_interpretation.get(
                "indicator"
            ),
            "region": investment_interpretation.get(
                "region"
            ),
            "date": investment_interpretation.get(
                "date"
            ),
            "regime": regime,
            "overall": overall,
            "environment": environment,
            "risk": risk,
            "opportunity": opportunity,
            "macro_bias": macro_bias,
            "transition": transition,
            "horizon": horizon,
            "conviction": conviction,
            "alerts": alerts,
            "signals": signals,
            "confidence": confidence,
        }

    @classmethod
    def _validate(
        cls,
        investment_interpretation: dict[str, Any],
    ) -> None:
        """
        Valida que la interpretación de inversión contenga
        todas las secciones necesarias.
        """

        if not isinstance(
            investment_interpretation,
            dict,
        ):
            raise TypeError(
                "investment_interpretation debe ser un dict"
            )

        missing_sections = (
            cls.REQUIRED_SECTIONS
            - set(investment_interpretation)
        )

        if missing_sections:
            raise ValueError(
                "Faltan secciones necesarias en "
                "investment_interpretation: "
                f"{sorted(missing_sections)}"
            )

        for section in (
            cls.REQUIRED_SECTIONS
            - {"regime"}
        ):
            if not isinstance(
                investment_interpretation[section],
                dict,
            ):
                raise TypeError(
                    f"La sección '{section}' "
                    "debe ser un dict"
                )

        if not isinstance(
            investment_interpretation["regime"],
            str,
        ):
            raise TypeError(
                "La sección 'regime' debe ser un str"
            )