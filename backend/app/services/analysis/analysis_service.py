from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any

import pandas as pd

from .cycle.cycle_analysis_service import CycleAnalysisService
from ..features.feature_engine import FeatureEngine
from ..interpretation.macro.cycle_interpretation_service import (
    CycleInterpretationService,
)
from ..interpretation.macro.economic_interpretation_service import (
    EconomicInterpretationService,
)
from ..features.feature_analysis_service import FeatureAnalysisService
from ..interpretation.investment.investment_interpretation_service import (
    InvestmentInterpretationService,
)
from .investment.asset.asset_registry import AssetRegistry
from .investment.asset.asset_scorer import AssetScorer
from .investment.asset.macro_factor_scorer import MacroFactorScorer
from .investment.investment_analysis_service import (
    InvestmentAnalysisService,
)
from .macro_regime.macro_regime_service import MacroRegimeService


class AnalysisService:
    """
    Orquestador central del análisis macroeconómico.

    Permite analizar:

        1. Un único indicador
        2. Múltiples indicadores

    Flujo individual:

        Observations
              ↓
        Desambiguación por fuente
              ↓
        FeatureEngine
              ↓
        FeatureAnalysisService
              ↓
        CycleAnalysisService
              ↓
        CycleInterpretationService
              ↓
        EconomicInterpretationService
              ↓
        InvestmentInterpretationService

    Flujo multi-indicador:

        Observations de múltiples indicadores
              ↓
        AnalysisService
              ↓
        Análisis individual de cada indicador
              ↓
        MacroRegimeService
              ↓
        Régimen macroeconómico agregado
              ↓
        MacroFactorScorer
              ↓
        Factores macro normalizados
              ↓
        AssetRegistry + AssetScorer
              ↓
        Ranking de activos

    Este servicio NO implementa lógica matemática ni reglas de
    interpretación propias.

    Su responsabilidad es coordinar los diferentes motores.
    """

    # ==============================================================
    # ANÁLISIS DE UN INDICADOR
    # ==============================================================

    @classmethod
    def analyze(
        cls,
        observations,
        *,
        source_code: str | None = None,
        level_window: int = 8,
        trend_short_window: int = 4,
        trend_medium_window: int = 8,
        trend_long_window: int = 16,
        volatility_window: int = 8,
        extreme_window: int = 8,
        cycle_top_n: int = 5,
        hp_lambda: float = 100.0,
    ) -> dict[str, Any]:
        """
        Ejecuta el análisis completo de una serie de observaciones.

        Todas las observaciones deben pertenecer al mismo indicador.

        Si hay observaciones de varias fuentes para el mismo indicador,
        se debe indicar `source_code` explícitamente; si no se indica
        y solo hay una fuente presente, se usa esa.
        """

        if not observations:
            raise ValueError(
                "No hay observaciones para analizar."
            )

        # ==========================================================
        # 1. VALIDAR INDICADOR
        # ==========================================================

        indicator_ids = {
            observation.indicator.id
            for observation in observations
        }

        if len(indicator_ids) != 1:
            raise ValueError(
                "Todas las observaciones deben pertenecer "
                "al mismo indicador."
            )

        indicator = observations[0].indicator
        frequency = indicator.frequency.value

        # ==========================================================
        # 2. DESAMBIGUAR POR FUENTE
        # ==========================================================

        #
        # Un mismo indicador/región puede tener observaciones de
        # varias fuentes (p. ej. BEA y OECD). Mezclarlas sin
        # desambiguar produce una serie inconsistente.
        #

        series_by_source = cls._build_series_by_source(
            observations
        )

        if source_code is not None:
            source_code = source_code.upper()

            if source_code not in series_by_source:
                raise ValueError(
                    f"No hay observaciones de la fuente "
                    f"{source_code} para este indicador."
                )

            series = series_by_source[source_code]

        elif len(series_by_source) == 1:
            series = next(iter(series_by_source.values()))

        else:
            raise ValueError(
                "Hay observaciones de múltiples fuentes "
                f"({sorted(series_by_source)}) para este indicador; "
                "especifica `source_code`."
            )

        ordered_observations = sorted(
            (
                observation
                for observation in observations
                if source_code is None
                or observation.source.code == source_code
            ),
            key=lambda observation: observation.date,
        )

        # ==========================================================
        # 3. DATOS ORIGINALES
        # ==========================================================

        original_data = [
            {
                "date": observation.date.isoformat(),
                "value": float(observation.value),
                "region": observation.region.code,
                "indicator": observation.indicator.code,
                "source": observation.source.code,
            }
            for observation in ordered_observations
        ]

        # ==========================================================
        # 4. FEATURES
        # ==========================================================

        features = FeatureEngine.compute(
            series=series,
            frequency=frequency,
            growth_method=indicator.growth_method,
            level_window=level_window,
            trend_short_window=trend_short_window,
            trend_medium_window=trend_medium_window,
            trend_long_window=trend_long_window,
            volatility_window=volatility_window,
            extreme_window=extreme_window,
        )

        # ==========================================================
        # 5. SEÑALES
        # ==========================================================

        signals = FeatureAnalysisService.analyze(
            features
        )

        # ==========================================================
        # 6. ANÁLISIS DE CICLOS
        # ==========================================================

        try:
            cycle_analysis = CycleAnalysisService.analyze(
                observations=ordered_observations,
                top_n=cycle_top_n,
                hp_lambda=hp_lambda,
            )
        except ValueError as exc:
            if "valores positivos" in str(exc):
                cycle_analysis = {
                    "available": False,
                    "reason": "La serie no permite análisis logarítmico.",
                }
            else:
                raise

        # ==========================================================
        # 7. INTERPRETACIÓN DE CICLOS
        # ==========================================================

        cycle_interpretation = (
            CycleInterpretationService.interpret(
                cycle_analysis
            )
        )

        # ==========================================================
        # 8. INTERPRETACIÓN ECONÓMICA
        # ==========================================================

        economic_interpretation = (
            EconomicInterpretationService.analyze(
                features=features,
                signals=signals,
                indicator_code=indicator.code,
                region_code=ordered_observations[0].region.code,
            )
        )

        # ==========================================================
        # 9. INTERPRETACIÓN DE INVERSIÓN
        # ==========================================================

        investment_interpretation = (
            InvestmentInterpretationService.analyze(
                economic_interpretation=economic_interpretation,
            )
        )

        # ==========================================================
        # 10. SÍNTESIS DE INVERSIÓN (TESIS CUALITATIVA)
        # ==========================================================

        investment_analysis = (
            InvestmentAnalysisService.analyze(
                investment_interpretation
            )
        )

        # ==========================================================
        # 11. SERIALIZACIÓN
        # ==========================================================

        features_data = cls._dataframe_to_records(
            features
        )

        signals_data = cls._dataframe_to_records(
            signals
        )

        # ==========================================================
        # 12. RESULTADO
        # ==========================================================

        return {
            "indicator": indicator.code,
            "region": ordered_observations[0].region.code,
            "data": {
                "observations": original_data,
                "frequency": frequency,
                "count": len(original_data),
            },
            "features": features_data,
            "signals": signals_data,
            "cycles": cycle_analysis,
            "cycle_interpretation": cycle_interpretation,
            "economic_interpretation": economic_interpretation,
            "investment_interpretation": investment_interpretation,
            "investment_analysis": investment_analysis,
        }

    # ==============================================================
    # ANÁLISIS MULTI-INDICADOR
    # ==============================================================

    @classmethod
    def analyze_multiple(
        cls,
        observations,
        *,
        as_of_date: str | date | datetime | None = None,
        max_lag_days: int | None = 180,
        level_window: int = 8,
        trend_short_window: int = 4,
        trend_medium_window: int = 8,
        trend_long_window: int = 16,
        volatility_window: int = 8,
        extreme_window: int = 8,
        cycle_top_n: int = 5,
        hp_lambda: float = 100.0,
    ) -> dict[str, Any]:
        """
        Ejecuta el análisis macroeconómico sobre múltiples indicadores.

        Parámetros temporales y de alineación:
        --------------------------------------
        as_of_date:
            Fecha de corte opcional para análisis point-in-time o backtesting.
            Si se indica, descarta observaciones posteriores a esta fecha.
        max_lag_days:
            Máximo número de días de rezago tolerado respecto a la fecha
            de referencia global. Si un indicador tiene una última observación
            con un desfase superior a este umbral, se marca como 'stale'
            y se excluye de la votación del régimen macro y del scoring
            de activos para evitar contaminación con datos obsoletos.
            Por defecto: 180 días (~2 trimestres). None desactiva el filtro.

        Nota: si algún indicador tiene observaciones de varias fuentes,
        `analyze()` lanzará ValueError para ese indicador — este método
        no permite especificar `source_code` por indicador. Si tu
        conjunto de datos tiene indicadores multi-fuente, hay que
        filtrar `observations` a una sola fuente por indicador antes
        de llamar aquí.

        Parameters
        ----------
        observations:
            Lista de objetos Observation pertenecientes a uno o
            varios indicadores.

        Returns
        -------
        dict
            Resultado agregado con sección de alineamiento temporal.
        """

        if not observations:
            raise ValueError(
                "No hay observaciones para analizar."
            )

        # ==========================================================
        # 1. FILTRADO POR AS_OF_DATE (POINT-IN-TIME)
        # ==========================================================

        if as_of_date is not None:
            cutoff = cls._normalize_date(as_of_date)
            observations = [
                obs
                for obs in observations
                if cls._normalize_date(obs.date) <= cutoff
            ]

            if not observations:
                raise ValueError(
                    f"No hay observaciones disponibles en o antes de {cutoff}."
                )

        # ==========================================================
        # 2. VALIDAR REGIÓN
        # ==========================================================

        regions = {
            observation.region.code
            for observation in observations
        }

        if len(regions) != 1:
            raise ValueError(
                "Todas las observaciones del análisis "
                "multi-indicador deben pertenecer a la misma región."
            )

        region = next(iter(regions))

        # ==========================================================
        # 3. AGRUPAR POR INDICADOR
        # ==========================================================

        grouped_observations = defaultdict(list)

        for observation in observations:
            indicator_code = observation.indicator.code

            grouped_observations[indicator_code].append(
                observation
            )

        # ==========================================================
        # 4. FECHA DE REFERENCIA Y ANÁLISIS INDIVIDUAL
        # ==========================================================

        reference_date = max(
            cls._normalize_date(obs.date)
            for obs in observations
        )

        indicator_results: dict[str, dict[str, Any]] = {}
        indicator_dates: dict[str, str] = {}
        indicator_lags: dict[str, int] = {}

        for (
            indicator_code,
            indicator_observations,
        ) in grouped_observations.items():

            indicator_results[indicator_code] = cls.analyze(
                indicator_observations,
                level_window=level_window,
                trend_short_window=trend_short_window,
                trend_medium_window=trend_medium_window,
                trend_long_window=trend_long_window,
                volatility_window=volatility_window,
                extreme_window=extreme_window,
                cycle_top_n=cycle_top_n,
                hp_lambda=hp_lambda,
            )

            latest_ind_date = max(
                cls._normalize_date(obs.date)
                for obs in indicator_observations
            )
            lag_days = (reference_date - latest_ind_date).days

            indicator_dates[indicator_code] = latest_ind_date.isoformat()
            indicator_lags[indicator_code] = lag_days

        # ==========================================================
        # 5. ALINEACIÓN TEMPORAL Y SEGREGACIÓN DE INDICADORES OBSOLETOS
        # ==========================================================

        active_indicators: list[str] = []
        stale_indicators: list[str] = []

        for indicator_code, lag_days in indicator_lags.items():
            if max_lag_days is not None and lag_days > max_lag_days:
                stale_indicators.append(indicator_code)
            else:
                active_indicators.append(indicator_code)

        active_interpretations = {
            indicator_code: indicator_results[indicator_code][
                "economic_interpretation"
            ]
            for indicator_code in active_indicators
        }

        # ==========================================================
        # 6. RÉGIMEN MACROECONÓMICO Y FACTORES
        # ==========================================================

        if active_interpretations:
            macro_regime = MacroRegimeService.classify(
                active_interpretations
            )

            macro_factor_scores = MacroFactorScorer.score(
                active_interpretations
            )

            assets = AssetRegistry().get_all()

            asset_scores = AssetScorer.score_all(
                assets=assets,
                factor_scores=macro_factor_scores,
            )
        else:
            macro_regime = MacroRegimeService._empty_result(
                indicators_used=list(grouped_observations)
            )
            macro_factor_scores = {}
            asset_scores = []

        # ==========================================================
        # 7. RESULTADO AGREGADO
        # ==========================================================

        return {
            "region": region,
            "date": reference_date.isoformat(),
            "temporal_alignment": {
                "reference_date": reference_date.isoformat(),
                "as_of_date": (
                    cls._normalize_date(as_of_date).isoformat()
                    if as_of_date is not None
                    else None
                ),
                "max_lag_days": max_lag_days,
                "indicator_dates": indicator_dates,
                "indicator_lags_days": indicator_lags,
                "active_indicators": sorted(active_indicators),
                "stale_indicators": sorted(stale_indicators),
            },
            "indicators": indicator_results,
            "macro_regime": macro_regime,
            "macro_factor_scores": {
                factor.value: score
                for factor, score in macro_factor_scores.items()
            },
            "asset_scores": asset_scores,
            "indicator_count": len(indicator_results),
            "indicators_analyzed": sorted(
                indicator_results.keys()
            ),
            "indicators_active": sorted(active_indicators),
        }

    # ==============================================================
    # SERIES POR FUENTE
    # ==============================================================

    @staticmethod
    def _build_series_by_source(
        observations,
    ) -> dict[str, pd.Series]:
        """
        Agrupa las observaciones por fuente y construye una serie
        temporal por cada una, ordenada por fecha y deduplicada
        (última observación gana en caso de fecha repetida).
        """

        values_by_source: dict[str, list[tuple]] = {}

        for observation in observations:
            source = observation.source.code

            values_by_source.setdefault(
                source,
                [],
            ).append(
                (
                    observation.date,
                    observation.value,
                )
            )

        series_by_source: dict[str, pd.Series] = {}

        for source, values in values_by_source.items():
            series = pd.Series(
                data=[
                    value
                    for _, value in values
                ],
                index=pd.to_datetime(
                    [
                        date
                        for date, _ in values
                    ]
                ),
                name="value",
            )

            series_by_source[source] = (
                series
                .sort_index()
                .groupby(level=0)
                .last()
            )

        return series_by_source

    # ==============================================================
    # SERIALIZACIÓN
    # ==============================================================

    @staticmethod
    def _dataframe_to_records(
        dataframe: pd.DataFrame,
    ) -> list[dict]:
        """
        Convierte un DataFrame temporal en registros serializables.

        Los NaN se convierten en None para que el resultado pueda
        ser devuelto directamente por FastAPI/JSON.
        """

        result = []

        for index, row in dataframe.iterrows():
            record = {
                "date": (
                    index.isoformat()
                    if hasattr(index, "isoformat")
                    else str(index)
                ),
            }

            for column, value in row.items():
                if pd.isna(value):
                    record[column] = None

                elif hasattr(value, "item"):
                    record[column] = value.item()

                else:
                    record[column] = value

            result.append(record)

        return result

    # ==============================================================
    # NORMALIZACIÓN DE FECHAS
    # ==============================================================

    @staticmethod
    def _normalize_date(d: Any) -> date:
        """
        Normaliza cualquier representación temporal a un objeto datetime.date.
        """
        if isinstance(d, datetime):
            return d.date()
        if isinstance(d, date):
            return d
        return pd.to_datetime(d).date()