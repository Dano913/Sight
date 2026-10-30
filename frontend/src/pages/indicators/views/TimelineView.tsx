import type {
  Indicator,
  Region,
  ObservationResponse,
} from "../types.ts";

import { useAsyncData } from "../../../hooks/useAsyncData";

import {
  fetchTimeline,
  resolveIndicatorCode,
} from "../api";
import TimelineChart from "./timeline/TimelineChart";
import TimelineTable from "./timeline/TimelineTable";

interface TimelineViewProps {
  code: string;
  indicator: Indicator | null;
  regions: Region[];
  selectedRegion: string | null;
  onRegionChange: (region: string) => void;
}

const EMPTY_OBSERVATIONS: ObservationResponse[] = [];

export default function TimelineView({
  code,
  indicator,
  regions,
  selectedRegion,
  onRegionChange,
}: TimelineViewProps) {
  const effectiveCode = selectedRegion
    ? resolveIndicatorCode(code, selectedRegion)
    : null;

  const timeline = useAsyncData(
    selectedRegion && effectiveCode
      ? `${selectedRegion}|${effectiveCode}`
      : null,
    async (signal) => {
      const data = await fetchTimeline(
        selectedRegion!,
        effectiveCode!,
        signal
      );

      return data.indicators?.[effectiveCode!] ?? EMPTY_OBSERVATIONS;
    }
  );

  const observations = timeline.data ?? EMPTY_OBSERVATIONS;
  const loading = timeline.loading;
  const error = timeline.error
    ? `No hay datos de ${effectiveCode} para este país.`
    : null;

  return (
    <div>
      {/* ================================================= */}
      {/* SELECTOR DE REGIÓN */}
      {/* ================================================= */}

      <div className="mb-6 flex items-center gap-3">
        <label className="text-xs uppercase tracking-wider text-slate-400">
          Country
        </label>

        <select
          value={selectedRegion ?? ""}
          onChange={(e) =>
            onRegionChange(e.target.value)
          }
          className="w-56 rounded-lg border border-[#32485f] bg-[#1b2a39] px-3 py-2 text-white outline-none transition focus:border-blue-500"
        >
          {regions.map((region) => (
            <option
              key={region.code}
              value={region.code}
            >
              {region.name}
            </option>
          ))}
        </select>
      </div>

      {/* ================================================= */}
      {/* ERROR */}
      {/* ================================================= */}

      {error && (
        <p className="mb-4 text-sm text-red-400">
          {error}
        </p>
      )}

      {/* ================================================= */}
      {/* GRÁFICO */}
      {/* ================================================= */}

      <section className="overflow-hidden rounded-xl border border-[#32485f] bg-[#223548] p-6">
        <h2 className="mb-4 text-sm uppercase tracking-wider text-slate-400">
          Evolución
        </h2>

        {loading ? (
          <p className="py-10 text-center text-slate-400">
            Loading...
          </p>
        ) : (
          <TimelineChart
            observations={observations}
          />
        )}
      </section>

      {/* ================================================= */}
      {/* TABLA DESPLEGABLE */}
      {/* ================================================= */}

      <details className="mt-8 overflow-hidden rounded-xl border border-[#32485f] bg-[#223548]">
        <summary className="cursor-pointer select-none px-6 py-4 text-sm uppercase tracking-wider text-slate-400 transition hover:text-white">
          Datos históricos
        </summary>

        <div className="border-t border-[#32485f]">
          {loading ? (
            <p className="py-10 text-center text-slate-400">
              Loading...
            </p>
          ) : (
            <TimelineTable
              observations={observations}
              unit={indicator?.unit}
            />
          )}
        </div>
      </details>
    </div>
  );
}