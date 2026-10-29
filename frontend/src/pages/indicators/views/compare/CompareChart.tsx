import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export interface CompareRow {
  code: string;
  name: string;
  value: number;
}

interface CompareChartProps {
  rows: CompareRow[];
}

export default function CompareChart({ rows }: CompareChartProps) {
  if (rows.length === 0) {
    return (
      <p className="py-10 text-center text-slate-400">
        No data to display.
      </p>
    );
  }

  const height = Math.max(240, rows.length * 40);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={rows} layout="vertical" margin={{ left: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#32485f" />
        <XAxis type="number" stroke="#94a3b8" fontSize={12} tickLine={false} />
        <YAxis
          type="category"
          dataKey="name"
          stroke="#94a3b8"
          fontSize={12}
          tickLine={false}
          width={110}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1b2a39",
            border: "1px solid #32485f",
            borderRadius: 8,
            color: "#fff",
          }}
          labelStyle={{ color: "#94a3b8" }}
        />
        <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}