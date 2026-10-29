import type { AssetScore } from "../../pages/indicators/types";

interface Props {
  assets: AssetScore[];
  loading?: boolean;
}

function label(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function scoreClass(score: number) {
  if (score > 0) {
    return "text-emerald-400";
  }

  if (score < 0) {
    return "text-red-400";
  }

  return "text-slate-300";
}

function contributionClass(value: number) {
  if (value > 0) {
    return "text-emerald-400";
  }

  if (value < 0) {
    return "text-red-400";
  }

  return "text-slate-500";
}

export default function AssetRanking({
  assets,
  loading = false,
}: Props) {
  if (loading) {
    return (
      <section className="rounded-xl border border-slate-700 bg-[#1b2a39] p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 w-48 rounded bg-slate-700" />

          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((item) => (
              <div
                key={item}
                className="h-12 rounded-lg bg-slate-700"
              />
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (assets.length === 0) {
    return null;
  }

  return (
    <section className="rounded-xl border border-slate-700 bg-[#1b2a39] p-6 text-slate-100">
      <div className="mb-6">
        <p className="text-xs uppercase tracking-wider text-slate-400">
          Investment
        </p>

        <h2 className="mt-1 text-2xl font-semibold">
          Asset Ranking
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Relative attractiveness based on the current macroeconomic
          environment.
        </p>
      </div>

      <div className="space-y-2">
        {assets.map((asset, index) => (
          <div
            key={asset.asset}
            className="rounded-lg border border-slate-700 bg-[#223548] px-4 py-3"
          >
            <div className="flex items-center gap-4">
              <div className="w-8 shrink-0 text-sm font-medium text-slate-500">
                {index + 1}
              </div>

              <div className="min-w-0 flex-1">
                <p className="font-medium text-slate-100">
                  {label(asset.asset)}
                </p>

                <p className="text-xs text-slate-500">
                  {label(asset.asset_class)} · {label(asset.asset_type)}
                </p>
              </div>

              <div
                className={`text-lg font-semibold ${scoreClass(
                  asset.score,
                )}`}
              >
                {asset.score > 0 ? "+" : ""}
                {asset.score.toFixed(2)}
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 border-t border-slate-700 pt-3">
              {Object.entries(asset.contributions)
                .filter(([, value]) => value !== 0)
                .map(([factor, value]) => (
                  <span
                    key={factor}
                    className="text-xs text-slate-400"
                  >
                    {label(factor)}{" "}
                    <span
                      className={contributionClass(value)}
                    >
                      {value > 0 ? "+" : ""}
                      {value.toFixed(2)}
                    </span>
                  </span>
                ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}