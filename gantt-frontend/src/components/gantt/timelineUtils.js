export const DAY_MS = 24 * 60 * 60 * 1000;
export const HOUR_MS = 60 * 60 * 1000;

export function calcScaleDays(scaleType, centerTs) {
  const centerDate = new Date(centerTs);
  if (scaleType === "day") return 1;
  if (scaleType === "week") return 7;
  if (scaleType === "two-weeks") return 14;
  if (scaleType === "month") {
    const y = centerDate.getFullYear();
    const m = centerDate.getMonth();
    return new Date(y, m + 1, 0).getDate();
  }
  if (scaleType === "quarter") {
    const y = centerDate.getFullYear();
    const m = centerDate.getMonth();
    const qStart = Math.floor(m / 3) * 3;
    let d = 0;
    for (let i = 0; i < 3; i++) d += new Date(y, qStart + i + 1, 0).getDate();
    return d;
  }
  if (scaleType === "year") {
    const y = centerDate.getFullYear();
    const leap = (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
    return leap ? 366 : 365;
  }
  return 30;
}

export function buildTimeline(
  scaleType,
  centerTs,
  chartWidth,
  minDate = null,
  maxDate = null,
) {
  let startTs;
  let endTs;
  let totalDays;

  if (minDate !== null && maxDate !== null) {
    startTs = minDate;
    endTs = maxDate;
    totalDays = Math.ceil((endTs - startTs) / DAY_MS);
    const padding = Math.max((endTs - startTs) * 0.05, DAY_MS);
    startTs -= padding;
    endTs += padding;
    totalDays = Math.ceil((endTs - startTs) / DAY_MS);
  } else {
    totalDays = calcScaleDays(scaleType, centerTs);
    const rangeMs = totalDays * DAY_MS;
    startTs = centerTs - rangeMs / 2;
    endTs = centerTs + rangeMs / 2;
  }

  if (!chartWidth) {
    return {
      viewStart: new Date(startTs),
      viewEnd: new Date(endTs),
      totalDays,
      timeline: null,
    };
  }

  let pxPerDay;
  let timelineWidth;

  if (minDate !== null && maxDate !== null) {
    const scaleDays = calcScaleDays(scaleType, centerTs);
    pxPerDay = Math.max(chartWidth / scaleDays, 0.5);
    timelineWidth = Math.max(chartWidth, Math.floor(totalDays * pxPerDay));
  } else {
    pxPerDay = Math.max(chartWidth / totalDays, 1);
    timelineWidth = chartWidth;
  }

  const dayStepMap = {
    day: 1,
    week: 1,
    "two-weeks": 1,
    month: 2,
    quarter: 7,
    year: 30,
  };
  const dayStep = dayStepMap[scaleType] || 7;

  const ticks = [];

  if (minDate !== null && maxDate !== null) {
    for (let d = 0; d <= totalDays; d += dayStep) {
      const ts = startTs + d * DAY_MS;
      if (ts > endTs) break;
      const x = d * pxPerDay;
      ticks.push({
        timestamp: ts,
        x,
        label: new Date(ts).toLocaleDateString("ru-RU", {
          day: "2-digit",
          month: "2-digit",
        }),
      });
    }
  } else if (scaleType === "day") {
    const firstHour = Math.ceil(startTs / HOUR_MS) * HOUR_MS;
    for (let ts = firstHour; ts <= endTs; ts += HOUR_MS) {
      const x = ((ts - startTs) / DAY_MS) * pxPerDay;
      ticks.push({
        timestamp: ts,
        x,
        label: new Date(ts).toLocaleTimeString("ru-RU", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      });
    }
  } else {
    for (let d = 0; d <= totalDays; d += dayStep) {
      const ts = startTs + d * DAY_MS;
      const x = d * pxPerDay;
      ticks.push({
        timestamp: ts,
        x,
        label: new Date(ts).toLocaleDateString("ru-RU", {
          day: "2-digit",
          month: "2-digit",
        }),
      });
    }
  }

  return {
    viewStart: new Date(startTs),
    viewEnd: new Date(endTs),
    totalDays,
    timeline: {
      start: startTs,
      end: endTs,
      width: timelineWidth,
      ticks,
      pxPerDay,
      totalDays,
    },
  };
}
