from __future__ import annotations

import pandas as pd
import pytest

from app.services.interpretation.constants import REQUIRED_FEATURES, REQUIRED_SIGNALS
from app.services.interpretation.macro.economic_interpretation_service import (
    EconomicInterpretationService,
)


def make_features(rows: int = 2) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=rows, freq="MS")

    data = {
        column: [float(i + 1) for i in range(rows)]
        for column in REQUIRED_FEATURES
    }

    return pd.DataFrame(data, index=index)


def make_signals(rows: int = 2) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=rows, freq="MS")

    data = {
        column: [False] * rows
        for column in REQUIRED_SIGNALS
    }

    return pd.DataFrame(data, index=index)


def make_interpretations() -> dict[str, object]:
    return {
        "growth": {"state": "positive", "direction": "improving"},
        "trend": {"state": "bullish", "direction": "improving"},
        "momentum": {"state": "positive", "direction": "improving"},
        "volatility": {"level": "normal", "direction": "stable"},
        "position": {"state": "neutral"},
        "transition": {
            "detected": False,
            "direction": "stable",
        },
    }


@pytest.mark.parametrize(
    "invalid_features",
    [
        None,
        "invalid",
        [],
    ],
)
def test_validate_inputs_rejects_invalid_features(invalid_features):
    signals = make_signals()

    with pytest.raises(TypeError, match="features"):
        EconomicInterpretationService._validate_inputs(
            invalid_features,
            signals,
        )


@pytest.mark.parametrize(
    "invalid_signals",
    [
        None,
        "invalid",
        [],
    ],
)
def test_validate_inputs_rejects_invalid_signals(invalid_signals):
    features = make_features()

    with pytest.raises(TypeError, match="signals"):
        EconomicInterpretationService._validate_inputs(
            features,
            invalid_signals,
        )


def test_validate_inputs_rejects_empty_features():
    features = pd.DataFrame(columns=list(REQUIRED_FEATURES))
    signals = make_signals()

    with pytest.raises(ValueError, match="features no puede estar vacío"):
        EconomicInterpretationService._validate_inputs(
            features,
            signals,
        )


def test_validate_inputs_rejects_empty_signals():
    features = make_features()
    signals = pd.DataFrame(columns=list(REQUIRED_SIGNALS))

    with pytest.raises(ValueError, match="signals no puede estar vacío"):
        EconomicInterpretationService._validate_inputs(
            features,
            signals,
        )


def test_validate_inputs_requires_matching_indices():
    features = make_features(rows=2)
    signals = make_signals(rows=2)
    signals.index = pd.date_range("2025-01-01", periods=2, freq="MS")

    with pytest.raises(
        ValueError,
        match="mismo índice",
    ):
        EconomicInterpretationService._validate_inputs(
            features,
            signals,
        )


def test_validate_inputs_rejects_missing_features():
    features = make_features().drop(columns=[next(iter(REQUIRED_FEATURES))])
    signals = make_signals()

    with pytest.raises(
        ValueError,
        match="Faltan features necesarios",
    ):
        EconomicInterpretationService._validate_inputs(
            features,
            signals,
        )


def test_validate_inputs_rejects_missing_signals():
    signals = make_signals().drop(columns=[next(iter(REQUIRED_SIGNALS))])
    features = make_features()

    with pytest.raises(
        ValueError,
        match="Faltan señales necesarias",
    ):
        EconomicInterpretationService._validate_inputs(
            features,
            signals,
        )


def test_validate_inputs_accepts_valid_inputs():
    features = make_features()
    signals = make_signals()

    EconomicInterpretationService._validate_inputs(
        features,
        signals,
    )


def _patch_interpretation_components(
    monkeypatch,
    interpretations: dict[str, object],
    calls: dict[str, object] | None = None,
):
    calls = calls if calls is not None else {}

    def growth_interpret(latest, latest_signals):
        calls["growth"] = (latest, latest_signals)
        return interpretations["growth"]

    def trend_interpret(latest, latest_signals):
        calls["trend"] = (latest, latest_signals)
        return interpretations["trend"]

    def momentum_interpret(latest, latest_signals):
        calls["momentum"] = (latest, latest_signals)
        return interpretations["momentum"]

    def volatility_interpret(latest, latest_signals):
        calls["volatility"] = (latest, latest_signals)
        return interpretations["volatility"]

    def position_interpret(latest, latest_signals):
        calls["position"] = (latest, latest_signals)
        return interpretations["position"]

    def transition_detect(**kwargs):
        calls["transition"] = kwargs
        return interpretations["transition"]

    def regime_classify(**kwargs):
        calls["regime"] = kwargs
        return "expansion"

    assessment = {
        "state": "expanding",
        "directional_bias": "improving",
        "regime": "expansion",
        "coherence": "high",
        "confidence": "high",
        "reasons": [],
    }

    def assessment_build(**kwargs):
        calls["assessment"] = kwargs
        return assessment

    module = (
        "app.services.interpretation.macro."
        "economic_interpretation_service"
    )

    monkeypatch.setattr(
        f"{module}.GrowthInterpreter.interpret",
        growth_interpret,
    )
    monkeypatch.setattr(
        f"{module}.TrendInterpreter.interpret",
        trend_interpret,
    )
    monkeypatch.setattr(
        f"{module}.MomentumInterpreter.interpret",
        momentum_interpret,
    )
    monkeypatch.setattr(
        f"{module}.VolatilityInterpreter.interpret",
        volatility_interpret,
    )
    monkeypatch.setattr(
        f"{module}.PositionInterpreter.interpret",
        position_interpret,
    )
    monkeypatch.setattr(
        f"{module}.TransitionDetector.detect",
        transition_detect,
    )
    monkeypatch.setattr(
        f"{module}.RegimeClassifier.classify",
        regime_classify,
    )
    monkeypatch.setattr(
        f"{module}.AssessmentBuilder.build",
        assessment_build,
    )

    return calls, assessment


