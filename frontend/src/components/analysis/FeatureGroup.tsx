import { FeatureMetric } from "./FeatureMetric";
import type { FeatureAnalysisResult, FeatureKey } from "../../pages/indicators/types.ts";

interface FeatureGroupProps {
  title: string;
  features: [FeatureKey, string][];
  data: FeatureAnalysisResult;
}

export function FeatureGroup({
  title,
  features,
  data,
}: FeatureGroupProps) {
  const latest = data.observations[data.observations.length - 1];

  if (!latest) {
    return null;
  }

  return (
    <section className="rounded-xl border border-slate-700 bg-[#182b3a]">
      <header className="border-b border-slate-700 px-5 py-4">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-200">
          {title}
        </h3>

        <p className="mt-1 text-xs text-slate-500">
          {latest.date}
        </p>
      </header>

      <div className="grid grid-cols-1 divide-y divide-slate-700 sm:grid-cols-2 lg:grid-cols-3">
        {features.map(([key, label]) => (
          <FeatureMetric
            key={key}
            label={label}
            value={latest.features[key]}
            featureKey={key}
          />
        ))}
      </div>
    </section>
  );
}