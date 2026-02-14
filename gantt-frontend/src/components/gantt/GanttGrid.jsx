import React from "react";
import { HEADER_HEIGHT } from "./ganttConstants.js";

const GanttGrid = ({ timeline }) => {
  return (
    <div
      style={{
        position: "absolute",
        top: HEADER_HEIGHT,
        left: 0,
        bottom: 0,
        width: timeline.width,
        zIndex: 0,
      }}
    >
      {timeline.ticks.map((tick, idx) => (
        <div
          key={idx}
          style={{
            position: "absolute",
            left: tick.x,
            top: 0,
            bottom: 0,
            width: 1,
            background: "#ececec",
          }}
        />
      ))}
    </div>
  );
};

export default GanttGrid;
