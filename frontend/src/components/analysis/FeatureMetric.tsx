interface FeatureMetricProps {
  label: string;
  value: number | null | undefined;
  featureKey: string;
}

export function FeatureMetric({
  label,
  value,
  featureKey,
}: FeatureMetricProps) {
  const formattedValue = formatFeatureValue(value, featureKey);

  return (
    <div className="px-5 py-4">
      <p className="text-xs text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-lg font-medium text-white">
        {formattedValue}
      </p>
    </div>
  );
}

function formatFeatureValue(
  value: number | null | undefined,
  featureKey: string,
): string {
  if (value === null || value === undefined) {
    return "—";
  }

  if (
    featureKey.includes("percentage") ||
    featureKey.includes("growth") ||
    featureKey === "drawdown" ||
    featureKey === "rolling_volatility" ||
    featureKey === "distance_from_rolling_mean" ||
    featureKey === "distance_from_max" ||
    featureKey === "distance_from_min" ||
    featureKey === "trend_change" ||
    featureKey === "volatility_change"
  ) {
    return `${(value * 100).toFixed(2)}%`;
  }

  if (
    featureKey.includes("zscore") ||
    featureKey === "zscore" ||
    featureKey === "percentile" ||
    featureKey === "rolling_percentile"
  ) {
    if (
      featureKey === "percentile" ||
      featureKey === "rolling_percentile"
    ) {
      return `${(value * 100).toFixed(1)}%`;
    }

    return value.toFixed(2);
  }

  return new Intl.NumberFormat("es-ES", {
    maximumFractionDigits: 2,
  }).format(value);
}