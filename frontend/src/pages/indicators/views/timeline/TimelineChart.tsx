import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

import type { ObservationResponse as Observation } from "../../types.ts";

interface TimelineChartProps {
  observations: Observation[];
}

export default function TimelineChart({
  observations,
}: TimelineChartProps) {
  const chartData = [...observations]
    .sort(
      (a, b) =>
        new Date(a.date).getTime() -
        new Date(b.date).getTime()
    )
    .map((observation) => ({
      ...observation,
      dateLabel: new Date(
        observation.date
      ).toLocaleDateString("es-ES", {
        month: "short",
        year: "numeric",
      }),
    }));

  if (chartData.length === 0) {
    return (
      <p className="py-10 text-center text-slate-400">
        No data to display.
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart
        data={chartData}
        margin={{
          top: 10,
          right: 20,
          left: 0,
          bottom: 10,
        }}
      >
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="#32485f"
        />

        <XAxis
          dataKey="dateLabel"
          stroke="#94a3b8"
          fontSize={12}
          tickLine={false}
          minTickGap={40}
        />

        <YAxis
          stroke="#94a3b8"
          fontSize={12}
          tickLine={false}
          width={60}
        />

        <Tooltip
          contentStyle={{
            backgroundColor: "#1b2a39",
            border: "1px solid #32485f",
            borderRadius: 8,
            color: "#fff",
          }}
          labelStyle={{
            color: "#94a3b8",
          }}
        />

        <Line
          type="monotone"
          dataKey="value"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}