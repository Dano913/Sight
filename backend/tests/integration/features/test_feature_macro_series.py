from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.features.feature_engine import FeatureEngine


class TestMacroFeatureSeries:
    """
    Comprueba el comportamiento del FeatureEngine sobre
    series ficticias con características similares a
    indicadores macroeconómicos reales.
    """

    def test_gdp_series(self):
        """
        PIB ficticio con crecimiento estable y posteriormente acelerado.
        """

        series = pd.Series(
            [
                100.0,
                100.5,
                101.0,
                101.5,
                102.0,
                102.8,
                103.8,
                105.0,
                106.5,
                108.2,
            ]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # El PIB crece durante toda la serie.
        assert result["percentage_change"].dropna().gt(0).all()

        # La tendencia es alcista.
        assert result["rolling_slope_short"].dropna().gt(0).all()
        assert result["rolling_slope_medium"].dropna().gt(0).all()
        assert result["rolling_slope_long"].dropna().gt(0).all()

        # El valor acumulado aumenta.
        assert result["cumulative_growth"].iloc[-1] > 0

        # La serie no presenta drawdown al ser siempre creciente.
        assert np.allclose(
            result["drawdown"].dropna(),
            0,
        )

        # La aceleración al final es positiva:
        # el crecimiento se está intensificando.
        assert result["acceleration"].iloc[-1] > 0

    def test_inflation_series(self):
        """
        Inflación ficticia con una fase estable y posteriormente
        una aceleración inflacionaria.
        """

        series = pd.Series(
            [
                2.0,
                2.1,
                2.0,
                2.1,
                2.2,
                2.4,
                2.8,
                3.3,
                4.0,
                4.8,
            ]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # El nivel de inflación aumenta en la segunda mitad.
        assert result["value"].iloc[-1] > result["value"].iloc[4]

        # La tendencia final es claramente alcista.
        assert result["rolling_slope_short"].iloc[-1] > 0
        assert result["rolling_slope_medium"].iloc[-1] > 0

        # La inflación termina en un nivel superior al inicial.
        assert result["cumulative_growth"].iloc[-1] > 0

        # El crecimiento del propio indicador se intensifica.
        assert result["acceleration"].iloc[-1] > 0

        # El valor final está por encima de su media reciente.
        assert (
            result["distance_from_rolling_mean"].iloc[-1] > 0
        )

    def test_unemployment_series(self):
        """
        Desempleo ficticio que aumenta inicialmente y posteriormente
        comienza una recuperación.
        """

        series = pd.Series(
            [
                7.0,
                7.3,
                7.6,
                8.0,
                8.2,
                8.0,
                7.6,
                7.1,
                6.7,
                6.3,
            ]
        )

        result = FeatureEngine.compute(
            series=series,
            frequency="annual",
            trend_short_window=3,
            trend_medium_window=4,
            trend_long_window=5,
        )

        # El desempleo alcanza un máximo intermedio.
        assert result["value"].iloc[4] == 8.2

        # Posteriormente comienza a caer.
        assert (
            result["percentage_change"].iloc[-1] < 0
        )

        # La tendencia de corto plazo termina siendo bajista.
        assert (
            result["rolling_slope_short"].iloc[-1] < 0
        )

        # El desempleo final está por debajo de su máximo.
        assert (
            result["drawdown"].iloc[-1] < 0
        )

        # La distancia respecto al máximo reciente es negativa.
        assert (
            result["distance_from_max"].iloc[-1] < 0
        )

        # El indicador se encuentra en recuperación respecto
        # al máximo alcanzado.
        assert (
            result["value"].iloc[-1]
            < result["value"].iloc[4]
        )