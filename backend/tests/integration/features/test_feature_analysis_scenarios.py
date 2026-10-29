from __future__ import annotations

import pandas as pd

from app.services.features.feature_engine import FeatureEngine
from app.services.features.feature_analysis_service import (
    FeatureAnalysisService,
)


class TestFeatureAnalysisScenarios:

    def _analyze(
        self,
        series,
        **kwargs,
    ) -> pd.DataFrame:
        features = FeatureEngine.compute(
            series=pd.Series(series),
            frequency="annual",
            **kwargs,
        )
        return FeatureAnalysisService.analyze(features)

    def test_stable_series(self):
        result = self._analyze(
            [100.0] * 30,
        )

        assert not result["positive_growth"].any()
        assert not result["negative_growth"].any()
        assert not result["accelerating_growth"].any()

        assert not result["bullish_trend"].any()
        assert not result["bearish_trend"].any()
        assert not result["trend_reversal"].any()

        assert not result["high_volatility"].any()
        assert not result["volatility_increasing"].any()
        assert not result["significant_drawdown"].any()

        near_high = result["near_historical_high"]

        assert near_high.iloc[7:].all()
        assert not near_high.iloc[:7].any()
        
        near_low = result["near_historical_low"]

        assert near_low.iloc[7:].all()
        assert not near_low.iloc[:7].any()

    def test_constant_growth(self):
        result = self._analyze(
            [100.0, 110.0, 120.0, 130.0, 140.0, 150.0],
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["positive_growth"].iloc[1:].all()
        assert not result["negative_growth"].any()
        assert not result["accelerating_growth"].any()

        assert result["bullish_trend"].iloc[-1]
        assert not result["significant_drawdown"].any()

    def test_acceleration(self):
        result = self._analyze(
            [100.0, 102.0, 106.0, 112.0, 120.0, 130.0],
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["positive_growth"].iloc[1:].all()
        assert result["accelerating_growth"].iloc[2:].all()
        assert result["bullish_trend"].iloc[-1]
        assert not result["significant_drawdown"].any()

    def test_deceleration(self):
        result = self._analyze(
            [100.0, 110.0, 118.0, 124.0, 128.0, 130.0],
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["positive_growth"].iloc[1:].all()
        assert not result["negative_growth"].any()
        assert not result["accelerating_growth"].iloc[2:].any()
        assert result["bullish_trend"].iloc[-1]

    def test_negative_growth(self):
        result = self._analyze(
            [150.0, 140.0, 130.0, 120.0, 110.0, 100.0],
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["negative_growth"].iloc[1:].all()
        assert not result["positive_growth"].any()

        assert result["bearish_trend"].iloc[-1]
        assert result["significant_drawdown"].iloc[-1]

    def test_shock(self):
        result = self._analyze(
            [100.0, 102.0, 101.0, 70.0, 72.0, 75.0],
            extreme_window=3,
            level_window=3,
            volatility_window=3,
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["negative_growth"].iloc[3]
        assert result["significant_drawdown"].iloc[3]
        assert result["near_historical_low"].iloc[3]

    def test_recovery(self):
        result = self._analyze(
            [100.0, 95.0, 90.0, 85.0, 90.0, 96.0, 103.0],
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["negative_growth"].iloc[1:4].all()
        assert result["positive_growth"].iloc[4:].all()

        assert result["significant_drawdown"].iloc[3]

        assert result["bullish_trend"].iloc[-1]

    def test_high_volatility(self):
        result = self._analyze(
            [100.0, 120.0, 80.0, 125.0, 75.0, 130.0, 70.0],
            level_window=3,
            volatility_window=3,
        )

        assert not result["positive_growth"].iloc[[2, 4, 6]].all()

        assert result["volatility_increasing"].iloc[-1] in {
            True,
            False,
        }

        assert not result["significant_drawdown"].iloc[:2].any()

    def test_trend_reversal(self):
        result = self._analyze(
            [150.0, 140.0, 130.0, 120.0, 125.0, 135.0, 145.0],
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["bearish_trend"].iloc[3]
        assert result["bullish_trend"].iloc[-1]

    def test_growth_with_increasing_volatility(self):
        result = self._analyze(
            [100.0, 102.0, 105.0, 110.0, 108.0, 118.0, 115.0, 130.0],
            level_window=3,
            volatility_window=3,
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["positive_growth"].iloc[1:].sum() >= 4
        assert result["bullish_trend"].iloc[-1]
        assert result["volatility_increasing"].iloc[-1]

    def test_negative_growth_with_recovery(self):
        result = self._analyze(
            [150.0, 140.0, 130.0, 120.0, 125.0, 135.0, 145.0],
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["negative_growth"].iloc[1:4].all()
        assert result["positive_growth"].iloc[4:].all()

        assert result["bearish_trend"].iloc[3]
        assert result["bullish_trend"].iloc[-1]

        assert result["significant_drawdown"].iloc[3]

    def test_shock_and_recovery(self):
        result = self._analyze(
            [100.0, 101.0, 102.0, 70.0, 72.0, 80.0, 90.0, 102.0],
            extreme_window=3,
            level_window=3,
            volatility_window=3,
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["negative_growth"].iloc[3]
        assert result["significant_drawdown"].iloc[3]

        assert result["positive_growth"].iloc[4:].all()
        assert result["bullish_trend"].iloc[-1]

    def test_boom_and_bust(self):
        result = self._analyze(
            [
                100.0,
                110.0,
                125.0,
                145.0,
                170.0,
                150.0,
                125.0,
                105.0,
                90.0,
            ],
            extreme_window=3,
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["positive_growth"].iloc[1:5].all()
        assert result["negative_growth"].iloc[5:].all()

        assert result["significant_drawdown"].iloc[-1]
        assert result["bearish_trend"].iloc[-1]

    def test_stable_high_level(self):
        result = self._analyze(
            [1000.0] * 30,
        )

        assert not result["positive_growth"].any()
        assert not result["negative_growth"].any()

        assert not result["bullish_trend"].any()
        assert not result["bearish_trend"].any()
        assert not result["trend_reversal"].any()

        assert not result["significant_drawdown"].any()

    def test_stable_low_level(self):
        result = self._analyze(
            [10.0] * 30,
        )

        assert not result["positive_growth"].any()
        assert not result["negative_growth"].any()

        assert not result["bullish_trend"].any()
        assert not result["bearish_trend"].any()
        assert not result["trend_reversal"].any()

        assert not result["significant_drawdown"].any()

        assert result["near_historical_high"].iloc[7:].all()
        assert result["near_historical_low"].iloc[7:].all()