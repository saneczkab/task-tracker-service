import React, { forwardRef, Fragment, useMemo, useState } from "react";
import {
  HEADER_HEIGHT,
  LABEL_HEIGHT,
  FONT_SIZE,
  SIDEBAR_WIDTH,
} from "./ganttConstants.js";
import { IconButton, Menu, MenuItem, CircularProgress } from "@mui/material";
import {
  MoreVert as MoreVertIcon,
  Add as AddIcon,
  ChevronLeft as ChevronLeftIcon,
} from "@mui/icons-material";
import GoalForm from "../tasks/GoalForm.jsx";
import TaskForm from "../tasks/TaskForm.jsx";

import { useProcessError } from "../../hooks/useProcessError.js";
import { deleteGoalApi, updateGoalApi } from "../../api/goal.js";
import { deleteTaskApi, updateTaskApi } from "../../api/task.js";
import { fetchStatusesApi, fetchPrioritiesApi } from "../../api/meta.js";

const GanttSidebar = forwardRef(
  (
    {
      rows,
      open,
      renderHeight,
      onDataChanged,
      onToggleSidebar,
      projectId,
      teamId,
    },
    ref,
  ) => {
    const processError = useProcessError();
    const token = useMemo(
      () => window.localStorage.getItem("auth_token") || "",
      [],
    );

    const [menuAnchorEl, setMenuAnchorEl] = useState(null);
    const [menuRow, setMenuRow] = useState(null);
    const menuOpen = Boolean(menuAnchorEl);

    const [goalFormOpen, setGoalFormOpen] = useState(false);
    const [taskFormOpen, setTaskFormOpen] = useState(false);
    const [selectedGoal, setSelectedGoal] = useState(null);
    const [selectedTask, setSelectedTask] = useState(null);
    const [currentStreamId, setCurrentStreamId] = useState(null);
    const [statuses, setStatuses] = useState([]);
    const [priorities, setPriorities] = useState([]);
    const [metaLoading, setMetaLoading] = useState(false);
    const [hoveredRow, setHoveredRow] = useState(null);
    const [draggedGoal, setDraggedGoal] = useState(null);
    const [draggedTask, setDraggedTask] = useState(null);
    const [dropTarget, setDropTarget] = useState(null);

    const grouped = useMemo(() => {
      const result = [];
      let currentStream = null;
      let currentGoals = [];
      let currentTasks = [];

      for (const row of rows) {
        if (row.type === "stream") {
          if (currentStream) {
            result.push({
              stream: currentStream,
              goals: currentGoals,
              tasks: currentTasks,
            });
          }
          currentStream = row;
          currentGoals = [];
          currentTasks = [];
        } else if (row.type === "goal") {
          currentGoals.push(row);
        } else if (row.type === "task") {
          currentTasks.push(row);
        }
      }

      if (currentStream)
        result.push({
          stream: currentStream,
          goals: currentGoals,
          tasks: currentTasks,
        });

      return result;
    }, [rows]);

    const loadMeta = async () => {
      if (statuses.length && priorities.length) {
        return;
      }

      setMetaLoading(true);

      const statusesResp = await fetchStatusesApi();
      if (!statusesResp.ok) {
        processError(statusesResp.status);
        return;
      }
      setStatuses(statusesResp.statuses);

      const prioritiesResp = await fetchPrioritiesApi();
      if (!prioritiesResp.ok) {
        processError(prioritiesResp.status);
        return;
      }
      setPriorities(prioritiesResp.priorities);

      setMetaLoading(false);
    };

    const openMenu = (event, row, streamId) => {
      setMenuAnchorEl(event.currentTarget);
      setMenuRow({ type: row.type, item: row.item, streamId });
    };

    const handleAddTask = async (streamId, afterPosition = null) => {
      setSelectedTask({ position: afterPosition });
      setCurrentStreamId(streamId);
      await loadMeta();
      setTaskFormOpen(true);
    };

    const handleEdit = async () => {
      if (menuRow.type === "goal") {
        setSelectedGoal(menuRow.item);
        setCurrentStreamId(menuRow.streamId);
        setGoalFormOpen(true);
      } else if (menuRow.type === "task") {
        setSelectedTask(menuRow.item);
        setCurrentStreamId(menuRow.streamId);
        await loadMeta();
        setTaskFormOpen(true);
      }

      setMenuAnchorEl(null);
    };

    const handleDelete = async () => {
      if (menuRow.type === "goal") {
        const reponse = await deleteGoalApi(menuRow.item.id, token);
        if (!reponse.ok) {
          processError(reponse.status);
          return;
        }
      } else if (menuRow.type === "task") {
        const response = await deleteTaskApi(menuRow.item.id, token);
        if (!response.ok) {
          processError(response.status);
          return;
        }
      }

      onDataChanged?.({
        type: menuRow.type,
        action: "delete",
        streamId: menuRow.streamId,
        item: menuRow.item,
      });

      setHoveredRow((prev) =>
        menuRow.item?.id === prev?.id && menuRow.type === prev?.type
          ? null
          : prev,
      );
      setMenuAnchorEl(null);
    };

    const handleGoalSaved = (saved) => {
      const action = selectedGoal ? "update" : "create";
      setGoalFormOpen(false);
      setSelectedGoal(null);
      onDataChanged?.({
        type: "goal",
        action,
        streamId: currentStreamId,
        item: saved,
      });
    };

    const handleTaskSaved = async (saved) => {
      const action = selectedTask?.id ? "update" : "create";

      setTaskFormOpen(false);
      setSelectedTask(null);
      onDataChanged?.({
        type: "task",
        action,
        streamId: currentStreamId,
        item: saved,
      });
    };

    const handleBeforeCreateTask = async (newPosition) => {
      const streamTasks = grouped
        .find((g) => g.stream.item.id === currentStreamId)
        ?.tasks.map((task) => task.item)
        .sort((a, b) => (a.position || 0) - (b.position || 0)) || [];

      for (const task of streamTasks) {
        if (task.position >= newPosition) {
          const payload = {
            name: task.name,
            status_id: Number(task.status_id) || null,
            priority_id: Number(task.priority_id) || null,
            assignee_email: task.assignee_email || null,
            start_date: task.start_date || null,
            deadline: task.deadline || null,
            position: task.position + 1,
          };

          const response = await updateTaskApi(task.id, payload, token);
          if (!response.ok) {
            processError(response.status);
          }
        }
      }
    };

    const handleGoalDragStart = (goal, streamId) => {
      setDraggedGoal({ goal, streamId });
    };

    const handleGoalDragOver = (e, targetGoal, targetStreamId) => {
      e.preventDefault();
      if (
        draggedGoal &&
        draggedGoal.streamId === targetStreamId &&
        draggedGoal.goal.id !== targetGoal.id
      ) {
        setDropTarget({ goal: targetGoal, streamId: targetStreamId });
      }
    };

    const handleGoalDrop = async (e, targetGoal, targetStreamId) => {
      e.preventDefault();
      if (!draggedGoal || draggedGoal.streamId !== targetStreamId) {
        setDraggedGoal(null);
        setDropTarget(null);
        return;
      }

      const sourceGoal = draggedGoal.goal;
      if (sourceGoal.id === targetGoal.id) {
        setDraggedGoal(null);
        setDropTarget(null);
        return;
      }

      const streamGoals =
        grouped
          .find((g) => g.stream.item.id === targetStreamId)
          ?.goals.map((g) => g.item)
          .sort((a, b) => (a.position || 0) - (b.position || 0)) || [];

      const sourceIdx = streamGoals.findIndex((g) => g.id === sourceGoal.id);
      const targetIdx = streamGoals.findIndex((g) => g.id === targetGoal.id);

      if (sourceIdx === -1 || targetIdx === -1) {
        setDraggedGoal(null);
        setDropTarget(null);
        return;
      }

      const reordered = [...streamGoals];
      const [removed] = reordered.splice(sourceIdx, 1);
      reordered.splice(targetIdx, 0, removed);

      for (let i = 0; i < reordered.length; i++) {
        const goal = reordered[i];
        const newPosition = i + 1;
        const payload = {
          name: goal.name?.trim() || "Цель",
          deadline: goal.deadline || null,
          position: newPosition,
        };
        const response = await updateGoalApi(goal.id, payload, token);
        if (!response.ok) {
          processError(response.status);
          setDraggedGoal(null);
          setDropTarget(null);
          return;
        }
      }

      onDataChanged?.({
        type: "goal",
        action: "reorder",
        streamId: targetStreamId,
        goals: reordered.map((g, idx) => ({ ...g, position: idx + 1 })),
      });

      setDraggedGoal(null);
      setDropTarget(null);
    };

    const handleGoalDragEnd = () => {
      setDraggedGoal(null);
      setDropTarget(null);
    };

    const handleTaskDragStart = (task, streamId) => {
      setDraggedTask({ task, streamId });
    };

    const handleTaskDragOver = (e, targetTask, targetStreamId) => {
      e.preventDefault();
      if (
        draggedTask &&
        draggedTask.streamId === targetStreamId &&
        draggedTask.task.id !== targetTask.id
      ) {
        setDropTarget({ task: targetTask, streamId: targetStreamId });
      }
    };

    const handleTaskDrop = async (e, targetTask, targetStreamId) => {
      e.preventDefault();
      if (!draggedTask || draggedTask.streamId !== targetStreamId) {
        setDraggedTask(null);
        setDropTarget(null);
        return;
      }

      const sourceTask = draggedTask.task;
      if (sourceTask.id === targetTask.id) {
        setDraggedTask(null);
        setDropTarget(null);
        return;
      }

      const streamTasks =
        grouped
          .find((g) => g.stream.item.id === targetStreamId)
          ?.tasks.map((t) => t.item)
          .sort((a, b) => (a.position || 0) - (b.position || 0)) || [];

      const sourceIdx = streamTasks.findIndex((t) => t.id === sourceTask.id);
      const targetIdx = streamTasks.findIndex((t) => t.id === targetTask.id);

      if (sourceIdx === -1 || targetIdx === -1) {
        setDraggedTask(null);
        setDropTarget(null);
        return;
      }

      const reordered = [...streamTasks];
      const [removed] = reordered.splice(sourceIdx, 1);
      reordered.splice(targetIdx, 0, removed);

      for (let i = 0; i < reordered.length; i++) {
        const task = reordered[i];
        const newPosition = i + 1;
        const payload = {
          name: task.name?.trim() || "Задача",
          status_id: Number(task.status_id) || null,
          priority_id: Number(task.priority_id) || null,
          assignee_email: task.assignee_email || null,
          start_date: task.start_date || null,
          deadline: task.deadline || null,
          position: newPosition,
        };
        const response = await updateTaskApi(task.id, payload, token);
        if (!response.ok) {
          processError(response.status);
          setDraggedTask(null);
          setDropTarget(null);
          return;
        }
      }

      onDataChanged?.({
        type: "task",
        action: "reorder",
        streamId: targetStreamId,
        tasks: reordered.map((t, idx) => ({ ...t, position: idx + 1 })),
      });

      setDraggedTask(null);
      setDropTarget(null);
    };

    const handleTaskDragEnd = () => {
      setDraggedTask(null);
      setDropTarget(null);
    };

    return (
      <div
        ref={ref}
        style={{
          width: open ? SIDEBAR_WIDTH : 0,
          background: "#fff",
          borderRight: open ? "1px solid #EDEDED" : "none",
          zIndex: 50,
          transition: "width 0.3s ease-in-out",
          overflow: "hidden",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            minWidth: open ? SIDEBAR_WIDTH : 0,
            width: open ? SIDEBAR_WIDTH : 0,
          }}
        >
          <div
            style={{
              height: HEADER_HEIGHT,
              position: "relative",
              borderBottom: "1px solid #ededed",
            }}
          >
            <IconButton
              size="small"
              onClick={onToggleSidebar}
              sx={{
                position: "absolute",
                right: 8,
                top: "50%",
                transform: "translateY(-50%)",
                background: "#fff",
                padding: "4px",
                "&:hover": { background: "#f3f3f3" },
              }}
            >
              <ChevronLeftIcon fontSize="small" />
            </IconButton>
          </div>
          <div
            style={{
              position: "relative",
              height: renderHeight - HEADER_HEIGHT,
            }}
          >
            {grouped.map(({ stream, goals, tasks }) => (
              <Fragment key={`stream-${stream.item.id}`}>
                <div
                  style={{
                    position: "absolute",
                    top: (stream.labelTop || stream.top) - HEADER_HEIGHT,
                    height: LABEL_HEIGHT,
                    display: "flex",
                    alignItems: "center",
                    padding: "12px 12px",
                    fontSize: 14,
                    fontWeight: 600,
                  }}
                >
                  {stream.item.name}
                </div>
                {goals.map((goal) => {
                  const showActions =
                    (hoveredRow?.id === goal.item.id &&
                      hoveredRow?.type === "goal") ||
                    (menuOpen &&
                      menuRow?.item?.id === goal.item.id &&
                      menuRow?.type === "goal");

                  const isDragging =
                    draggedGoal?.goal.id === goal.item.id &&
                    draggedGoal?.streamId === stream.item.id;
                  const isDropTarget =
                    dropTarget?.goal?.id === goal.item.id &&
                    dropTarget?.streamId === stream.item.id;

                  return (
                    <div
                      key={`goal-${goal.item.id}`}
                      draggable
                      onDragStart={() =>
                        handleGoalDragStart(goal.item, stream.item.id)
                      }
                      onDragOver={(e) =>
                        handleGoalDragOver(e, goal.item, stream.item.id)
                      }
                      onDrop={(e) =>
                        handleGoalDrop(e, goal.item, stream.item.id)
                      }
                      onDragEnd={handleGoalDragEnd}
                      style={{
                        position: "absolute",
                        top: goal.top - HEADER_HEIGHT,
                        left: 0,
                        right: 0,
                        height: goal.height,
                        display: "flex",
                        alignItems: "center",
                        fontSize: FONT_SIZE - 1,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        opacity: isDragging ? 0.5 : 1,
                        background: isDropTarget ? "#e3f2fd" : "transparent",
                        borderTop: isDropTarget ? "2px solid #2196f3" : "none",
                        cursor: "move",
                      }}
                      title={goal.item.name}
                      onMouseEnter={() =>
                        setHoveredRow({ id: goal.item.id, type: "goal" })
                      }
                      onMouseLeave={() =>
                        setHoveredRow((prev) =>
                          prev?.id === goal.item.id && prev?.type === "goal"
                            ? null
                            : prev,
                        )
                      }
                    >
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAddTask(stream.item.id, goal.item.position);
                        }}
                        sx={{
                          position: "absolute",
                          top: "50%",
                          transform: "translateY(-50%)",
                          opacity: showActions ? 1 : 0,
                        }}
                      >
                        <AddIcon fontSize="inherit" />
                      </IconButton>
                      <span style={{ marginLeft: 24 }}>{goal.item.name}</span>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          openMenu(e, goal, stream.item.id);
                        }}
                        sx={{
                          position: "absolute",
                          right: 4,
                          top: "50%",
                          transform: "translateY(-50%)",
                          opacity: showActions ? 1 : 0,
                        }}
                      >
                        <MoreVertIcon fontSize="inherit" />
                      </IconButton>
                    </div>
                  );
                })}

                {tasks.map((task) => {
                  const showActions =
                    (hoveredRow?.id === task.item.id &&
                      hoveredRow?.type === "task") ||
                    (menuOpen &&
                      menuRow?.item?.id === task.item.id &&
                      menuRow?.type === "task");

                  const isDragging =
                    draggedTask?.task.id === task.item.id &&
                    draggedTask?.streamId === stream.item.id;
                  const isDropTarget =
                    dropTarget?.task?.id === task.item.id &&
                    dropTarget?.streamId === stream.item.id;

                  return (
                    <div
                      key={`task-${task.item.id}`}
                      draggable
                      onDragStart={() =>
                        handleTaskDragStart(task.item, stream.item.id)
                      }
                      onDragOver={(e) =>
                        handleTaskDragOver(e, task.item, stream.item.id)
                      }
                      onDrop={(e) =>
                        handleTaskDrop(e, task.item, stream.item.id)
                      }
                      onDragEnd={handleTaskDragEnd}
                      style={{
                        position: "absolute",
                        top: task.top - HEADER_HEIGHT,
                        left: 0,
                        right: 0,
                        height: task.height,
                        display: "flex",
                        alignItems: "center",
                        fontSize: FONT_SIZE - 1,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        opacity: isDragging ? 0.5 : 1,
                        background: isDropTarget ? "#e3f2fd" : "transparent",
                        borderTop: isDropTarget ? "2px solid #2196f3" : "none",
                        cursor: "move",
                      }}
                      title={task.item.name}
                      onMouseEnter={() =>
                        setHoveredRow({ id: task.item.id, type: "task" })
                      }
                      onMouseLeave={() =>
                        setHoveredRow((prev) =>
                          prev?.id === task.item.id && prev?.type === "task"
                            ? null
                            : prev,
                        )
                      }
                    >
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAddTask(stream.item.id, task.item.position);
                        }}
                        sx={{
                          position: "absolute",
                          top: "50%",
                          transform: "translateY(-50%)",
                          opacity: showActions ? 1 : 0,
                        }}
                      >
                        <AddIcon fontSize="inherit" />
                      </IconButton>
                      <span style={{ marginLeft: 24 }}>{task.item.name}</span>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          openMenu(e, task, stream.item.id);
                        }}
                        sx={{
                          position: "absolute",
                          right: 4,
                          top: "50%",
                          transform: "translateY(-50%)",
                          opacity: showActions ? 1 : 0,
                        }}
                      >
                        <MoreVertIcon fontSize="inherit" />
                      </IconButton>
                    </div>
                  );
                })}
              </Fragment>
            ))}

            {rows.map((row) => (
              <div
                style={{
                  position: "absolute",
                  top: row.top - HEADER_HEIGHT + row.height,
                  left: 0,
                  right: 0,
                  height: 1,
                  background: "#E0E0E0",
                }}
              />
            ))}
          </div>

          <Menu
            anchorEl={menuAnchorEl}
            open={menuOpen}
            onClose={() => setMenuAnchorEl(null)}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "right" }}
          >
            <MenuItem onClick={handleEdit}>Редактировать</MenuItem>
            <MenuItem onClick={handleDelete}>Удалить</MenuItem>
          </Menu>

          <GoalForm
            open={goalFormOpen}
            onClose={() => {
              setGoalFormOpen(false);
              setSelectedGoal(null);
            }}
            streamId={currentStreamId}
            goal={selectedGoal}
            onSaved={handleGoalSaved}
          />

          <TaskForm
            open={taskFormOpen}
            onClose={() => {
              setTaskFormOpen(false);
              setSelectedTask(null);
            }}
            streamId={currentStreamId}
            task={selectedTask}
            statuses={statuses}
            priorities={priorities}
            projectId={projectId}
            teamId={teamId}
            onSaved={handleTaskSaved}
            onBeforeCreate={handleBeforeCreateTask}
          />

          {metaLoading && <CircularProgress size={16} />}
        </div>
      </div>
    );
  },
);

export default GanttSidebar;
