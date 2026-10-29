from __future__ import annotations
from unittest import result

import pandas as pd

from app.services.features.feature_engine import FeatureEngine


class TestStableScenario:

    def test_stable_series(self):
        series = pd.Series(
            [100.0] * 30
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        # El nivel permanece constante.
        assert (result["value"] == 100.0).all()

        # No existe crecimiento.
        assert result["percentage_change"].dropna().eq(0.0).all()
        assert result["log_difference"].dropna().eq(0.0).all()

        # No existe momentum.
        assert result["momentum"].dropna().eq(0.0).all()

        # No existe aceleración.
        assert result["acceleration"].dropna().eq(0.0).all()
        # No existe volatilidad.
        assert result["rolling_std"].dropna().eq(0.0).all()
        assert result["rolling_volatility"].dropna().eq(0.0).all()

        # El valor coincide siempre con el máximo y mínimo.
        assert result["distance_from_max"].dropna().eq(0.0).all()
        assert result["distance_from_min"].dropna().eq(0.0).all()

        # Nunca existe drawdown.
        assert result["drawdown"].eq(0.0).all()

    def test_constant_growth(self):
        series = pd.Series(
            [100.0, 110.0, 120.0, 130.0, 140.0, 150.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["percentage_change"].dropna().gt(0).all()
        assert result["acceleration"].dropna().eq(0.0).all()

        assert result["rolling_slope_short"].dropna().gt(0).all()
        assert result["rolling_slope_medium"].dropna().gt(0).all()
        assert result["rolling_slope_long"].dropna().gt(0).all()

        assert result["drawdown"].eq(0.0).all()

    def test_acceleration(self):
        series = pd.Series(
            [100.0, 102.0, 106.0, 112.0, 120.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        assert result["percentage_change"].dropna().gt(0).all()
        assert result["acceleration"].dropna().gt(0).all()

        assert result["rolling_slope_short"].dropna().gt(0).all()
        assert result["rolling_slope_medium"].dropna().gt(0).all()
        assert result["rolling_slope_long"].dropna().gt(0).all()

        assert result["drawdown"].eq(0.0).all()

    def test_deceleration(self):
        series = pd.Series(
            [100.0, 110.0, 118.0, 124.0, 128.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # Sigue creciendo.
        assert result["percentage_change"].dropna().gt(0).all()

        # Pero el crecimiento se está desacelerando.
        assert result["acceleration"].dropna().lt(0).all()

        # La tendencia sigue siendo alcista.
        assert result["rolling_slope_short"].dropna().gt(0).all()
        assert result["rolling_slope_medium"].dropna().gt(0).all()
        assert result["rolling_slope_long"].dropna().gt(0).all()


    def test_negative_growth(self):
        series = pd.Series(
            [150.0, 140.0, 130.0, 120.0, 110.0, 100.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # El indicador está cayendo.
        assert result["percentage_change"].dropna().lt(0).all()

        # La tendencia es bajista.
        assert result["rolling_slope_short"].dropna().lt(0).all()
        assert result["rolling_slope_medium"].dropna().lt(0).all()
        assert result["rolling_slope_long"].dropna().lt(0).all()

        # Al caer desde el máximo inicial, aparece drawdown negativo.
        assert result["drawdown"].iloc[1:].lt(0).all()

    def test_shock(self):
        series = pd.Series(
            [100.0, 102.0, 101.0, 70.0, 72.0, 75.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
            extreme_window=3,
        )

        # El shock provoca una caída fuerte.
        assert result["percentage_change"].iloc[3] < 0
        assert result["percentage_change"].iloc[3] < -0.20

        # La aceleración se vuelve negativa durante el shock.
        assert result["acceleration"].iloc[3] < 0

        # Aparece un drawdown importante.
        assert result["drawdown"].iloc[3] < -0.20

        # El valor queda por debajo de su máximo histórico.
        assert result["distance_from_max"].iloc[3] < -0.20


    def test_recovery(self):
        series = pd.Series(
            [100.0, 95.0, 90.0, 85.0, 90.0, 96.0, 103.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # Primero hay caída y posteriormente recuperación.
        assert result["percentage_change"].iloc[3] < 0
        assert result["percentage_change"].iloc[4:].gt(0).all()

        # El valor empieza a recuperar desde el mínimo.
        assert result["drawdown"].iloc[4] > result["drawdown"].iloc[3]
        assert result["drawdown"].iloc[5] > result["drawdown"].iloc[4]
        assert result["drawdown"].iloc[6] > result["drawdown"].iloc[5]

        # La pendiente de corto plazo termina siendo positiva.
        assert result["rolling_slope_short"].iloc[-1] > 0


    def test_high_volatility(self):
        series = pd.Series(
            [100.0, 120.0, 80.0, 125.0, 75.0, 130.0, 70.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            level_window=3,
            volatility_window=3,
        )

        # La serie presenta movimientos porcentuales muy grandes.
        assert result["rolling_volatility"].dropna().gt(0).all()

        # La variabilidad de los niveles es elevada.
        assert result["rolling_std"].dropna().gt(0).all()

        # Existe una amplitud importante entre máximos y mínimos.
        assert result["rolling_range"].dropna().gt(20).all()

        # La volatilidad está presente de forma clara al final.
        assert result["rolling_volatility"].iloc[-1] > 0

    def test_trend_reversal(self):
        series = pd.Series(
            [150.0, 140.0, 130.0, 120.0, 125.0, 135.0, 145.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # Antes del giro, la tendencia es bajista.
        assert result["rolling_slope_short"].iloc[3] < 0

        # Después del giro, la pendiente de corto plazo se vuelve positiva.
        assert result["rolling_slope_short"].iloc[-1] > 0

        # La aceleración refleja el cambio de dinámica.
        assert result["acceleration"].iloc[4] > 0

        # La pendiente de corto plazo mejora respecto a la anterior.
        assert result["slope_change"].iloc[-1] > 0

        # El cambio de tendencia debe ser positivo.
        assert result["trend_change"].iloc[-1] > 0

    def test_growth_with_increasing_volatility(self):
        series = pd.Series(
            [100.0, 102.0, 105.0, 110.0, 108.0, 118.0, 115.0, 130.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            level_window=3,
            volatility_window=3,
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # El indicador mantiene una tendencia general de crecimiento.
        assert result["percentage_change"].iloc[1:].gt(0).sum() >= 4

        # La tendencia de corto plazo termina siendo alcista.
        assert result["rolling_slope_short"].iloc[-1] > 0

        # Existe volatilidad.
        assert result["rolling_volatility"].dropna().gt(0).all()

        # La variabilidad de los niveles es positiva.
        assert result["rolling_std"].dropna().gt(0).all()

        # La volatilidad final es elevada respecto al inicio de la
        # ventana disponible.
        volatility = result["rolling_volatility"].dropna()

        assert volatility.iloc[-1] > volatility.iloc[0]

    def test_negative_growth_with_recovery(self):
        series = pd.Series(
            [150.0, 140.0, 130.0, 120.0, 110.0, 115.0, 125.0, 140.0]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # Primero existe crecimiento negativo.
        assert result["percentage_change"].iloc[1:5].lt(0).all()

        # Posteriormente comienza la recuperación.
        assert result["percentage_change"].iloc[5:].gt(0).all()

        # El drawdown mejora durante la recuperación.
        assert result["drawdown"].iloc[5] > result["drawdown"].iloc[4]
        assert result["drawdown"].iloc[6] > result["drawdown"].iloc[5]
        assert result["drawdown"].iloc[7] > result["drawdown"].iloc[6]

        # La tendencia de corto plazo termina siendo alcista.
        assert result["rolling_slope_short"].iloc[-1] > 0

        # La pendiente mejora durante el cambio de régimen.
        assert result["slope_change"].iloc[-1] > 0

    def test_shock_and_recovery(self):
        series = pd.Series(
            [
                100.0,
                101.0,
                100.0,
                98.0,
                60.0,
                65.0,
                72.0,
                82.0,
                95.0,
            ]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            extreme_window=3,
            volatility_window=3,
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # El shock provoca una caída muy fuerte.
        assert result["percentage_change"].iloc[4] < -0.20

        # El shock genera un drawdown importante.
        assert result["drawdown"].iloc[4] < -0.20

        # El valor queda muy por debajo del máximo reciente.
        assert result["distance_from_max"].iloc[4] < -0.20

        # Durante la recuperación el drawdown mejora.
        assert result["drawdown"].iloc[-1] > result["drawdown"].iloc[4]

        # La dinámica termina siendo positiva durante la recuperación.
        assert result["momentum"].iloc[-1] > 0

        # La tendencia de corto plazo termina siendo alcista.
        assert result["rolling_slope_short"].iloc[-1] > 0

        # El cambio de tendencia termina siendo positivo.
        assert result["trend_change"].iloc[-1] > 0

    def test_boom_and_bust(self):
        series = pd.Series(
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
            ]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            extreme_window=3,
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # Durante el boom existe crecimiento positivo.
        assert result["percentage_change"].iloc[1:5].gt(0).all()

        # El indicador alcanza un máximo.
        assert result["value"].iloc[4] == result["value"].max()

        # Posteriormente comienza una caída fuerte.
        assert result["percentage_change"].iloc[5:].lt(0).all()

        # Aparece un drawdown importante después del máximo.
        assert result["drawdown"].iloc[-1] < -0.40

        # La distancia respecto al máximo también es muy negativa.
        assert result["distance_from_max"].iloc[-1] < 0

        # La tendencia de corto plazo termina siendo bajista.
        assert result["rolling_slope_short"].iloc[-1] < 0

    def test_stable_high_level(self):
        series = pd.Series(
            [200.0] * 20
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        # El indicador se encuentra en un nivel elevado.
        assert result["value"].iloc[-1] == 200.0

        # Pero no existe crecimiento.
        assert result["percentage_change"].dropna().eq(0.0).all()
        assert result["log_difference"].dropna().eq(0.0).all()

        # Tampoco existe tendencia.
        assert result["rolling_slope_short"].dropna().abs().lt(1e-10).all()

        # Ni volatilidad.
        assert result["rolling_std"].dropna().eq(0.0).all()

        # Ni drawdown.
        assert result["drawdown"].eq(0.0).all()

    def test_stable_low_level(self):
        series = pd.Series(
            [20.0] * 20
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
        )

        # El indicador se encuentra en un nivel bajo.
        assert result["value"].iloc[-1] == 20.0

        # Pero no existe crecimiento.
        assert result["percentage_change"].dropna().eq(0.0).all()
        assert result["log_difference"].dropna().eq(0.0).all()

        # Tampoco existe tendencia.
        assert result["rolling_slope_short"].dropna().abs().lt(1e-10).all()

        # Ni volatilidad.
        assert result["rolling_std"].dropna().eq(0.0).all()

        # Ni drawdown.
        assert result["drawdown"].eq(0.0).all()