"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { SignalRecord } from "@/lib/api";


type SignalChartProps = {
  data: SignalRecord[];
};


export function SignalChart({ data }: SignalChartProps) {
  const chartData = data.map((item) => ({
    ...item,
    timestampLabel: formatTimestamp(item.signal_timestamp),
  }));

  return (
    <div className="h-[360px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
          <CartesianGrid stroke="rgba(22, 48, 43, 0.12)" strokeDasharray="4 4" />
          <XAxis
            dataKey="timestampLabel"
            tick={{ fill: "#5c6f69", fontSize: 12 }}
            minTickGap={24}
          />
          <YAxis tick={{ fill: "#5c6f69", fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              borderRadius: "16px",
              border: "1px solid rgba(22, 48, 43, 0.12)",
              boxShadow: "0 16px 40px rgba(22, 48, 43, 0.08)",
            }}
            formatter={(value: number) => [value.toFixed(2), "Sinal"]}
            labelFormatter={(label) => `Horario: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="signal_value"
            stroke="#5F8B4C"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 5, fill: "#C97B63" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}


function formatTimestamp(timestamp: string) {
  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
