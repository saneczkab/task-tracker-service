import React, { useMemo, Fragment } from "react";
import GanttGoalBar from "./GanttGoalBar.jsx";
import GanttTaskBar from "./GanttTaskBar.jsx";
import {
  SEPARATOR_OFFSET,
  GOAL_ROW_HEIGHT,
  TASK_ROW_HEIGHT,
  ROW_GAP,
  LABEL_HEIGHT,
  LABEL_MARGIN,
  BETWEEN_GOALS_TASKS,
  STREAM_BOTTOM_PADDING,
  FONT_SIZE,
} from "./ganttConstants.js";
import { DAY_MS } from "./timelineUtils.js";

const GanttStream = ({
  streamId,
  streamName,
  goals,
  tasks,
  timeline,
  baseTop,
  onStartResizeTask,
  onEndResizeTask,
  onStartResizeGoal,
  onEndResizeGoal,
  resizingInfo,
  onContextMenuGoal,
  onContextMenuTask,
  onDragStartTask,
  onDragStartGoal,
  draggingInfo,
  verticalDraggingInfo,
  relationColorMap = {},
}) => {
  const layout = useMemo(() => {
    const lineY = baseTop + SEPARATOR_OFFSET;
    const goalsTop = baseTop + SEPARATOR_OFFSET + LABEL_HEIGHT + LABEL_MARGIN;
    const goalsHeight = goals.length
      ? goals.length * (GOAL_ROW_HEIGHT + ROW_GAP)
      : 0;
    const tasksTop = goalsTop + goalsHeight + BETWEEN_GOALS_TASKS;
    const tasksHeight = tasks.length
      ? tasks.length * (TASK_ROW_HEIGHT + ROW_GAP)
      : 0;
    const totalHeight =
      tasksTop + tasksHeight + STREAM_BOTTOM_PADDING - baseTop;

    return { lineY, goalsTop, tasksTop, totalHeight };
  }, [goals, tasks, baseTop]);

  const dateToX = (timestamp) =>
    ((timestamp - timeline.start) / DAY_MS) * timeline.pxPerDay;

  const getBarBounds = (startTs, endTs) => {
    let xStart = typeof startTs === "number" ? dateToX(startTs) : 0;
    let xEnd = typeof endTs === "number" ? dateToX(endTs) : timeline.width;
    if (xEnd < xStart) {
      [xStart, xEnd] = [xEnd, xStart];
    }

    const left = Math.max(0, Math.min(xStart, timeline.width));
    const right = Math.max(0, Math.min(xEnd, timeline.width));
    return { left, width: Math.max(2, right - left), xStart, xEnd };
  };

  return (
    <>
      <div
        style={{
          position: "absolute",
          top: layout.lineY,
          left: 0,
          right: 0,
          height: 1,
          background: "#ededed",
        }}
      />

      {goals.map((goal, idx) => {
        let startTs = goal?.start_date
          ? new Date(goal.start_date).getTime()
          : null;
        let endTs = goal?.deadline ? new Date(goal.deadline).getTime() : null;

        if (
          draggingInfo &&
          draggingInfo.type === "goal" &&
          draggingInfo.itemId === goal.id
        ) {
          startTs = startTs ? startTs + draggingInfo.deltaMs : startTs;
          endTs = endTs ? endTs + draggingInfo.deltaMs : endTs;
        }

        const { left, width, xStart, xEnd } = getBarBounds(startTs, endTs);
        const startVisible = startTs ? startTs >= timeline.start : false;
        const endVisible = endTs ? endTs <= timeline.end : false;
        const roundLeft = startVisible;
        let adjustedWidth = width;
        let adjustedLeft = left;

        if (
          resizingInfo &&
          resizingInfo.type === "goal" &&
          resizingInfo.itemId === goal.id
        ) {
          const timestampX = dateToX(resizingInfo.currentTs);
          if (resizingInfo.edge === "start") {
            const newLeft = Math.max(0, Math.min(timestampX, xEnd));
            adjustedLeft = newLeft;
            adjustedWidth = Math.max(2, xEnd - newLeft);
          } else if (resizingInfo.edge === "end") {
            adjustedWidth = Math.max(
              2,
              Math.min(timeline.width, timestampX) - adjustedLeft,
            );
          }
        }

        const isBeingDragged =
          draggingInfo?.type === "goal" && draggingInfo?.itemId === goal.id;
        const isBeingResized =
          resizingInfo?.type === "goal" && resizingInfo?.itemId === goal.id;

        const isBeingVerticallyDragged =
          verticalDraggingInfo?.type === "goal" &&
          verticalDraggingInfo?.itemId === goal.id &&
          verticalDraggingInfo?.streamId === streamId;

        let verticalOffset = 0;
        if (isBeingVerticallyDragged && verticalDraggingInfo.deltaY) {
          verticalOffset = verticalDraggingInfo.deltaY;
        }

        const showDropIndicator = isBeingDragged || isBeingVerticallyDragged;
        const targetRowIdx =
          showDropIndicator && verticalDraggingInfo?.deltaY
            ? Math.max(
                0,
                Math.min(
                  goals.length - 1,
                  idx +
                    Math.round(verticalOffset / (GOAL_ROW_HEIGHT + ROW_GAP)),
                ),
              )
            : idx;

        return (
          <Fragment key={`goal-${goal.id}`}>
            {showDropIndicator && (
              <div
                style={{
                  position: "absolute",
                  top:
                    layout.goalsTop +
                    targetRowIdx * (GOAL_ROW_HEIGHT + ROW_GAP),
                  left: 0,
                  width: timeline.width,
                  height: GOAL_ROW_HEIGHT,
                  backgroundColor: "#e3f2fd",
                  borderTop: "2px solid #2196f3",
                  pointerEvents: "none",
                  zIndex: 5,
                }}
              />
            )}

            <GanttGoalBar
              goal={goal}
              style={{
                position: "absolute",
                top:
                  layout.goalsTop +
                  idx * (GOAL_ROW_HEIGHT + ROW_GAP) +
                  verticalOffset,
                left: adjustedLeft,
                width: adjustedWidth,
                height: GOAL_ROW_HEIGHT,
                opacity:
                  isBeingDragged || isBeingResized || isBeingVerticallyDragged
                    ? 0.5
                    : 1,
                cursor:
                  isBeingDragged || isBeingVerticallyDragged
                    ? "move"
                    : "default",
                zIndex: isBeingVerticallyDragged || isBeingDragged ? 10 : 2,
              }}
              onDragStart={(goal, e) => onDragStartGoal?.(goal, streamId, e)}
              roundLeft={roundLeft}
              roundRight={endVisible}
              onContextMenu={(e) => onContextMenuGoal?.(e, goal, streamId)}
              canResizeStart={startVisible}
              canResizeEnd={endVisible}
              onResizeEdge={(edge) => {
                if (edge === "start") {
                  onStartResizeGoal?.(goal, streamId, xStart);
                } else {
                  onEndResizeGoal?.(goal, streamId, xEnd);
                }
              }}
              isResizing={isBeingResized}
              isDragging={isBeingDragged || isBeingVerticallyDragged}
            />
          </Fragment>
        );
      })}

      {tasks.map((task, idx) => {
        let start = task.start_date
          ? new Date(task.start_date).getTime()
          : null;
        let end = task.deadline ? new Date(task.deadline).getTime() : null;

        if (
          draggingInfo &&
          draggingInfo.type === "task" &&
          draggingInfo.itemId === task.id
        ) {
          start = start ? start + draggingInfo.deltaMs : start;
          end = end ? end + draggingInfo.deltaMs : end;
        }

        const isVisible = (() => {
          if (start && end) {
            return !(end < timeline.start || start >= timeline.end);
          }
          if (start) {
            return !(start >= timeline.end);
          }
          if (end) {
            return !(end < timeline.start);
          }
          return true;
        })();

        if (!isVisible) {
          return (
            <div
              style={{
                position: "absolute",
                top: layout.tasksTop + idx * (TASK_ROW_HEIGHT + ROW_GAP),
                left: 0,
                width: "100%",
                height: TASK_ROW_HEIGHT,
                pointerEvents: "none",
              }}
            />
          );
        }

        const { left, width, xStart, xEnd } = getBarBounds(start, end);
        const startVisible = start ? start >= timeline.start : false;
        const endVisible = end ? end <= timeline.end : false;
        const roundLeft = startVisible;
        let adjustedLeft = left;
        let adjustedWidth = width;

        if (
          resizingInfo &&
          resizingInfo.type === "task" &&
          resizingInfo.itemId === task.id
        ) {
          const timestampX = dateToX(resizingInfo.currentTs);
          if (resizingInfo.edge === "start") {
            const newLeft = Math.max(0, Math.min(timestampX, xEnd));
            adjustedLeft = newLeft;
            adjustedWidth = Math.max(2, xEnd - newLeft);
          } else if (resizingInfo.edge === "end") {
            const newEnd = Math.max(
              xStart,
              Math.min(timestampX, timeline.width),
            );
            adjustedWidth = Math.max(2, newEnd - xStart);
          }
        }

        const isBeingDragged =
          draggingInfo?.type === "task" && draggingInfo?.itemId === task.id;
        const isBeingResized =
          resizingInfo?.type === "task" && resizingInfo?.itemId === task.id;

        const isBeingVerticallyDragged =
          verticalDraggingInfo?.type === "task" &&
          verticalDraggingInfo?.itemId === task.id &&
          verticalDraggingInfo?.streamId === streamId;

        let verticalOffset = 0;
        if (isBeingVerticallyDragged && verticalDraggingInfo.deltaY) {
          verticalOffset = verticalDraggingInfo.deltaY;
        }

        const showDropIndicator = isBeingDragged || isBeingVerticallyDragged;
        const targetRowIdx =
          showDropIndicator && verticalDraggingInfo?.deltaY
            ? Math.max(
                0,
                Math.min(
                  tasks.length - 1,
                  idx +
                    Math.round(verticalOffset / (TASK_ROW_HEIGHT + ROW_GAP)),
                ),
              )
            : idx;

        return (
          <Fragment key={`task-${task.id}`}>
            {showDropIndicator && (
              <div
                style={{
                  position: "absolute",
                  top:
                    layout.tasksTop +
                    targetRowIdx * (TASK_ROW_HEIGHT + ROW_GAP),
                  left: 0,
                  width: timeline.width,
                  height: TASK_ROW_HEIGHT,
                  backgroundColor: "#e3f2fd",
                  borderTop: "2px solid #2196f3",
                  pointerEvents: "none",
                  zIndex: 5,
                }}
              />
            )}

            <GanttTaskBar
              task={task}
              style={{
                position: "absolute",
                top:
                  layout.tasksTop +
                  idx * (TASK_ROW_HEIGHT + ROW_GAP) +
                  verticalOffset,
                left: adjustedLeft,
                width: adjustedWidth,
                height: TASK_ROW_HEIGHT,
                opacity:
                  isBeingDragged || isBeingResized || isBeingVerticallyDragged
                    ? 0.5
                    : 1,
                cursor:
                  isBeingDragged || isBeingVerticallyDragged
                    ? "move"
                    : "default",
                zIndex: isBeingVerticallyDragged || isBeingDragged ? 10 : 1,
              }}
              roundLeft={roundLeft}
              roundRight={endVisible}
              onDragStart={(task, e) => onDragStartTask?.(task, streamId, e)}
              onContextMenu={(e) => onContextMenuTask?.(e, task, streamId)}
              canResizeStart={startVisible}
              canResizeEnd={endVisible}
              onResizeEdge={(edge) => {
                if (edge === "start")
                  onStartResizeTask?.(task, streamId, xStart, xEnd);
                else onEndResizeTask?.(task, streamId, xStart, xEnd);
              }}
              isResizing={isBeingResized}
              isDragging={isBeingDragged || isBeingVerticallyDragged}
              relationColor={relationColorMap[task.id] || null}
            />
          </Fragment>
        );
      })}
    </>
  );
};

export default GanttStream;
