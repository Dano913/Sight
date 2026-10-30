import type { ObservationResponse as Observation } from "../../types.ts";

interface TimelineTableProps {
  observations: Observation[];
  unit?: string;
}

export default function TimelineTable({
  observations,
  unit,
}: TimelineTableProps) {
  const sorted = [...observations].sort(
    (a, b) =>
      new Date(b.date).getTime() -
      new Date(a.date).getTime()
  );

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left">
        <thead className="border-b border-[#32485f] bg-[#1b2a39]">
          <tr>
            <th className="px-6 py-4 text-xs font-medium uppercase tracking-wider text-slate-400">
              Date
            </th>

            <th className="px-6 py-4 text-xs font-medium uppercase tracking-wider text-slate-400">
              Value
            </th>

            <th className="px-6 py-4 text-xs font-medium uppercase tracking-wider text-slate-400">
              Unit
            </th>
          </tr>
        </thead>

        <tbody>
          {sorted.length === 0 ? (
            <tr>
              <td
                colSpan={3}
                className="px-6 py-10 text-center text-slate-400"
              >
                No observations available.
              </td>
            </tr>
          ) : (
            sorted.map((observation) => (
              <tr
                key={observation.date}
                className="border-b border-[#32485f] transition hover:bg-[#2b4258]"
              >
                <td className="px-6 py-4 text-white">
                  {observation.date}
                </td>

                <td className="px-6 py-4 text-white">
                  {observation.value.toFixed(2)}
                </td>

                <td className="px-6 py-4 text-slate-300">
                  {unit}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}