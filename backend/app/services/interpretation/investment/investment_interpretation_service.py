from __future__ import annotations

from typing import Any

from .confidence_estimator import ConfidenceEstimator
from .environment_interpreter import EnvironmentInterpreter
from .opportunity_interpreter import OpportunityInterpreter
from .risk_interpreter import RiskInterpreter
from .signal_generator import SignalGenerator


class InvestmentInterpretationService:
    """
    Orquesta la interpretación macroeconómica desde una perspectiva
    orientada a inversión.

    Este servicio NO:

        - calcula features,
        - obtiene datos,
        - realiza valoración fundamental,
        - selecciona activos,
        - genera órdenes,
        - genera recomendaciones BUY/SELL,
        - construye carteras.

    Su función es consumir la interpretación económica ya construida
    y distribuirla entre los distintos componentes de interpretación
    de inversión.

    Flujo:

        FeatureEngine
            ↓
        FeatureAnalysisService
            ↓
        EconomicInterpretationService
            ↓
        InvestmentInterpretationService
            ↓
        InvestmentAnalysisService

    La interpretación de inversión se divide en:

        environment
            → describe el entorno macro actual.

        risk
            → identifica fragilidad, deterioro y estrés macro.

        opportunity
            → identifica evidencia macro compatible con una
              oportunidad potencial.

        signals
            → expone señales estructuradas sin reinterpretarlas.

        confidence
            → estima la coherencia y claridad de la interpretación.

    Ninguno de estos componentes asigna por sí mismo una valoración
    de activos ni constituye una recomendación de inversión.
    """

    REQUIRED_SECTIONS = {
        "growth",
        "trend",
        "momentum",
        "volatility",
        "position",
        "transition",
        "regime",
    }

    @classmethod
    def analyze(
        cls,
        economic_interpretation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Genera una interpretación estructurada desde la perspectiva
        de inversión.

        El método únicamente orquesta los intérpretes. No realiza
        cálculos adicionales ni vuelve a interpretar las señales.
        """

        cls._validate_input(economic_interpretation)

        sections = cls._extract_sections(
            economic_interpretation
        )

        environment = EnvironmentInterpreter.interpret(
            **sections
        )

        risk = RiskInterpreter.interpret(
            **sections
        )

        opportunity = OpportunityInterpreter.interpret(
            **sections
        )

        signals = SignalGenerator.generate(
            **sections
        )

        confidence = ConfidenceEstimator.estimate(
            **sections
        )

        return {
            "indicator": economic_interpretation.get(
                "indicator"
            ),
            "region": economic_interpretation.get(
                "region"
            ),
            "date": economic_interpretation.get(
                "date"
            ),
            "regime": sections["regime"],
            "transition": sections["transition"],
            "environment": environment,
            "risk": risk,
            "opportunity": opportunity,
            "signals": signals,
            "confidence": confidence,
        }

    @classmethod
    def _validate_input(
        cls,
        economic_interpretation: dict[str, Any],
    ) -> None:
        """
        Valida que la interpretación económica contenga
        todas las secciones necesarias.
        """

        if not isinstance(
            economic_interpretation,
            dict,
        ):
            raise TypeError(
                "economic_interpretation debe ser un dict"
            )

        missing_sections = (
            cls.REQUIRED_SECTIONS
            - set(economic_interpretation)
        )

        if missing_sections:
            raise ValueError(
                "Faltan secciones necesarias en "
                "economic_interpretation: "
                f"{sorted(missing_sections)}"
            )

        for section in cls.REQUIRED_SECTIONS - {"regime"}:
            if not isinstance(
                economic_interpretation[section],
                dict,
            ):
                raise TypeError(
                    f"La sección '{section}' "
                    "debe ser un dict"
                )

        if not isinstance(
            economic_interpretation["regime"],
            str,
        ):
            raise TypeError(
                "La sección 'regime' debe ser un str"
            )

    @classmethod
    def _extract_sections(
        cls,
        economic_interpretation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extrae únicamente las secciones que consumen
        los intérpretes de inversión.

        No transforma ni reinterpreta su contenido.
        """

        return {
            "growth": economic_interpretation["growth"],
            "trend": economic_interpretation["trend"],
            "momentum": economic_interpretation["momentum"],
            "volatility": economic_interpretation["volatility"],
            "position": economic_interpretation["position"],
            "transition": economic_interpretation["transition"],
            "regime": economic_interpretation["regime"],
        }