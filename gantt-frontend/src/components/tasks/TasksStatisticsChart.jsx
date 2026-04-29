import React, { useMemo } from "react";
import { CircularProgress } from "@mui/material";
import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const TasksStatisticsChart = ({ statistics, loading = false, error = "" }) => {
  const chartData = useMemo(() => {
    if (!statistics) {
      return { data: [], total: 0 };
    }

    const data = [
      { name: "Просрочено", value: statistics.overdue || 0, fill: "#EF4444" },
      {
        name: "Выполнено",
        value: statistics.completed_on_time || 0,
        fill: "#22C55E",
      },
      {
        name: "В процессе",
        value: statistics.in_progress || 0,
        fill: "#3B82F6",
      },
    ];

    return {
      data,
      total: statistics.total_tasks || 0,
    };
  }, [statistics]);

  const { data, total } = chartData;

  if (loading) {
    return (
      <div className="flex items-center justify-center w-full h-64">
        <CircularProgress size={40} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center w-full h-64 text-red-600">
        <p>{error}</p>
      </div>
    );
  }

  if (total === 0) {
    return (
      <div className="flex items-center justify-center w-full h-64 text-gray-500">
        <p>Нет задач для отображения статистики</p>
      </div>
    );
  }

  const renderLegend = (props) => {
    const payload = props?.payload || [];
    return (
      <div style={{ fontFamily: "Montserrat, sans-serif" }}>
        {payload.map((entry) => (
          <div
            key={entry.value}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 10,
              whiteSpace: "nowrap",
            }}
          >
            <span
              style={{
                width: 18,
                height: 18,
                borderRadius: "9999px",
                backgroundColor: entry.color,
                display: "inline-block",
              }}
            />
            <span
              style={{
                display: "inline-flex",
                alignItems: "baseline",
                gap: 10,
                fontSize: 18,
                color: "#111827",
                lineHeight: 1.2,
              }}
            >
              <span
                style={{
                  width: 42,
                  textAlign: "right",
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {entry.payload?.value ?? 0}
              </span>
              <span>{entry.value}</span>
            </span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="w-full" style={{ fontFamily: "Montserrat, sans-serif" }}>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="28%"
            cy="50%"
            innerRadius={70}
            outerRadius={95}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => `${value} задач${value === 1 ? "а" : ""}`}
            contentStyle={{
              backgroundColor: "#f9fafb",
              border: "1px solid #e5e7eb",
              borderRadius: "6px",
              fontFamily: "Montserrat, sans-serif",
            }}
          />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            content={renderLegend}
          />
          <text
            x="46%"
            y="44%"
            textAnchor="middle"
            fill="#000000"
            fontSize="16"
            fontWeight="600"
            style={{ fontFamily: "Montserrat, sans-serif" }}
          >
            Всего задач
          </text>
          <text
            x="46%"
            y="53%"
            textAnchor="middle"
            fill="#000000"
            fontSize="32"
            fontWeight="700"
            style={{ fontFamily: "Montserrat, sans-serif" }}
          >
            {total}
          </text>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TasksStatisticsChart;
