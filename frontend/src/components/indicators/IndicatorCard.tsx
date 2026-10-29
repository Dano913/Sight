import { Link } from "react-router-dom";

interface IndicatorCardProps {
  indicator: {
    code: string;
    name: string;
    category: string;
  };
}

export default function IndicatorCard({
  indicator,
}: IndicatorCardProps) {
  return (
    <article className="overflow-hidden rounded-lg border-2 border-zinc-600 bg-zinc-900">
      {/* Header */}
      <div className="border-b-2 border-zinc-600 px-5 py-4">
        <div className="flex items-center justify-between">
          <span className="font-mono text-xl font-bold tracking-wider text-white">
            {indicator.code}
          </span>

          <span className="rounded border-2 border-zinc-500 px-2 py-1 text-xs font-semibold uppercase tracking-widest text-zinc-300">
            {indicator.category}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="border-b-2 border-zinc-600 px-5 py-5">
        <h3 className="text-lg font-semibold leading-snug text-white">
          {indicator.name}
        </h3>
      </div>

      {/* Footer */}
      <div className="grid grid-cols-2">
        <div className="border-r-2 border-zinc-600 p-4">
          <p className="text-[11px] uppercase tracking-widest text-zinc-500">
            Source
          </p>

          <p className="mt-2 font-medium text-white">
            Eurostat
          </p>
        </div>

        <div className="p-4">
          <p className="text-[11px] uppercase tracking-widest text-zinc-500">
            Frequency
          </p>

          <p className="mt-2 font-medium text-white">
            Monthly
          </p>
        </div>
      </div>

      <div className="border-t-2 border-zinc-600 px-5 py-3">
        <Link to={`/indicators/${indicator.code}`}>
          <button className="cursor-pointer w-full border-2 border-blue-500 py-2 text-sm font-semibold uppercase tracking-wider text-blue-400 transition hover:bg-blue-500 hover:text-white">
            View Indicator
          </button>
        </Link>
      </div>
    </article>
  );
}