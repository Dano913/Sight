from __future__ import annotations

from typing import Any

from app.models.investment_asset import MacroFactor


class MacroFactorScorer:
    """
    Convierte la interpretación económica de cada indicador en un
    score normalizado de un factor macroeconómico.

    El score representa la orientación del propio factor.

    Escala:

        -2.0  fuertemente negativo
        -1.0  negativo
         0.0  neutral
        +1.0  positivo
        +2.0  fuertemente positivo

    El score NO representa el impacto sobre un activo concreto.

    Ese impacto se calcula posteriormente mediante AssetScorer:

        factor_score * asset_sensitivity

    La interpretación se basa principalmente en:

        growth.state
            Estado actual de la serie.

        growth.direction
            Evolución del estado actual.

        trend.direction
            Confirmación de la evolución.

        momentum.direction
            Confirmación adicional del movimiento.

    Importante:

        direction nunca sustituye a state.

        Ejemplo:

            state = "negative"
            direction = "improving"

        significa que el indicador sigue estando en terreno negativo,
        pero está mejorando.

        Por tanto, no debe convertirse automáticamente en un score
        positivo.
    """

    INDICATOR_FACTORS: dict[str, MacroFactor] = {
        # Growth
        "GDP": MacroFactor.GROWTH,
        "REAL_GDP": MacroFactor.GROWTH,
        "GDP_GROWTH": MacroFactor.GROWTH,

        # Activity
        "INDUSTRIAL_PRODUCTION": MacroFactor.ACTIVITY,
        "RETAIL_SALES": MacroFactor.ACTIVITY,

        # Employment
        "UNEMPLOYMENT": MacroFactor.EMPLOYMENT,

        # Inflation
        "INFLATION": MacroFactor.INFLATION,
        "CPI": MacroFactor.INFLATION,

        # Interest rates
        "INTEREST_RATE": MacroFactor.INTEREST_RATES,
        "INTEREST_RATES": MacroFactor.INTEREST_RATES,

        # Housing
        "HOUSE_PRICE_INDEX": MacroFactor.HOUSING,
        "HOUSING": MacroFactor.HOUSING,

        # Trade
        "EXPORTS": MacroFactor.TRADE,
        "IMPORTS": MacroFactor.TRADE,
        "TRADE_BALANCE": MacroFactor.TRADE,
        "EXPORTS_US": MacroFactor.TRADE,
        "IMPORTS_US": MacroFactor.TRADE,
        "TRADE_BALANCE_US": MacroFactor.TRADE,
        "EXPORTS_EU": MacroFactor.TRADE,
        "IMPORTS_EU": MacroFactor.TRADE,
        "TRADE_BALANCE_EU": MacroFactor.TRADE,
        "EXPORTS_CN": MacroFactor.TRADE,
        "IMPORTS_CN": MacroFactor.TRADE,
        "TRADE_BALANCE_CN": MacroFactor.TRADE,
    }

    # Para estos indicadores, un estado positivo de la serie
    # representa una orientación negativa para el factor.
    INVERTED_INDICATORS = {
        "UNEMPLOYMENT",
    }

    @classmethod
    def score(
        cls,
        interpretations: dict[str, dict[str, Any]],
    ) -> dict[MacroFactor, float]:
        """
        Calcula los scores agregados de los factores macro.

        Si varios indicadores representan el mismo factor, sus scores
        se agregan mediante una media simple.
        """

        factor_values: dict[MacroFactor, list[float]] = {}

        for indicator_code, interpretation in interpretations.items():
            normalized_code = indicator_code.upper()

            factor = cls.INDICATOR_FACTORS.get(normalized_code)

            if factor is None:
                continue

            value = cls._indicator_score(
                interpretation=interpretation,
                indicator_code=normalized_code,
            )

            if value is None:
                continue

            factor_values.setdefault(factor, []).append(value)

        return {
            factor: cls._average(values)
            for factor, values in factor_values.items()
        }

    @classmethod
    def _indicator_score(
        cls,
        interpretation: dict[str, Any],
        indicator_code: str,
    ) -> float | None:
        """
        Calcula la orientación de un indicador concreto.

        El estado actual determina la mayor parte del score.

        Direction, trend y momentum únicamente realizan ajustes pequeños
        para representar la evolución sin sustituir al estado.
        """

        base_score = cls._base_score(interpretation)

        if base_score is None:
            return None

        score = base_score

        growth = interpretation.get("growth")

        if isinstance(growth, dict):
            score = cls._apply_growth_direction(
                score=score,
                direction=growth.get("direction"),
            )

        trend = interpretation.get("trend")

        if isinstance(trend, dict):
            score = cls._apply_trend_confirmation(
                score=score,
                direction=trend.get("direction"),
            )

        momentum = interpretation.get("momentum")

        if isinstance(momentum, dict):
            score = cls._apply_momentum_confirmation(
                score=score,
                direction=momentum.get("direction"),
            )

        if indicator_code in cls.INVERTED_INDICATORS:
            score *= -1

        return cls._normalize(score)

    @staticmethod
    def _base_score(
        interpretation: dict[str, Any],
    ) -> float | None:
        """
        Determina el score inicial a partir del estado actual del
        crecimiento.

        GrowthInterpreter define:

            positive -> estado positivo
            negative -> estado negativo
            flat     -> estado neutral

        No utilizamos growth.direction aquí porque direction describe
        evolución y no nivel.
        """

        growth = interpretation.get("growth")

        if not isinstance(growth, dict):
            return None

        state = growth.get("state")

        if state == "positive":
            return 1.0

        if state == "negative":
            return -1.0

        if state == "flat":
            return 0.0

        return None

    @staticmethod
    def _apply_growth_direction(
        *,
        score: float,
        direction: Any,
    ) -> float:
        """
        Ajusta ligeramente el score según la evolución del crecimiento.

        improving:
            mueve el score ligeramente hacia positivo.

        deteriorating:
            mueve el score ligeramente hacia negativo.

        stable / unknown:
            no modifica el score.

        La modificación es pequeña para evitar que direction sustituya
        al estado actual.
        """

        if direction == "improving":
            return score + 0.25

        if direction == "deteriorating":
            return score - 0.25

        return score

    @staticmethod
    def _apply_trend_confirmation(
        *,
        score: float,
        direction: Any,
    ) -> float:
        """
        Utiliza la dirección de tendencia como confirmación.

        strengthening:
            aumenta ligeramente la magnitud del estado actual.

        weakening:
            reduce ligeramente la magnitud del estado actual.

        stable / unknown:
            no modifica el score.
        """

        if direction == "strengthening":
            if score > 0:
                return score + 0.15

            if score < 0:
                return score - 0.15

            return score

        if direction == "weakening":
            if score > 0:
                return score - 0.15

            if score < 0:
                return score + 0.15

            return score

        return score

    @staticmethod
    def _apply_momentum_confirmation(
        *,
        score: float,
        direction: Any,
    ) -> float:
        """
        Utiliza la dirección del momentum como confirmación secundaria.

        improving:
            desplaza ligeramente el score hacia positivo.

        deteriorating:
            desplaza ligeramente el score hacia negativo.

        stable / unknown:
            no modifica el score.
        """

        if direction == "improving":
            return score + 0.10

        if direction == "deteriorating":
            return score - 0.10

        return score

    @staticmethod
    def _normalize(value: float) -> float:
        """
        Limita el score al rango [-2, 2].
        """

        return max(-2.0, min(2.0, float(value)))

    @staticmethod
    def _average(values: list[float]) -> float:
        """
        Calcula la media simple de varios scores del mismo factor.
        """

        if not values:
            return 0.0

        return MacroFactorScorer._normalize(
            sum(values) / len(values)
        )