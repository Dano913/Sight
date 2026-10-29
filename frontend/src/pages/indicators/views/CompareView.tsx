import { useEffect, useMemo, useState } from "react";
import type {
  Indicator,
  RegionResponse,
  ObservationResponse,
} from "../types";
import { fetchComparison } from "../api";

import CompareChart, {
  type CompareRow,
} from "./compare/CompareChart";
import CompareTable from "./compare/CompareTable";

interface CompareViewProps {
  code: string;
  indicator: Indicator | null;
}

const DEFAULT_REGIONS = [
  "EU27_2020",
  "DE",
  "FR",
  "IT",
  "ES",
  "NL",
  "PL",
  "BE",
  "SE",
  "AT",
  "IE",
  "DK",
  "FI",
  "CZ",
  "PT",
  "US",
];

export default function CompareView({
  code,
  indicator,
}: CompareViewProps) {
  const [comparison, setComparison] = useState<RegionResponse[]>([]);
  const [selectedYear, setSelectedYear] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);

  useEffect(() => {
    loadComparison();
  }, [code]);

  async function loadComparison() {

    console.log("LOAD COMPARISON");
    console.log(code);

    try {
      setLoading(true);

      const data = await fetchComparison(code, DEFAULT_REGIONS);

      console.log(data[0]);
      console.log(data[0].indicators);
      console.log(Object.keys(data[0].indicators));
      console.log(data);

      setComparison(data);

      setSelectedRegions(
        data.map((r: { region: { code: any; }; }) => r.region.code)
      );

      const years = new Set<string>();

      data.forEach((region: { indicators: { [x: string]: never[]; }; }) => {
        const observations: ObservationResponse[] =
          region.indicators[code] ?? [];

        observations.forEach((observation) => {
          years.add(observation.date.slice(0, 4));
        });
      });

      const sortedYears = [...years].sort(
        (a, b) => Number(b) - Number(a)
      );

      if (sortedYears.length > 0) {
        setSelectedYear(sortedYears[0]);
      }
    } finally {
      setLoading(false);
    }
  }

  function toggleRegion(code: string) {
    setSelectedRegions((current) =>
      current.includes(code)
        ? current.filter((c) => c !== code)
        : [...current, code]
    );
  }

  function selectAll() {
    setSelectedRegions(
      comparison.map((r) => r.region.code)
    );
  }

  function clearAll() {
    setSelectedRegions([]);
  }

  const availableYears = useMemo(() => {
    const years = new Set<string>();

    comparison.forEach((region) => {
      const observations: ObservationResponse[] =
        region.indicators[code] ?? [];

      observations.forEach((observation) => {
        years.add(observation.date.slice(0, 4));
      });
    });

    return [...years].sort(
      (a, b) => Number(b) - Number(a)
    );
  }, [comparison, code]);

  const rows: CompareRow[] = useMemo(() => {
    return comparison
      .filter((region) =>
        selectedRegions.includes(region.region.code)
      )
      .map((region) => {
        const observations: ObservationResponse[] =
          region.indicators[code] ?? [];

        const observation = observations
          .filter((o) => o.date.startsWith(selectedYear))
          .sort((a, b) => b.date.localeCompare(a.date))[0];

        if (!observation) return null;

        return {
          code: region.region.code,
          name: region.region.name,
          value: observation.value,
        };
      })
      .filter((row): row is CompareRow => row !== null)
      .sort((a, b) => b.value - a.value);
  }, [comparison, selectedYear, code, selectedRegions]);

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <label className="text-xs uppercase tracking-wider text-slate-400">
          Year
        </label>

        <select
          value={selectedYear}
          onChange={(e) => setSelectedYear(e.target.value)}
          className="w-40 rounded-lg border border-[#32485f] bg-[#1b2a39] px-3 py-2 text-white"
        >
          {availableYears.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-6">
  <p className="mb-3 text-xs uppercase tracking-wider text-slate-400">
    Countries
  </p>

  <div className="grid grid-cols-2 gap-2">
    <div className="mb-3 flex gap-2">
  <button
    onClick={selectAll}
    className="rounded-md border border-[#32485f] px-3 py-1 text-sm text-white hover:bg-[#32485f]"
  >
    Select all
  </button>

  <button
    onClick={clearAll}
    className="rounded-md border border-[#32485f] px-3 py-1 text-sm text-white hover:bg-[#32485f]"
  >
    Clear all
  </button>
</div>
    {comparison.map((region) => (
      <label
        key={region.region.code}
        className="flex items-center gap-2 text-sm text-white"
      >
        <input
          type="checkbox"
          checked={selectedRegions.includes(region.region.code)}
          onChange={() => toggleRegion(region.region.code)}
        />

        {region.region.name}
      </label>
    ))}
  </div>
</div>

      <section className="overflow-hidden rounded-xl border border-[#32485f] bg-[#223548] p-6">
        <h2 className="mb-4 text-sm uppercase tracking-wider text-slate-400">
          Comparación por país
        </h2>

        {loading ? (
          <p className="py-10 text-center text-slate-400">
            Loading...
          </p>
        ) : (
          <CompareChart rows={rows} />
        )}
      </section>

      <section className="mt-8 overflow-hidden rounded-xl border border-[#32485f] bg-[#223548]">
        {loading ? (
          <p className="py-10 text-center text-slate-400">
            Loading...
          </p>
        ) : (
          <CompareTable
            rows={rows}
            unit={indicator?.unit}
          />
        )}
      </section>
    </div>
  );
}