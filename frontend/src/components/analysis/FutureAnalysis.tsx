import type { FeatureAnalysisResult } from "../../pages/indicators/types";
import { FeatureGroup } from "./FeatureGroup";

interface FeatureAnalysisProps {
  data: FeatureAnalysisResult;
}

export function FeatureAnalysis({ data }: FeatureAnalysisProps) {
  return (
    <section className="mt-8 space-y-6">
      <header>
        <h2 className="text-xl font-semibold text-white">
          Feature Analysis
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Evolución y comportamiento estadístico del indicador.
        </p>
      </header>

      <FeatureGroup
        title="Valor"
        features={[
          ["value", "Valor"],
        ]}
        data={data}
      />

      <FeatureGroup
        title="Crecimiento"
        features={[
          ["percentage_change", "Cambio porcentual"],
          ["log_difference", "Diferencia logarítmica"],
          ["yoy_growth", "Crecimiento interanual"],
          ["yoy_log_growth", "Crecimiento logarítmico interanual"],
          ["cumulative_growth", "Crecimiento acumulado"],
          ["momentum", "Momentum"],
        ]}
        data={data}
      />

      <FeatureGroup
        title="Tendencia"
        features={[
          ["rolling_slope_short", "Pendiente corta"],
          ["rolling_slope_medium", "Pendiente media"],
          ["rolling_slope_long", "Pendiente larga"],
          ["acceleration", "Aceleración"],
          ["slope_change", "Cambio de pendiente"],
          ["trend_change", "Cambio de tendencia"],
        ]}
        data={data}
      />

      <FeatureGroup
        title="Volatilidad"
        features={[
          ["rolling_std", "Desviación estándar"],
          ["rolling_volatility", "Volatilidad"],
          ["rolling_range", "Rango"],
          ["volatility_change", "Cambio de volatilidad"],
          ["volatility_zscore", "Z-score de volatilidad"],
        ]}
        data={data}
      />

      <FeatureGroup
        title="Distribución"
        features={[
          ["zscore", "Z-score"],
          ["percentile", "Percentil"],
          ["rolling_zscore", "Z-score rolling"],
          ["rolling_percentile", "Percentil rolling"],
        ]}
        data={data}
      />

      <FeatureGroup
        title="Posición relativa"
        features={[
          ["rolling_mean", "Media rolling"],
          ["rolling_median", "Mediana rolling"],
          ["rolling_min", "Mínimo rolling"],
          ["rolling_max", "Máximo rolling"],
          ["distance_from_rolling_mean", "Distancia de la media"],
          ["distance_from_max", "Distancia del máximo"],
          ["distance_from_min", "Distancia del mínimo"],
          ["drawdown", "Drawdown"],
        ]}
        data={data}
      />
    </section>
  );
}