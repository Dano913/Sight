from __future__ import annotations


class RegimeConfidence:
    """
    Calcula la confianza del régimen macroeconómico dominante.

    La confianza depende de:

    - score del régimen dominante
    - proporción del score dominante sobre el total
    - margen respecto al segundo régimen
    - número de indicadores independientes que lo respaldan

    Un único indicador nunca puede producir confianza HIGH.
    """

    @staticmethod
    def calculate(
        *,
        dominant_score: float,
        total_score: float,
        indicator_count: int,
        score_margin: float = 0.0,
    ) -> str:

        if total_score <= 0 or dominant_score <= 0:
            return "low"

        share = dominant_score / total_score

        # Nunca permitimos confianza alta con un solo indicador.
        if indicator_count <= 1:
            if (
                dominant_score >= 4
                and share >= 0.60
                and score_margin >= 2
            ):
                return "medium"

            return "low"

        # Dos indicadores independientes.
        if indicator_count == 2:
            if (
                dominant_score >= 8
                and share >= 0.65
                and score_margin >= 3
            ):
                return "high"

            if (
                dominant_score >= 4
                and share >= 0.50
                and score_margin >= 1
            ):
                return "medium"

            return "low"

        # Tres o más indicadores independientes.
        if (
            dominant_score >= 8
            and share >= 0.60
            and score_margin >= 2
        ):
            return "high"

        if (
            dominant_score >= 4
            and share >= 0.45
            and score_margin >= 1
        ):
            return "medium"

        return "low"