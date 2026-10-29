from __future__ import annotations

from typing import Any

from app.models.investment_asset import (
    InvestmentAsset,
    MacroFactor,
)


class AssetScorer:
    """
    Calcula la puntuación de una exposición de inversión
    a partir del estado actual de los factores macroeconómicos.

    No interpreta datos macroeconómicos directamente.
    Recibe factores ya normalizados y aplica las sensibilidades
    definidas por cada InvestmentAsset.

    Fórmula:

        asset_score =
            sum(
                macro_factor_score * asset_sensitivity
            )

    La puntuación resultante es relativa y sirve para comparar
    activos dentro del mismo análisis.
    """

    @staticmethod
    def score(
        asset: InvestmentAsset,
        factor_scores: dict[MacroFactor, float],
    ) -> dict[str, Any]:
        contributions: dict[str, float] = {}
        total_score = 0.0

        for factor, sensitivity in asset.sensitivities.items():
            factor_score = factor_scores.get(factor, 0.0)

            contribution = factor_score * sensitivity

            contributions[factor.value] = contribution
            total_score += contribution

        return {
            "asset": asset.code,
            "name": asset.name,
            "asset_class": asset.asset_class.value,
            "asset_type": asset.asset_type.value,
            "region": asset.region,
            "score": total_score,
            "contributions": contributions,
        }

    @classmethod
    def score_all(
        cls,
        assets: list[InvestmentAsset],
        factor_scores: dict[MacroFactor, float],
    ) -> list[dict[str, Any]]:
        results = [
            cls.score(
                asset=asset,
                factor_scores=factor_scores,
            )
            for asset in assets
        ]

        return sorted(
            results,
            key=lambda result: result["score"],
            reverse=True,
        )