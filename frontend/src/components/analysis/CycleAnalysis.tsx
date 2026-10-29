import type { CycleAnalysisResult } from "../../pages/indicators/types";

interface Props {
  analysis: CycleAnalysisResult | null;
  loading: boolean;
}

export default function CycleAnalysis({
  analysis,
  loading,
}: Props) {

  if (loading) {
    return (
      <section className="mt-8 rounded-xl border border-[#32485f] bg-[#223548] p-6 text-white">
        <h2 className="mb-4 text-lg font-semibold">
          Cycle Analysis
        </h2>

        <div className="text-sm text-slate-400">
          Calculando ciclos...
        </div>
      </section>
    );
  }

  if (!analysis) {
    return (
      <section className="mt-8 rounded-xl border border-[#32485f] bg-[#223548] p-6 text-white">
        <h2 className="mb-4 text-lg font-semibold">
          Cycle Analysis
        </h2>

        <div className="text-sm text-slate-400">
          No hay análisis disponible.
        </div>
      </section>
    );
  }

  const cycles = analysis.robust_cycles ?? [];

  return (
    <section className="mt-8 rounded-xl border border-[#32485f] bg-[#223548] p-6 text-white">

      {/* HEADER */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">
            Cycle Analysis
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            {analysis.start_date} → {analysis.end_date}
          </p>
        </div>

        <div className="text-right">
          <div className="text-sm text-slate-400">
            Observations
          </div>

          <div className="text-xl font-semibold">
            {analysis.observations}
          </div>
        </div>
      </div>


      {/* CYCLES */}
      <div>
        <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
          Detected cycles
        </h3>

        {cycles.length === 0 ? (
          <div className="rounded-lg border border-[#32485f] p-4 text-sm text-slate-400">
            No robust cycles detected.
          </div>
        ) : (

          <div className="space-y-3">

            {cycles.map((cycle, index) => (

              <div
                key={`${cycle.period_years}-${index}`}
                className="rounded-lg border border-[#32485f] bg-[#1b2a39] p-4"
              >

                <div className="flex items-center justify-between">

                  {/* PERIOD */}
                  <div>
                    <div className="text-2xl font-semibold">
                      {cycle.period_years.toFixed(1)}
                      <span className="ml-1 text-sm font-normal text-slate-400">
                        years
                      </span>
                    </div>

                    <div className="mt-1 text-xs text-slate-500">
                      ~ {cycle.cycles_observable.toFixed(1)} observable cycles
                    </div>
                  </div>


                  {/* CONFIDENCE */}
                  <div className="text-right">

                    <div className="text-sm font-semibold">
                      {cycle.confidence}
                    </div>

                    <div className="text-xs text-slate-400">
                      Score {cycle.score.toFixed(2)}
                    </div>

                  </div>

                </div>


                {/* METHODS */}
                <div className="mt-4 flex flex-wrap gap-2">

                  {cycle.methods.map((method) => (
                    <span
                      key={method}
                      className="rounded-md border border-[#32485f] px-2 py-1 text-xs text-slate-300"
                    >
                      {method}
                    </span>
                  ))}

                </div>


                {/* DETAILS */}
                <div className="mt-4 grid grid-cols-2 gap-4 text-xs text-slate-400 sm:grid-cols-4">

                  <div>
                    <div className="text-slate-500">
                      Methods
                    </div>

                    <div className="mt-1 text-sm text-slate-200">
                      {cycle.method_count}
                    </div>
                  </div>

                  <div>
                    <div className="text-slate-500">
                      Coverage
                    </div>

                    <div className="mt-1 text-sm text-slate-200">
                      {(cycle.method_coverage * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div>
                    <div className="text-slate-500">
                      Dispersion
                    </div>

                    <div className="mt-1 text-sm text-slate-200">
                      {cycle.period_dispersion.toFixed(4)}
                    </div>
                  </div>

                  <div>
                    <div className="text-slate-500">
                      Evidence
                    </div>

                    <div className="mt-1 text-sm text-slate-200">
                      {cycle.evidence.length}
                    </div>
                  </div>

                </div>


                {/* EVIDENCE */}
                <div className="mt-4 border-t border-[#32485f] pt-4">

                  <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Evidence
                  </div>

                  <div className="space-y-1">

                    {cycle.evidence.map((item, evidenceIndex) => (

                      <div
                        key={`${item.method}-${evidenceIndex}`}
                        className="flex items-center justify-between text-xs"
                      >

                        <span className="text-slate-400">
                          {item.method}
                        </span>

                        <span className="text-slate-300">
                          {item.period_years.toFixed(3)} years
                        </span>

                      </div>

                    ))}

                  </div>

                </div>

              </div>

            ))}

          </div>
        )}
      </div>

    </section>
  );
}