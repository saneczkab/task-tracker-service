import React from "react";
import { FONT_SIZE, HEADER_HEIGHT } from "./ganttConstants.js";
import { DAY_MS } from "./timelineUtils.js";

const GanttTimelineHeader = ({ timeline, scaleType }) => {
  const dayStepMap = {
    day: 1,
    week: 1,
    "two-weeks": 1,
    month: 1,
    quarter: 2,
    year: 7,
  };
  const dayStep = dayStepMap[scaleType] || 7;

  const startTs = timeline.start;
  const endTs = timeline.end;
  const pxPerDay = timeline.pxPerDay;

  const dateToX = (ts) => ((ts - startTs) / DAY_MS) * pxPerDay;

  const topLabels = [];
  if (scaleType === "day") {
    const startDate = new Date(startTs);
    startDate.setHours(0, 0, 0, 0);

    let dayCursor = new Date(startDate);
    if (dayCursor.getTime() < startTs) {
      dayCursor.setDate(dayCursor.getDate() + 1);
    }

    while (dayCursor.getTime() < endTs) {
      const ts = dayCursor.getTime();
      topLabels.push({
        ts,
        x: dateToX(ts),
        text: dayCursor.toLocaleDateString("ru-RU", {
          day: "numeric",
          month: "long",
          year: "numeric",
        }),
      });
      dayCursor.setDate(dayCursor.getDate() + 1);
    }
  } else {
    const startDate = new Date(startTs);
    startDate.setHours(0, 0, 0, 0);
    let monthCursor = new Date(
      startDate.getFullYear(),
      startDate.getMonth(),
      1,
    );
    if (monthCursor.getTime() < startTs) {
      monthCursor = new Date(
        startDate.getFullYear(),
        startDate.getMonth() + 1,
        1,
      );
    }
    while (monthCursor.getTime() < endTs) {
      const ts = monthCursor.getTime();
      topLabels.push({
        ts,
        x:
          // TODO: разобраться со смещениями, убрать магические числа
          scaleType === "week" || scaleType === "two-weeks"
            ? dateToX(ts) + 85
            : scaleType === "month"
              ? dateToX(ts) + 45
              : dateToX(ts) + 15,
        text: monthCursor.toLocaleDateString("ru-RU", {
          month: "long",
          year: "numeric",
        }),
      });
      monthCursor.setMonth(monthCursor.getMonth() + 1, 1);
    }
  }

  const bottomLabels = [];
  if (scaleType === "day") {
    const HOUR_MS = 60 * 60 * 1000;
    const startHour = new Date(startTs);
    startHour.setMinutes(0, 0, 0);

    let hourCursor = startHour.getTime();
    if (hourCursor < startTs) {
      hourCursor += HOUR_MS;
    }

    while (hourCursor < endTs) {
      const date = new Date(hourCursor);
      const hours = date.getHours();
      bottomLabels.push({
        ts: hourCursor,
        x: dateToX(hourCursor),
        text: `${hours.toString().padStart(2, "0")}:00`,
      });
      hourCursor += HOUR_MS;
    }
  } else {
    const totalDays = Math.ceil((endTs - startTs) / DAY_MS);
    for (let d = 0; d <= totalDays; d += dayStep) {
      const ts = startTs + d * DAY_MS;
      if (ts > endTs) break;
      const date = new Date(ts);
      bottomLabels.push({
        ts,
        x: dateToX(ts),
        text: date.getDate(),
      });
    }
  }

  return (
    <div
      style={{
        position: "absolute",
        height: HEADER_HEIGHT,
        width: timeline.width,
        borderBottom: "1px solid #ededed",
        fontSize: 13,
      }}
    >
      {topLabels.map((label) => (
        <div
          key={`top-${label.ts}`}
          style={{
            position: "absolute",
            top: 4,
            left: label.x,
            fontSize: scaleType === "day" ? 13 : 13,
            fontWeight: 600,
            whiteSpace: "nowrap",
          }}
        >
          {label.text}
        </div>
      ))}

      {bottomLabels.map((label) => (
        <div
          key={`bottom-${label.ts}`}
          style={{
            position: "absolute",
            left: label.x,
            bottom: 4,
            fontSize: scaleType === "day" ? FONT_SIZE - 2 : FONT_SIZE,
            color: scaleType === "day" ? "#6b7280" : "#385865",
          }}
        >
          {label.text}
        </div>
      ))}

      <div
        style={{
          position: "absolute",
          right: 8,
          display: "flex",
          gap: 6,
          padding: "4px 4px",
        }}
      ></div>
    </div>
  );
};

export default GanttTimelineHeader;