def test_analyze_calls_all_interpretation_components(monkeypatch):
    features = make_features()
    signals = make_signals()

    interpretations = make_interpretations()
    calls: dict[str, object] = {}

    calls, assessment = _patch_interpretation_components(
        monkeypatch,
        interpretations,
        calls,
    )

    result = EconomicInterpretationService.analyze(
        features,
        signals,
        indicator_code="GDP",
        region_code="DE",
    )

    latest = features.iloc[-1]
    latest_signals = signals.iloc[-1]

    assert set(
        [
            "growth",
            "trend",
            "momentum",
            "volatility",
            "position",
            "transition",
            "regime",
            "assessment",
        ]
    ) == set(calls)

    for name in (
        "growth",
        "trend",
        "momentum",
        "volatility",
        "position",
    ):
        received_latest, received_signals = calls[name]
        pd.testing.assert_series_equal(
            received_latest,
            latest,
        )
        pd.testing.assert_series_equal(
            received_signals,
            latest_signals,
        )

    assert calls["transition"] == {
        "growth": interpretations["growth"],
        "trend": interpretations["trend"],
        "momentum": interpretations["momentum"],
        "volatility": interpretations["volatility"],
        "position": interpretations["position"],
    }

    assert calls["regime"] == {
        "growth": interpretations["growth"],
        "trend": interpretations["trend"],
        "momentum": interpretations["momentum"],
        "volatility": interpretations["volatility"],
        "position": interpretations["position"],
        "transition": interpretations["transition"],
    }

    assert calls["assessment"] == {
        "growth": interpretations["growth"],
        "trend": interpretations["trend"],
        "momentum": interpretations["momentum"],
        "volatility": interpretations["volatility"],
        "position": interpretations["position"],
        "transition": interpretations["transition"],
        "regime": "expansion",
    }

    assert result["assessment"] == assessment


def test_analyze_returns_complete_output_structure(monkeypatch):
    features = make_features()
    signals = make_signals()

    interpretations = make_interpretations()

    _patch_interpretation_components(
        monkeypatch,
        interpretations,
    )

    result = EconomicInterpretationService.analyze(
        features,
        signals,
        indicator_code="GDP",
        region_code="DE",
    )

    assert set(result) == {
        "indicator",
        "region",
        "date",
        "regime",
        "growth",
        "trend",
        "momentum",
        "volatility",
        "position",
        "transition",
        "assessment",
        "history",
        "current",
        "signals",
    }

    assert result["indicator"] == "GDP"
    assert result["region"] == "DE"
    assert result["regime"] == "expansion"
    assert result["growth"] == interpretations["growth"]
    assert result["trend"] == interpretations["trend"]
    assert result["momentum"] == interpretations["momentum"]
    assert result["volatility"] == interpretations["volatility"]
    assert result["position"] == interpretations["position"]
    assert result["transition"] == interpretations["transition"]


def test_analyze_preserves_history_metadata(monkeypatch):
    features = make_features(rows=3)
    signals = make_signals(rows=3)

    interpretations = make_interpretations()

    _patch_interpretation_components(
        monkeypatch,
        interpretations,
    )

    result = EconomicInterpretationService.analyze(
        features,
        signals,
    )

    assert result["history"]["observations"] == 3
    assert result["history"]["start"] == "2024-01-01T00:00:00"
    assert result["history"]["end"] == "2024-03-01T00:00:00"

    assert result["date"] == "2024-03-01T00:00:00"


def test_analyze_uses_latest_feature_row_for_current_values(monkeypatch):
    features = make_features(rows=2)
    signals = make_signals(rows=2)

    interpretations = make_interpretations()

    _patch_interpretation_components(
        monkeypatch,
        interpretations,
    )

    result = EconomicInterpretationService.analyze(
        features,
        signals,
    )

    for column in REQUIRED_FEATURES:
        assert result["current"][column] == features.iloc[-1][column]

    for column in REQUIRED_FEATURES:
        assert result["current"][column] != features.iloc[0][column]


def test_analyze_serializes_signal_values_as_booleans(monkeypatch):
    features = make_features()
    signals = make_signals()

    # Convert to object so the test can explicitly verify bool(...)
    # without relying on pandas boolean dtype coercion.
    signals = signals.astype(object)

    for column in REQUIRED_SIGNALS:
        signals.loc[signals.index[-1], column] = 1

    interpretations = make_interpretations()

    _patch_interpretation_components(
        monkeypatch,
        interpretations,
    )

    result = EconomicInterpretationService.analyze(
        features,
        signals,
    )

    for column in REQUIRED_SIGNALS:
        assert result["signals"][column] is True


def test_analyze_allows_missing_optional_metadata(monkeypatch):
    features = make_features()
    signals = make_signals()

    interpretations = make_interpretations()

    _patch_interpretation_components(
        monkeypatch,
        interpretations,
    )

    result = EconomicInterpretationService.analyze(
        features,
        signals,
    )

    assert result["indicator"] is None
    assert result["region"] is None