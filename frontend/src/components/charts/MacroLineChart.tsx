import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

type Observation = {
    date: string;
    value: number;
    source: string;
};

type MacroLineChartProps = {
    title: string;
    observations: Observation[];
    unit?: string;
};

export default function MacroLineChart({
    title,
    observations,
    unit = "",
}: MacroLineChartProps) {
    const data = observations.map((observation) => ({
        date: observation.date.slice(0, 4),
        value: observation.value,
    }));

    return (
        <div
            style={{
                background: "#ffffff",
                border: "1px solid #e2e8f0",
                borderRadius: 12,
                padding: 20,
            }}
        >
            <div
                style={{
                    fontSize: 16,
                    fontWeight: 600,
                    color: "#1b2a39",
                    marginBottom: 16,
                }}
            >
                {title}
            </div>

            {data.length === 0 ? (
                <div
                    style={{
                        height: 280,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#94a3b8",
                    }}
                >
                    No data available
                </div>
            ) : (
                <ResponsiveContainer width="100%" height={280}>
                    <LineChart
                        data={data}
                        margin={{
                            top: 5,
                            right: 20,
                            left: 10,
                            bottom: 5,
                        }}
                    >
                        <CartesianGrid strokeDasharray="3 3" />

                        <XAxis
                            dataKey="date"
                            tick={{ fontSize: 11 }}
                            minTickGap={30}
                        />

                        <YAxis
                            tick={{ fontSize: 11 }}
                            width={60}
                        />

                        <Tooltip
                            formatter={(
                                value:
                                    | string
                                    | number
                                    | ReadonlyArray<string | number>
                                    | undefined,
                            ) => {
                                const numericValue = Array.isArray(value)
                                    ? value[0]
                                    : value;

                                return [
                                    numericValue !== undefined
                                        ? `${Number(numericValue).toLocaleString("en-US", {
                                              maximumFractionDigits: 2,
                                          })}${unit}`
                                        : "",
                                    title,
                                ];
                            }}
                        />

                        <Line
                            type="monotone"
                            dataKey="value"
                            stroke="#2563eb"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            )}
        </div>
    );
}