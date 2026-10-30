from __future__ import annotations

from typing import Any

import pandas as pd

from .assessment_builder import AssessmentBuilder
from .growth_interpreter import GrowthInterpreter
from .momentum_interpreter import MomentumInterpreter
from .position_interpreter import PositionInterpreter
from .regime_classifier import RegimeClassifier
from ..constants import REQUIRED_FEATURES, REQUIRED_SIGNALS
from .transition_detector import TransitionDetector
from .trend_interpreter import TrendInterpreter
from ..utils import safe_bool, serialize
from .volatility_interpreter import VolatilityInterpreter


class EconomicInterpretationService:

    @staticmethod
    def analyze(
        features: pd.DataFrame,
        signals: pd.DataFrame,
        *,
        indicator_code: str | None = None,
        region_code: str | None = None,
    ) -> dict[str, Any]:

        EconomicInterpretationService._validate_inputs(
            features,
            signals,
        )

        latest = features.iloc[-1]
        latest_signals = signals.iloc[-1]

        growth = GrowthInterpreter.interpret(
            latest,
            latest_signals,
        )

        trend = TrendInterpreter.interpret(
            latest,
            latest_signals,
        )

        momentum = MomentumInterpreter.interpret(
            latest,
            latest_signals,
        )

        volatility = VolatilityInterpreter.interpret(
            latest,
            latest_signals,
        )

        position = PositionInterpreter.interpret(
            latest,
            latest_signals,
        )

        transition = TransitionDetector.detect(
            growth=growth,
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            position=position,
        )

        regime = RegimeClassifier.classify(
            growth=growth,
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            position=position,
            transition=transition,
        )

        assessment = AssessmentBuilder.build(
            growth=growth,
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            position=position,
            transition=transition,
            regime=regime,
        )

        return {
            "indicator": indicator_code,
            "region": region_code,
            "date": serialize(features.index[-1]),
            "regime": regime,
            "growth": growth,
            "trend": trend,
            "momentum": momentum,
            "volatility": volatility,
            "position": position,
            "transition": transition,
            "assessment": assessment,
            "history": {
                "observations": len(features),
                "start": serialize(features.index[0]),
                "end": serialize(features.index[-1]),
            },
            "current": {
                column: serialize(latest[column])
                for column in REQUIRED_FEATURES
                if column in features.columns
            } | {
                column: serialize(latest[column])
                for column in ("percentage_change", "change")
                if column in features.columns
            },
            "signals": {
                column: safe_bool(latest_signals[column])
                for column in REQUIRED_SIGNALS
            },
        }

    @staticmethod
    def _validate_inputs(
        features: pd.DataFrame,
        signals: pd.DataFrame,
    ) -> None:

        if not isinstance(features, pd.DataFrame):
            raise TypeError(
                "features debe ser un pandas.DataFrame"
            )

        if not isinstance(signals, pd.DataFrame):
            raise TypeError(
                "signals debe ser un pandas.DataFrame"
            )

        if features.empty:
            raise ValueError(
                "features no puede estar vacío"
            )

        if signals.empty:
            raise ValueError(
                "signals no puede estar vacío"
            )

        if not features.index.equals(signals.index):
            raise ValueError(
                "features y signals deben tener el mismo índice"
            )

        missing_features = (
            REQUIRED_FEATURES - set(features.columns)
        )

        if missing_features:
            raise ValueError(
                "Faltan features necesarios: "
                f"{sorted(missing_features)}"
            )

        missing_signals = (
            REQUIRED_SIGNALS - set(signals.columns)
        )

        if missing_signals:
            raise ValueError(
                "Faltan señales necesarias: "
                f"{sorted(missing_signals)}"
            )
