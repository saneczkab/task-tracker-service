import React from "react";
import { FONT_SIZE } from "./ganttConstants.js";

const GanttTaskBar = ({
  task,
  style,
  onDragStart,
  roundLeft,
  roundRight,
  onContextMenu,
  canResizeStart,
  canResizeEnd,
  onResizeEdge,
  isResizing,
  isDragging,
  relationColor = null,
}) => {
  const radius = 6;
  const titleText = `${task?.name || "Задача"}`;

  return (
    <div
      style={{
        fontSize: FONT_SIZE,
        display: "flex",
        alignItems: "center",
        padding: "0 10px",
        boxShadow: "0 2px 4px rgba(0,0,0,0.32)",
        background: "#f8f8fb",
        border: "1px solid #dfdfdf",
        color: "#000000",
        borderTopLeftRadius: roundLeft ? radius : 0,
        borderBottomLeftRadius: roundLeft ? radius : 0,
        borderTopRightRadius: roundRight ? radius : 0,
        borderBottomRightRadius: roundRight ? radius : 0,
        userSelect: "none",
        pointerEvents: "auto",
        ...style,
      }}
      title={titleText}
      onMouseDown={(e) => !isResizing && onDragStart?.(task, e)}
      onContextMenu={(e) => {
        e.preventDefault();
        if (!isResizing && !isDragging) {
          onContextMenu?.(e);
        }
      }}
    >
      {relationColor && (
        <div
          style={{
            width: 20,
            height: 20,
            backgroundColor: relationColor,
            borderRadius: 2,
            marginRight: 8,
            flexShrink: 0,
          }}
        />
      )}
      <span
        style={{
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {titleText}
      </span>

      {canResizeStart && (
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            bottom: 0,
            width: 6,
            cursor: "ew-resize",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onMouseDown={(e) => {
            e.stopPropagation();
            e.preventDefault();
            onResizeEdge?.("start");
          }}
          onClick={(e) => e.stopPropagation()}
          onContextMenu={(e) => e.preventDefault()}
        >
          <div style={{ width: 2, height: "60%", background: "#a1a1a1" }} />
        </div>
      )}

      {canResizeEnd && (
        <div
          style={{
            position: "absolute",
            right: 0,
            top: 0,
            bottom: 0,
            width: 6,
            cursor: "ew-resize",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onMouseDown={(e) => {
            e.stopPropagation();
            e.preventDefault();
            onResizeEdge?.("end");
          }}
          onClick={(e) => e.stopPropagation()}
          title="Изменить дедлайн"
          onContextMenu={(e) => e.preventDefault()}
        >
          <div style={{ width: 2, height: "60%", background: "#a1a1a1" }} />
        </div>
      )}
    </div>
  );
};

export default GanttTaskBar;
