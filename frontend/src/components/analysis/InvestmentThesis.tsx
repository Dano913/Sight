import type { InvestmentAnalysisResult } from "../../pages/indicators/types";

interface Props {
  analysis: InvestmentAnalysisResult | null;
  loading?: boolean;
}

function label(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function stateClass(value: string) {
  if (
    ["supportive", "constructive", "low", "moderate", "improving"].includes(value)
  ) {
    return "text-emerald-400";
  }

  if (
    ["defensive", "cautious", "high", "extreme", "very_low", "deteriorating"].includes(value)
  ) {
    return "text-red-400";
  }

  return "text-slate-300";
}

export default function InvestmentThesis({
  analysis,
  loading = false,
}: Props) {
  if (loading) {
    return (
      <section className="rounded-xl border border-slate-700 bg-[#1b2a39] p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 w-48 rounded bg-slate-700" />
          <div className="h-4 w-3/4 rounded bg-slate-700" />
          <div className="h-20 rounded bg-slate-700" />
        </div>
      </section>
    );
  }

  if (!analysis) {
    return null;
  }

  const { overall, environment, risk, opportunity } = analysis;

  return (
    <section className="rounded-xl border border-slate-700 bg-[#1b2a39] p-6 text-slate-100">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-400">
            Investment Thesis
          </p>

          <h2 className="mt-1 text-2xl font-semibold">
            {label(overall.macro_bias || overall.assessment)}
          </h2>
        </div>

        <div className="text-right">
          <p className="text-xs text-slate-400">Conviction</p>
          <p
            className={`text-lg font-semibold ${stateClass(
              overall.conviction,
            )}`}
          >
            {label(overall.conviction)}
          </p>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4">
        <Metric
          title="Environment"
          value={environment.state}
        />

        <Metric
          title="Risk"
          value={risk.state}
        />

        <Metric
          title="Opportunity"
          value={opportunity.state}
        />

        <Metric
          title="Direction"
          value={overall.direction || "neutral"}
        />
      </div>

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <Horizon
          title="Short term"
          value={analysis.horizon.short_term}
        />

        <Horizon
          title="Medium term"
          value={analysis.horizon.medium_term}
        />

        <Horizon
          title="Long term"
          value={analysis.horizon.long_term}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <h3 className="mb-3 text-sm font-semibold text-slate-300">
            Key factors
          </h3>

          <ul className="space-y-2 text-sm text-slate-400">
            {overall.environment && (
              <li>
                Environment:{" "}
                <span className="text-slate-200">
                  {label(overall.environment)}
                </span>
              </li>
            )}

            {overall.risk && (
              <li>
                Risk:{" "}
                <span className="text-slate-200">
                  {label(overall.risk)}
                </span>
              </li>
            )}

            {overall.opportunity && (
              <li>
                Opportunity:{" "}
                <span className="text-slate-200">
                  {label(overall.opportunity)}
                </span>
              </li>
            )}

            {overall.confidence && (
              <li>
                Confidence:{" "}
                <span className="text-slate-200">
                  {label(overall.confidence)}
                </span>
              </li>
            )}
          </ul>
        </div>

        <div>
          <h3 className="mb-3 text-sm font-semibold text-slate-300">
            Alerts
          </h3>

          {analysis.alerts.length === 0 ? (
            <p className="text-sm text-slate-500">
              No significant alerts.
            </p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {analysis.alerts.map((alert) => (
                <span
                  key={alert}
                  className="rounded-md border border-slate-600 px-2 py-1 text-xs text-slate-300"
                >
                  {label(alert)}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function Metric({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-lg bg-[#223548] p-4">
      <p className="text-xs text-slate-400">{title}</p>
      <p
        className={`mt-1 font-semibold ${stateClass(value)}`}
      >
        {label(value)}
      </p>
    </div>
  );
}

function Horizon({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-slate-700 p-4">
      <p className="text-xs text-slate-400">{title}</p>
      <p className="mt-1 font-medium text-slate-200">
        {label(value)}
      </p>
    </div>
  );
}