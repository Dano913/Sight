import type { CompareRow } from "./CompareChart";

interface CompareTableProps {
  rows: CompareRow[];
  unit?: string;
}

export default function CompareTable({ rows, unit }: CompareTableProps) {
  return (
    <table className="w-full">
      <thead className="bg-[#1f3042]">
        <tr>
          <th className="border-b border-[#32485f] px-6 py-4 text-left text-slate-300">
            Rank
          </th>
          <th className="border-b border-[#32485f] px-6 py-4 text-left text-slate-300">
            Country
          </th>
          <th className="border-b border-[#32485f] px-6 py-4 text-left text-slate-300">
            Value
          </th>
          <th className="border-b border-[#32485f] px-6 py-4 text-left text-slate-300">
            Unit
          </th>
        </tr>
      </thead>

      <tbody>
        {rows.length === 0 ? (
          <tr>
            <td colSpan={4} className="px-6 py-10 text-center text-slate-400">
              No observations available.
            </td>
          </tr>
        ) : (
          rows.map((row, index) => (
            <tr
              key={row.code}
              className="border-b border-[#32485f] transition hover:bg-[#2b4258]"
            >
              <td className="px-6 py-4 text-slate-400">{index + 1}</td>
              <td className="px-6 py-4 text-white">{row.name}</td>
              <td className="px-6 py-4 text-white">{row.value}</td>
              <td className="px-6 py-4 text-slate-300">{unit}</td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}