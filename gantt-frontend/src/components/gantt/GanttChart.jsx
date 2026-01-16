import React, {
  useState,
  useEffect,
  useMemo,
  useRef,
  useLayoutEffect,
  useCallback,
} from "react";
import {
  CircularProgress,
  Menu,
  MenuItem,
  IconButton,
  Button,
  Select,
} from "@mui/material";
import { fetchStreamsApi } from "../../api/stream.js";
import { fetchStatusesApi, fetchPrioritiesApi } from "../../api/meta.js";
import GanttStream from "./GanttStream.jsx";
import GanttTimelineHeader from "./GanttTimelineHeader.jsx";
import GanttGrid from "./GanttGrid.jsx";
import CurrentTimeMarker from "./CurrentTimeMarker.jsx";
import { buildTimeline, calcScaleDays, DAY_MS } from "./timelineUtils.js";
import {
  HEADER_HEIGHT,
  GOAL_ROW_HEIGHT,
  TASK_ROW_HEIGHT,
  ROW_GAP,
  SEPARATOR_OFFSET,
  LABEL_HEIGHT,
  LABEL_MARGIN,
  STREAM_BOTTOM_PADDING,
  BETWEEN_GOALS_TASKS,
  FONT_SIZE,
  SIDEBAR_WIDTH,
} from "./ganttConstants.js";
import GanttSidebar from "./GanttSidebar.jsx";
import GoalForm from "../tasks/GoalForm.jsx";
import TaskForm from "../tasks/TaskForm.jsx";
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from "@mui/icons-material";

import { useProcessError } from "../../hooks/useProcessError.js";
import { fetchGoalsApi, updateGoalApi, deleteGoalApi } from "../../api/goal.js";
import { fetchTasksApi, updateTaskApi, deleteTaskApi } from "../../api/task.js";
import { generateRelationColors } from "../../utils/relationColors.js";

const GanttChart = ({ projId, teamId }) => {
  const [streamsData, setStreamsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef(null);
  const chartAreaRef = useRef(null);
  const [chartWidth, setChartWidth] = useState(null);
  const [chartAreaHeight, setChartAreaHeight] = useState(0);
  const [scaleType, setScaleType] = useState("week");
  const prevScaleTypeRef = useRef("week");
  const [centerTs, setCenterTs] = useState(() => Date.now());
  const [nowTs, setNowTs] = useState(Date.now());
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [goalFormOpen, setGoalFormOpen] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState(null);
  const [goalStreamId, setGoalStreamId] = useState(null);

  const [taskFormOpen, setTaskFormOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [taskStreamId, setTaskStreamId] = useState(null);

  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);

  const [resizing, setResizing] = useState(null);
  const [dragging, setDragging] = useState(null);
  const [verticalDragging, setVerticalDragging] = useState(null);
  const [contextMenu, setContextMenu] = useState(null);

  const processError = useProcessError();
  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );

  useEffect(() => {
    const id = setInterval(() => setNowTs(Date.now()), 60 * 1000);
    return () => clearInterval(id);
  }, []);

  const dateRange = useMemo(() => {
    let minDate = null;
    let maxDate = null;

    streamsData.forEach((stream) => {
      stream.tasks.forEach((task) => {
        if (task.start_date) {
          const startTs = new Date(task.start_date).getTime();
          if (!minDate || startTs < minDate) {
            minDate = startTs;
          }
        }
        if (task.deadline) {
          const deadlineTs = new Date(task.deadline).getTime();
          if (!maxDate || deadlineTs > maxDate) {
            maxDate = deadlineTs;
          }
        }
      });

      stream.goals.forEach((goal) => {
        if (goal.start_date) {
          const startTs = new Date(goal.start_date).getTime();
          if (!minDate || startTs < minDate) {
            minDate = startTs;
          }
        }
        if (goal.deadline) {
          const deadlineTs = new Date(goal.deadline).getTime();
          if (!maxDate || deadlineTs > maxDate) {
            maxDate = deadlineTs;
          }
        }
      });
    });

    if (minDate === null || maxDate === null) {
      return { minDate: null, maxDate: null };
    }

    const MIN_RANGE_MS = 7 * DAY_MS;
    if (maxDate - minDate < MIN_RANGE_MS) {
      const center = (minDate + maxDate) / 2;
      minDate = center - MIN_RANGE_MS / 2;
      maxDate = center + MIN_RANGE_MS / 2;
    }

    return { minDate, maxDate };
  }, [streamsData]);

  const scaleDaysForNow = calcScaleDays(scaleType, nowTs);
  const nowRangeMs = scaleDaysForNow * DAY_MS;
  const nowStart = nowTs - nowRangeMs / 2;

  const adjustedMinDate =
    dateRange.minDate !== null ? Math.min(dateRange.minDate, nowStart) : null;

  const useDataRange = adjustedMinDate !== null && dateRange.maxDate !== null;

  const { timeline } = buildTimeline(
    scaleType,
    centerTs,
    chartWidth,
    adjustedMinDate,
    dateRange.maxDate,
  );

  const relationColorMap = useMemo(() => {
    const allTasks = streamsData.flatMap((stream) => stream.tasks);
    return generateRelationColors(allTasks);
  }, [streamsData]);

  const loadStreamsData = useCallback(async () => {
    setLoading(true);

    const streamsResp = await fetchStreamsApi(projId, token);
    if (!streamsResp.ok) {
      processError(streamsResp.status);
      setLoading(false);
      return;
    }

    const streams = streamsResp.streams;
    const streamData = await Promise.all(
      streams.map(async (stream) => {
        const gResp = await fetchGoalsApi(stream.id, token);
        const tResp = await fetchTasksApi(stream.id, token);
        return {
          id: stream.id,
          name: stream.name,
          goals: gResp.goals,
          tasks: tResp.tasks,
        };
      }),
    );
    setStreamsData(streamData);

    setLoading(false);
  }, [processError, projId, token]);

  const loadMeta = useCallback(async () => {
    const statusesResp = await fetchStatusesApi();
    const prioritiesResp = await fetchPrioritiesApi();

    if (!statusesResp.ok) {
      processError(statusesResp);
      return;
    }

    if (!prioritiesResp.ok) {
      processError(prioritiesResp);
      return;
    }

    setStatuses(statusesResp.statuses);
    setPriorities(prioritiesResp.priorities);
  }, [processError]);

  useEffect(() => {
    loadStreamsData();
  }, [projId, token]);

  useEffect(() => {
    loadMeta();
  }, []);

  const measureChartWidth = useCallback(() => {
    if (!chartAreaRef.current) return;
    const w = chartAreaRef.current.getBoundingClientRect().width;
    if (w && w !== chartWidth) setChartWidth(w);
  }, [chartWidth]);

  useLayoutEffect(() => {
    measureChartWidth();
    const ro = new ResizeObserver(measureChartWidth);
    if (chartAreaRef.current) ro.observe(chartAreaRef.current);
    window.addEventListener("resize", measureChartWidth);
    const rafId = requestAnimationFrame(measureChartWidth);
    const tmId = setTimeout(measureChartWidth, 0);
    return () => {
      window.removeEventListener("resize", measureChartWidth);
      ro.disconnect();
      cancelAnimationFrame(rafId);
      clearTimeout(tmId);
    };
  }, [measureChartWidth]);

  useEffect(() => {
    if (chartWidth !== null) return;
    let attempts = 0;
    let timer = null;
    const tryMeasure = () => {
      attempts += 1;
      measureChartWidth();
      if (chartWidth === null && attempts < 5) {
        timer = setTimeout(tryMeasure, 100);
      }
    };
    timer = setTimeout(tryMeasure, 100);
    return () => clearTimeout(timer);
  }, [chartWidth, measureChartWidth]);

  useLayoutEffect(() => {
    const measureHeight = () => {
      if (!chartAreaRef.current) return;
      const h = chartAreaRef.current.getBoundingClientRect().height;
      setChartAreaHeight(h);
    };
    measureHeight();
    const ro = new ResizeObserver(measureHeight);
    if (chartAreaRef.current) ro.observe(chartAreaRef.current);
    window.addEventListener("resize", measureHeight);
    return () => {
      window.removeEventListener("resize", measureHeight);
      ro.disconnect();
    };
  }, []);

  const centerOnTimestamp = useCallback(
    (timestamp) => {
      if (chartAreaRef.current && timeline) {
        const chart = chartAreaRef.current;
        const clientW = chart.clientWidth;
        const x = ((timestamp - timeline.start) / DAY_MS) * timeline.pxPerDay;
        const targetLeft = Math.max(
          0,
          Math.min(x - clientW / 2, chart.scrollWidth - clientW),
        );
        try {
          chart.scrollTo({ left: targetLeft, behavior: "smooth" });
        } catch {
          chart.scrollLeft = targetLeft;
        }
      }
    },
    [timeline],
  );

  const initialCenteredRef = useRef(false);

  useEffect(() => {
    if (!timeline || !chartAreaRef.current) return;
    if (initialCenteredRef.current) return;
    initialCenteredRef.current = true;
    const rafId = requestAnimationFrame(() => {
      try {
        centerOnTimestamp(nowTs);
      } catch {}
    });
    return () => cancelAnimationFrame(rafId);
  }, [timeline, nowTs, centerOnTimestamp]);

  useEffect(() => {
    if (prevScaleTypeRef.current !== scaleType && timeline) {
      prevScaleTypeRef.current = scaleType;
      centerOnTimestamp(nowTs);
    }
  }, [scaleType, timeline, nowTs, centerOnTimestamp]);

  const goToday = () => {
    const now = Date.now();
    setCenterTs(now);
    setNowTs(now);
    centerOnTimestamp(now);
  };

  const scrollByVisible = (dir = 1) => {
    if (!chartAreaRef.current) return;
    const chart = chartAreaRef.current;
    const clientW = chart.clientWidth;
    const step = Math.max(100, Math.floor(clientW * 0.9));
    const target = Math.max(
      0,
      Math.min(chart.scrollLeft + dir * step, chart.scrollWidth - clientW),
    );
    try {
      chart.scrollTo({ left: target, behavior: "smooth" });
    } catch {
      chart.scrollLeft = target;
    }
  };

  const shiftRange = (dir) => {
    const stepDays = calcScaleDays(scaleType, centerTs);
    const shiftDays = Math.max(1, Math.round(stepDays * 0.25));
    setCenterTs((prev) => prev + dir * shiftDays * DAY_MS);
  };

  const onScale = (sType) => {
    setScaleType(sType);
    const now = Date.now();
    if (!useDataRange) {
      setCenterTs(now);
      setNowTs(now);
    }
  };

  const xNow = useMemo(() => {
    if (!timeline) return -1;
    return ((nowTs - timeline.start) / DAY_MS) * timeline.pxPerDay;
  }, [timeline, nowTs]);

  const contentHeight = useMemo(() => {
    let result = HEADER_HEIGHT;
    streamsData.forEach((stream) => {
      const goalsHeight = stream.goals.length * (GOAL_ROW_HEIGHT + ROW_GAP);
      const tasksHeight = stream.tasks.length * (TASK_ROW_HEIGHT + ROW_GAP);
      const streamHeight =
        SEPARATOR_OFFSET +
        LABEL_HEIGHT +
        LABEL_MARGIN +
        goalsHeight +
        BETWEEN_GOALS_TASKS +
        tasksHeight +
        STREAM_BOTTOM_PADDING;
      result += streamHeight;
    });
    return result;
  }, [streamsData]);

  const calculateStreamGeometry = (stream, currentTop) => {
    const goals = stream.goals;
    const tasks = stream.tasks;

    const baseTop = HEADER_HEIGHT + currentTop;
    const streamLabelTop = baseTop + SEPARATOR_OFFSET;
    const goalsTop = baseTop + SEPARATOR_OFFSET + LABEL_HEIGHT + LABEL_MARGIN;
    const goalsHeight = goals.length * (GOAL_ROW_HEIGHT + ROW_GAP);
    const tasksTop = goalsTop + goalsHeight + BETWEEN_GOALS_TASKS;
    const tasksHeight = tasks.length * (TASK_ROW_HEIGHT + ROW_GAP);
    const streamTotalHeight =
      SEPARATOR_OFFSET +
      LABEL_HEIGHT +
      LABEL_MARGIN +
      goalsHeight +
      BETWEEN_GOALS_TASKS +
      tasksHeight +
      STREAM_BOTTOM_PADDING;

    return {
      baseTop,
      streamLabelTop,
      goalsTop,
      goalsHeight,
      tasksTop,
      tasksHeight,
      streamTotalHeight,
      goals,
      tasks,
    };
  };

  const createStreamRow = (stream, geometry) => ({
    type: "stream",
    item: { id: stream.id, name: stream.name },
    top: geometry.baseTop + SEPARATOR_OFFSET,
    height: LABEL_HEIGHT + LABEL_MARGIN,
    labelTop: geometry.streamLabelTop,
  });

  const createGoalRows = (goals, goalsTop) =>
    goals.map((goal, idx) => ({
      type: "goal",
      item: goal,
      top: goalsTop + idx * (GOAL_ROW_HEIGHT + ROW_GAP),
      height: GOAL_ROW_HEIGHT,
    }));

  const createTaskRows = (tasks, tasksTop) =>
    tasks.map((task, idx) => ({
      type: "task",
      item: task,
      top: tasksTop + idx * (TASK_ROW_HEIGHT + ROW_GAP),
      height: TASK_ROW_HEIGHT,
    }));

  const sidebarRows = useMemo(() => {
    const rows = [];
    let totalTop = 0;
    streamsData.forEach((stream) => {
      const sortedStream = {
        ...stream,
        goals: [...stream.goals].sort(
          (a, b) => (a.position || 0) - (b.position || 0),
        ),
        tasks: [...stream.tasks].sort(
          (a, b) => (a.position || 0) - (b.position || 0),
        ),
      };
      const geometry = calculateStreamGeometry(sortedStream, totalTop);
      rows.push(createStreamRow(sortedStream, geometry));
      rows.push(...createGoalRows(geometry.goals, geometry.goalsTop));
      rows.push(...createTaskRows(geometry.tasks, geometry.tasksTop));
      totalTop += geometry.streamTotalHeight;
    });
    return rows;
  }, [streamsData]);

  const renderHeight = Math.max(contentHeight, chartAreaHeight || 0);

  const openGoalEdit = (goal, streamId) => {
    setSelectedGoal(goal);
    setGoalStreamId(streamId);
    setGoalFormOpen(true);
  };

  const openTaskEdit = (task, streamId) => {
    setSelectedTask(task);
    setTaskStreamId(streamId);
    setTaskFormOpen(true);
  };

  const handleContextMenuGoal = (e, goal, streamId) => {
    setContextMenu({
      mouseX: e.clientX + 2,
      mouseY: e.clientY - 6,
      type: "goal",
      item: goal,
      streamId,
    });
  };

  const handleContextMenuTask = (e, task, streamId) => {
    setContextMenu({
      mouseX: e.clientX + 2,
      mouseY: e.clientY - 6,
      type: "task",
      item: task,
      streamId,
    });
  };

  const closeContextMenu = () => setContextMenu(null);

  const handleEditFromMenu = () => {
    if (contextMenu.type === "goal") {
      openGoalEdit(contextMenu.item, contextMenu.streamId);
    } else if (contextMenu.type === "task") {
      openTaskEdit(contextMenu.item, contextMenu.streamId);
    }
    closeContextMenu();
  };

  const handleDeleteFromMenu = async () => {
    const { type, item } = contextMenu;
    if (type === "goal") {
      await handleGoalDelete(item);
    } else if (type === "task") {
      await handleTaskDelete(item);
    }
    closeContextMenu();
  };

  const handleTaskDelete = async (task) => {
    const response = await deleteTaskApi(task.id, token);
    if (!response.ok) {
      processError(response.status);
      return;
    }

    setStreamsData((prev) =>
      prev.map((stream) =>
        stream.id === contextMenu.streamId
          ? { ...stream, tasks: stream.tasks.filter((t) => t.id !== task.id) }
          : stream,
      ),
    );
  };

  const handleGoalDelete = async (goal) => {
    const response = await deleteGoalApi(goal.id, token);
    if (!response.ok) {
      processError(response.status);
      return;
    }

    setStreamsData((prev) =>
      prev.map((stream) =>
        stream.id === contextMenu.streamId
          ? { ...stream, goals: stream.goals.filter((g) => g.id !== goal.id) }
          : stream,
      ),
    );
  };

  const handleGoalSaved = useCallback(
    (saved) => {
      setStreamsData((prev) =>
        prev.map((stream) => {
          if (stream.id !== goalStreamId) return stream;
          const idx = stream.goals.findIndex((g) => g.id === saved.id);
          const copy = [...stream.goals];
          if (idx === -1) copy.push(saved);
          else copy[idx] = saved;
          return { ...stream, goals: copy };
        }),
      );
    },
    [goalStreamId],
  );

  const handleTaskSaved = useCallback(
    (saved) => {
      setStreamsData((prev) =>
        prev.map((stream) => {
          if (stream.id !== taskStreamId) return stream;
          const idx = stream.tasks.findIndex((t) => t.id === saved.id);
          const copy = [...stream.tasks];
          if (idx === -1) copy.push(saved);
          else copy[idx] = saved;
          return { ...stream, tasks: copy };
        }),
      );
    },
    [taskStreamId],
  );

  const handleSidebarDataChanged = useCallback(
    ({ type, action, streamId, item, goals, tasks }) => {
      setStreamsData((prev) =>
        prev.map((stream) => {
          if (stream.id !== streamId) return stream;
          if (type === "goal") {
            if (action === "reorder") {
              return { ...stream, goals: goals };
            }
            return handleGoalDataChanged(stream, item, action);
          }
          if (type === "task") {
            if (action === "reorder") {
              return { ...stream, tasks: tasks };
            }
            return handleTaskDataChanged(stream, item, action);
          }
          return stream;
        }),
      );
    },
    [],
  );

  const handleTaskDataChanged = (stream, item, action) => {
    if (action === "delete")
      return { ...stream, tasks: stream.tasks.filter((t) => t.id !== item.id) };
    if (action === "create") {
      if (stream.tasks.some((t) => t.id === item.id)) return stream;
      return { ...stream, tasks: [...stream.tasks, item] };
    }
    if (action === "update")
      return {
        ...stream,
        tasks: stream.tasks.map((t) => (t.id === item.id ? item : t)),
      };
  };

  const handleGoalDataChanged = (stream, item, action) => {
    if (action === "delete")
      return { ...stream, goals: stream.goals.filter((g) => g.id !== item.id) };
    if (action === "create") {
      if (stream.goals.some((g) => g.id === item.id)) return stream;
      return { ...stream, goals: [...stream.goals, item] };
    }
    if (action === "update")
      return {
        ...stream,
        goals: stream.goals.map((g) => (g.id === item.id ? item : g)),
      };
  };

  const xToTimestamp = useCallback(
    (x) => {
      const clamped = Math.max(0, Math.min(timeline.width, x));
      const days = clamped / timeline.pxPerDay;
      return timeline.start + days * DAY_MS;
    },
    [timeline],
  );

  const handleStartResizeTask = (task, streamId) => {
    setTaskStreamId(streamId);
    setResizing({
      type: "task",
      item: task,
      itemId: task.id,
      edge: "start",
      streamId,
    });
  };

  const handleResizeTaskDeadline = (task, streamId) => {
    setTaskStreamId(streamId);
    setResizing({
      type: "task",
      item: task,
      itemId: task.id,
      edge: "end",
      streamId,
    });
  };

  const handleStartResizeGoal = (goal, streamId) => {
    setGoalStreamId(streamId);
    setResizing({
      type: "goal",
      item: goal,
      itemId: goal.id,
      edge: "start",
      streamId,
    });
  };

  const handleEndResizeGoal = (goal, streamId) => {
    setGoalStreamId(streamId);
    setResizing({
      type: "goal",
      item: goal,
      itemId: goal.id,
      edge: "end",
      streamId,
    });
  };

  const handleDragStartTask = (task, streamId, e) => {
    const chartRect = chartAreaRef.current.getBoundingClientRect();
    const startX = e.clientX - chartRect.left + chartAreaRef.current.scrollLeft;
    const startY = e.clientY - chartRect.top + chartAreaRef.current.scrollTop;

    setTaskStreamId(streamId);

    setDragging({
      type: "task",
      item: task,
      itemId: task.id,
      streamId,
      startX,
      initialStartTs: task.start_date
        ? new Date(task.start_date).getTime()
        : null,
      initialEndTs: task.deadline ? new Date(task.deadline).getTime() : null,
    });

    setVerticalDragging({
      type: "task",
      item: task,
      itemId: task.id,
      streamId,
      startY,
      initialPosition: task.position || 0,
    });
  };

  const handleDragStartGoal = (goal, streamId, e) => {
    const chartRect = chartAreaRef.current.getBoundingClientRect();
    const startX = e.clientX - chartRect.left + chartAreaRef.current.scrollLeft;
    const startY = e.clientY - chartRect.top + chartAreaRef.current.scrollTop;

    setGoalStreamId(streamId);

    setDragging({
      type: "goal",
      item: goal,
      itemId: goal.id,
      streamId,
      startX,
      initialStartTs: goal.start_date
        ? new Date(goal.start_date).getTime()
        : null,
      initialEndTs: goal.deadline ? new Date(goal.deadline).getTime() : null,
    });

    setVerticalDragging({
      type: "goal",
      item: goal,
      itemId: goal.id,
      streamId,
      startY,
      initialPosition: goal.position || 0,
    });
  };

  useEffect(() => {
    const onMove = (e) => {
      if (dragging) {
        const chartRect = chartAreaRef.current?.getBoundingClientRect();
        const currentX =
          e.clientX - chartRect.left + chartAreaRef.current.scrollLeft;
        const deltaX = currentX - dragging.startX;
        const deltaDays = deltaX / timeline.pxPerDay;
        const deltaMs = deltaDays * DAY_MS;
        setDragging((prev) => ({ ...prev, deltaMs }));
      }

      if (verticalDragging) {
        const chartRect = chartAreaRef.current?.getBoundingClientRect();
        const currentY =
          e.clientY - chartRect.top + chartAreaRef.current.scrollTop;
        const deltaY = currentY - verticalDragging.startY;
        setVerticalDragging((prev) => ({ ...prev, deltaY }));
      }
    };

    const onUpTask = async (item, deltaMs) => {
      const oldStart = item.start_date
        ? new Date(item.start_date).getTime()
        : null;
      const oldEnd = item.deadline ? new Date(item.deadline).getTime() : null;
      const newStart = oldStart ? oldStart + deltaMs : null;
      const newEnd = oldEnd ? oldEnd + deltaMs : null;
      const payload = {
        name: item.name?.trim() || "Задача",
        status_id: Number(item.status_id) || null,
        priority_id: Number(item.priority_id) || null,
        assignee_email: item.assignee_email || null,
        start_date: newStart ? new Date(newStart).toISOString() : null,
        deadline: newEnd ? new Date(newEnd).toISOString() : null,
      };
      const response = await updateTaskApi(item.id, payload, token);
      if (!response.ok) {
        processError(response.status);
        return;
      }
      handleTaskSaved(response.task);
    };

    const onUpGoal = async (item, deltaMs) => {
      const oldStart = item.start_date
        ? new Date(item.start_date).getTime()
        : null;
      const oldEnd = item.deadline ? new Date(item.deadline).getTime() : null;
      const newStart = oldStart ? oldStart + deltaMs : null;
      const newEnd = oldEnd ? oldEnd + deltaMs : null;
      const payload = {
        name: item.name?.trim() || "Цель",
        start_date: newStart ? new Date(newStart).toISOString() : null,
        deadline: newEnd ? new Date(newEnd).toISOString() : null,
      };
      const resp = await updateGoalApi(item.id, payload, token);
      if (!resp.ok) {
        processError(resp.status);
        return;
      }
      handleGoalSaved(resp.goal);
    };

    const onUpVertical = async (streamId, item, deltaY) => {
      const hasVerticalMovement =
        Number.isFinite(deltaY) && Math.abs(deltaY) >= 5;

      if (hasVerticalMovement) {
        const stream = streamsData.find((s) => s.id === streamId);
        if (!stream) return;

        const sortedGoals = [...stream.goals].sort(
          (a, b) => (a.position || 0) - (b.position || 0),
        );

        const currentIdx = sortedGoals.findIndex((g) => g.id === item.id);
        if (currentIdx === -1) return;

        const rowsShift = Math.round(deltaY / (GOAL_ROW_HEIGHT + ROW_GAP));
        let newIdx = currentIdx + rowsShift;
        newIdx = Math.max(0, Math.min(sortedGoals.length - 1, newIdx));

        if (newIdx !== currentIdx) {
          const reordered = [...sortedGoals];
          const [removed] = reordered.splice(currentIdx, 1);
          reordered.splice(newIdx, 0, removed);

          for (let i = 0; i < reordered.length; i++) {
            const goal = reordered[i];
            const newPosition = i + 1;
            const payload = {
              name: goal.name?.trim() || "Цель",
              start_date: goal.start_date || null,
              deadline: goal.deadline || null,
              position: newPosition,
            };
            const response = await updateGoalApi(goal.id, payload, token);
            if (!response.ok) {
              processError(response.status);
              return;
            }
          }

          setStreamsData((prev) =>
            prev.map((s) =>
              s.id === streamId
                ? {
                    ...s,
                    goals: reordered.map((g, idx) => ({
                      ...g,
                      position: idx + 1,
                    })),
                  }
                : s,
            ),
          );
        }
      }
    };

    const onUpVerticalTask = async (streamId, item, deltaY) => {
      const hasVerticalMovement =
        Number.isFinite(deltaY) && Math.abs(deltaY) >= 5;

      if (hasVerticalMovement) {
        const stream = streamsData.find((s) => s.id === streamId);
        if (!stream) return;

        const sortedTasks = [...stream.tasks].sort(
          (a, b) => (a.position || 0) - (b.position || 0),
        );

        const currentIdx = sortedTasks.findIndex((t) => t.id === item.id);
        if (currentIdx === -1) return;

        const rowsShift = Math.round(deltaY / (TASK_ROW_HEIGHT + ROW_GAP));
        let newIdx = currentIdx + rowsShift;
        newIdx = Math.max(0, Math.min(sortedTasks.length - 1, newIdx));

        if (newIdx !== currentIdx) {
          const reordered = [...sortedTasks];
          const [removed] = reordered.splice(currentIdx, 1);
          reordered.splice(newIdx, 0, removed);

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
              return;
            }
          }

          setStreamsData((prev) =>
            prev.map((s) =>
              s.id === streamId
                ? {
                    ...s,
                    tasks: reordered.map((t, idx) => ({
                      ...t,
                      position: idx + 1,
                    })),
                  }
                : s,
            ),
          );
        }
      }
    };

    const onUp = async () => {
      const currentDragging = dragging;
      const currentVerticalDragging = verticalDragging;

      setDragging(null);
      setVerticalDragging(null);

      const isCombinedGoalMove =
        currentDragging?.type === "goal" &&
        currentVerticalDragging?.type === "goal" &&
        currentDragging.itemId === currentVerticalDragging.itemId;

      const isCombinedTaskMove =
        currentDragging?.type === "task" &&
        currentVerticalDragging?.type === "task" &&
        currentDragging.itemId === currentVerticalDragging.itemId;

      if (isCombinedTaskMove) {
        const { item, deltaMs, streamId } = currentDragging;
        const { deltaY } = currentVerticalDragging;

        const hasHorizontalMovement =
          Number.isFinite(deltaMs) && Math.abs(deltaMs) > 0;
        const hasVerticalMovement =
          Number.isFinite(deltaY) && Math.abs(deltaY) >= 5;

        let newStartDate = null;
        let newDeadline = null;
        if (hasHorizontalMovement) {
          const oldStart = item.start_date
            ? new Date(item.start_date).getTime()
            : null;
          const oldEnd = item.deadline
            ? new Date(item.deadline).getTime()
            : null;
          const newStart = oldStart ? oldStart + deltaMs : null;
          const newEnd = oldEnd ? oldEnd + deltaMs : null;
          newStartDate = newStart ? new Date(newStart).toISOString() : null;
          newDeadline = newEnd ? new Date(newEnd).toISOString() : null;
        }

        if (hasVerticalMovement) {
          const stream = streamsData.find((s) => s.id === streamId);
          if (stream) {
            const sortedTasks = [...stream.tasks].sort(
              (a, b) => (a.position || 0) - (b.position || 0),
            );

            const currentIdx = sortedTasks.findIndex((t) => t.id === item.id);
            if (currentIdx !== -1) {
              const rowsShift = Math.round(
                deltaY / (TASK_ROW_HEIGHT + ROW_GAP),
              );
              let newIdx = currentIdx + rowsShift;
              newIdx = Math.max(0, Math.min(sortedTasks.length - 1, newIdx));

              if (newIdx !== currentIdx) {
                const reordered = [...sortedTasks];
                const [removed] = reordered.splice(currentIdx, 1);
                reordered.splice(newIdx, 0, removed);

                for (let i = 0; i < reordered.length; i++) {
                  const task = reordered[i];
                  const newPosition = i + 1;

                  if (task.id === item.id) {
                    const payload = {
                      name: task.name?.trim() || "Задача",
                      status_id: Number(task.status_id) || null,
                      priority_id: Number(task.priority_id) || null,
                      assignee_email: task.assignee_email || null,
                      position: newPosition,
                    };
                    if (hasHorizontalMovement) {
                      payload.start_date = newStartDate;
                      payload.deadline = newDeadline;
                    } else {
                      payload.start_date = task.start_date;
                      payload.deadline = task.deadline;
                    }
                    const response = await updateTaskApi(
                      task.id,
                      payload,
                      token,
                    );
                    if (!response.ok) {
                      processError(response.status);
                      return;
                    }
                    handleTaskSaved(response.task);
                  } else {
                    const payload = {
                      name: task.name?.trim() || "Задача",
                      status_id: Number(task.status_id) || null,
                      priority_id: Number(task.priority_id) || null,
                      assignee_email: task.assignee_email || null,
                      start_date: task.start_date || null,
                      deadline: task.deadline || null,
                      position: newPosition,
                    };
                    const response = await updateTaskApi(
                      task.id,
                      payload,
                      token,
                    );
                    if (!response.ok) {
                      processError(response.status);
                      return;
                    }
                  }
                }

                setStreamsData((prev) =>
                  prev.map((s) =>
                    s.id === streamId
                      ? {
                          ...s,
                          tasks: reordered.map((t, idx) => ({
                            ...t,
                            position: idx + 1,
                            start_date:
                              t.id === item.id && hasHorizontalMovement
                                ? newStartDate
                                : t.start_date,
                            deadline:
                              t.id === item.id && hasHorizontalMovement
                                ? newDeadline
                                : t.deadline,
                          })),
                        }
                      : s,
                  ),
                );
              } else if (hasHorizontalMovement) {
                await onUpTask(item, deltaMs);
              }
            }
          }
        } else if (hasHorizontalMovement) {
          await onUpTask(item, deltaMs);
        }
      } else if (isCombinedGoalMove) {
        const { item, deltaMs, streamId } = currentDragging;
        const { deltaY } = currentVerticalDragging;

        const hasHorizontalMovement =
          Number.isFinite(deltaMs) && Math.abs(deltaMs) > 0;
        const hasVerticalMovement =
          Number.isFinite(deltaY) && Math.abs(deltaY) >= 5;

        let newStartDate = null;
        let newDeadline = null;
        if (hasHorizontalMovement) {
          const oldStart = item.start_date
            ? new Date(item.start_date).getTime()
            : null;
          const oldEnd = item.deadline
            ? new Date(item.deadline).getTime()
            : null;
          const newStart = oldStart ? oldStart + deltaMs : null;
          const newEnd = oldEnd ? oldEnd + deltaMs : null;
          newStartDate = newStart ? new Date(newStart).toISOString() : null;
          newDeadline = newEnd ? new Date(newEnd).toISOString() : null;
        }

        if (hasVerticalMovement) {
          const stream = streamsData.find((s) => s.id === streamId);
          if (stream) {
            const sortedGoals = [...stream.goals].sort(
              (a, b) => (a.position || 0) - (b.position || 0),
            );

            const currentIdx = sortedGoals.findIndex((g) => g.id === item.id);
            if (currentIdx !== -1) {
              const rowsShift = Math.round(
                deltaY / (GOAL_ROW_HEIGHT + ROW_GAP),
              );
              let newIdx = currentIdx + rowsShift;
              newIdx = Math.max(0, Math.min(sortedGoals.length - 1, newIdx));

              if (newIdx !== currentIdx) {
                const reordered = [...sortedGoals];
                const [removed] = reordered.splice(currentIdx, 1);
                reordered.splice(newIdx, 0, removed);

                for (let i = 0; i < reordered.length; i++) {
                  const goal = reordered[i];
                  const newPosition = i + 1;

                  if (goal.id === item.id) {
                    const payload = {
                      name: goal.name?.trim() || "Цель",
                      position: newPosition,
                    };
                    if (hasHorizontalMovement) {
                      payload.start_date = newStartDate;
                      payload.deadline = newDeadline;
                    } else {
                      payload.start_date = goal.start_date;
                      payload.deadline = goal.deadline;
                    }
                    const response = await updateGoalApi(
                      goal.id,
                      payload,
                      token,
                    );
                    if (!response.ok) {
                      processError(response.status);
                      return;
                    }
                    handleGoalSaved(response.goal);
                  } else {
                    const payload = {
                      name: goal.name?.trim() || "Цель",
                      start_date: goal.start_date || null,
                      deadline: goal.deadline || null,
                      position: newPosition,
                    };
                    const response = await updateGoalApi(
                      goal.id,
                      payload,
                      token,
                    );
                    if (!response.ok) {
                      processError(response.status);
                      return;
                    }
                  }
                }

                setStreamsData((prev) =>
                  prev.map((s) =>
                    s.id === streamId
                      ? {
                          ...s,
                          goals: reordered.map((g, idx) => ({
                            ...g,
                            position: idx + 1,
                            start_date:
                              g.id === item.id && hasHorizontalMovement
                                ? newStartDate
                                : g.start_date,
                            deadline:
                              g.id === item.id && hasHorizontalMovement
                                ? newDeadline
                                : g.deadline,
                          })),
                        }
                      : s,
                  ),
                );
              } else if (hasHorizontalMovement) {
                const payload = {
                  name: item.name?.trim() || "Цель",
                  start_date: newStartDate,
                  deadline: newDeadline,
                };
                const resp = await updateGoalApi(item.id, payload, token);
                if (!resp.ok) {
                  processError(resp.status);
                  return;
                }
                handleGoalSaved(resp.goal);
              }
            }
          }
        } else if (hasHorizontalMovement) {
          await onUpGoal(item, deltaMs);
        }
      } else {
        if (currentDragging) {
          const { type, item, deltaMs } = currentDragging;
          const hasHorizontalMovement =
            Number.isFinite(deltaMs) && Math.abs(deltaMs) > 0;

          if (hasHorizontalMovement) {
            if (type === "task") await onUpTask(item, deltaMs);
            else if (type === "goal") await onUpGoal(item, deltaMs);
          }
        }

        if (currentVerticalDragging) {
          const { type, streamId, item, deltaY } = currentVerticalDragging;
          if (type === "goal") {
            await onUpVertical(streamId, item, deltaY);
          } else if (type === "task") {
            await onUpVerticalTask(streamId, item, deltaY);
          }
        }
      }
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [
    dragging,
    verticalDragging,
    timeline,
    streamsData,
    token,
    processError,
    handleTaskSaved,
    handleGoalSaved,
  ]);

  useEffect(() => {
    const onMove = (e) => {
      if (!resizing) return;
      const chartRect = chartAreaRef.current?.getBoundingClientRect();
      const x = e.clientX - chartRect.left + chartAreaRef.current.scrollLeft;
      const timestamp = xToTimestamp(x);
      setResizing((prev) => ({ ...prev, currentTs: timestamp }));
    };

    const onUpTask = async (item, edge, newTs) => {
      const payload = {
        name: item.name?.trim() || "",
        status_id: Number(item.status_id),
        priority_id: Number(item.priority_id),
        assignee_email: item.assignee_email || null,
        start_date:
          edge === "start" ? new Date(newTs).toISOString() : item.start_date,
        deadline:
          edge === "end" ? new Date(newTs).toISOString() : item.deadline,
      };
      const response = await updateTaskApi(item.id, payload, token);
      if (!response.ok) {
        processError(response.status);
        return;
      }
      handleTaskSaved(response.task);
    };

    const onUpGoal = async (item, edge, newTs) => {
      const payload = {
        name: item.name?.trim() || "Цель",
        start_date:
          edge === "start"
            ? new Date(newTs).toISOString()
            : item.start_date || null,
        deadline:
          edge === "end"
            ? new Date(newTs).toISOString()
            : item.deadline || null,
      };
      const response = await updateGoalApi(item.id, payload, token);
      if (!response.ok) {
        processError(response.status);
        return;
      }
      handleGoalSaved(response.goal);
    };

    const onUp = async () => {
      if (!resizing) return;
      const { type, item, edge } = resizing;
      const newTs = resizing.currentTs;
      setResizing(null);
      if (type === "task") await onUpTask(item, edge, newTs);
      else if (type === "goal") await onUpGoal(item, edge, newTs);
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [
    resizing,
    timeline,
    token,
    processError,
    handleTaskSaved,
    handleGoalSaved,
    xToTimestamp,
  ]);

  if (loading)
    return (
      <div>
        <CircularProgress size={32} />
      </div>
    );

  return (
    <div style={{ flex: 0.2, padding: 16 }}>
      <div
        ref={containerRef}
        style={{
          background: "#fff",
          border: "1px solid #EDEDED",
          borderRadius: 12,
          boxShadow: "0 2px 4px rgba(0,0,0,0.04)",
          overflow: "hidden",
          position: "relative",
        }}
      >
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "100%",
            display: "flex",
          }}
        >
          <GanttSidebar
            rows={sidebarRows}
            open={sidebarOpen}
            renderHeight={renderHeight}
            onDataChanged={handleSidebarDataChanged}
            onToggleSidebar={() => setSidebarOpen((isOpen) => !isOpen)}
            projectId={projId}
            teamId={teamId}
          />
          <div
            ref={chartAreaRef}
            style={{
              flex: 1,
              height: "100%",
              overflow: "auto",
              position: "relative",
            }}
          >
            {timeline && (
              <div
                style={{
                  position: "relative",
                  height: renderHeight,
                  width: useDataRange ? timeline.width : "100%",
                  minWidth: "100%",
                }}
              >
                <GanttTimelineHeader
                  timeline={timeline}
                  scaleType={scaleType}
                  onToggleSidebar={() => setSidebarOpen((isOpen) => !isOpen)}
                  onPrev={() => shiftRange(-1)}
                  onNext={() => shiftRange(1)}
                  onToday={goToday}
                  onScale={onScale}
                  useDataRange={useDataRange}
                />

                <GanttGrid timeline={timeline} />

                <CurrentTimeMarker xNow={xNow} timelineWidth={timeline.width} />

                <div
                  style={{
                    position: "absolute",
                    top: HEADER_HEIGHT,
                    left: 0,
                    width: useDataRange ? timeline.width : "100%",
                    bottom: 0,
                    cursor: resizing
                      ? "ew-resize"
                      : dragging
                        ? "move"
                        : undefined,
                  }}
                >
                  {(() => {
                    let currentTop = 0;
                    return streamsData.map((stream) => {
                      const allGoals = [...stream.goals].sort(
                        (a, b) => (a.position || 0) - (b.position || 0),
                      );
                      const allTasks = [...stream.tasks].sort(
                        (a, b) => (a.position || 0) - (b.position || 0),
                      );

                      const element = (
                        <GanttStream
                          key={stream.id}
                          streamId={stream.id}
                          streamName={stream.name}
                          goals={allGoals}
                          tasks={allTasks}
                          timeline={timeline}
                          baseTop={currentTop}
                          onContextMenuGoal={handleContextMenuGoal}
                          onContextMenuTask={handleContextMenuTask}
                          onStartResizeTask={(t, streamId) =>
                            handleStartResizeTask(t, streamId)
                          }
                          onEndResizeTask={(t, streamId) =>
                            handleResizeTaskDeadline(t, streamId)
                          }
                          onStartResizeGoal={(g, streamId) =>
                            handleStartResizeGoal(g, streamId)
                          }
                          onEndResizeGoal={(g, streamId) =>
                            handleEndResizeGoal(g, streamId)
                          }
                          resizingInfo={resizing}
                          onDragStartTask={handleDragStartTask}
                          onDragStartGoal={handleDragStartGoal}
                          draggingInfo={dragging}
                          verticalDraggingInfo={verticalDragging}
                          relationColorMap={relationColorMap}
                        />
                      );

                      const goalsHeight =
                        allGoals.length * (GOAL_ROW_HEIGHT + ROW_GAP);
                      const tasksHeight =
                        allTasks.length * (TASK_ROW_HEIGHT + ROW_GAP);
                      const streamHeight =
                        SEPARATOR_OFFSET +
                        LABEL_HEIGHT +
                        LABEL_MARGIN +
                        goalsHeight +
                        BETWEEN_GOALS_TASKS +
                        tasksHeight +
                        STREAM_BOTTOM_PADDING;
                      currentTop += streamHeight;
                      return element;
                    });
                  })()}
                </div>
              </div>
            )}
          </div>
        </div>

        <div
          style={{
            position: "absolute",
            right: 12,
            top: 12,
            zIndex: 60,
            display: "flex",
            gap: 8,
            alignItems: "center",
          }}
        >
          <Select
            value={scaleType}
            onChange={(e) => onScale(e.target.value)}
            size="small"
            sx={{
              padding: "2px 6px",
              background: "#fff",
              fontSize: 12,
              "& .MuiSelect-select": { padding: 0 },
            }}
            variant="outlined"
          >
            {/*<MenuItem value="day">День</MenuItem> TODO: оптимизировать*/}
            <MenuItem value="week">Неделя</MenuItem>
            <MenuItem value="two-weeks">2 недели</MenuItem>
            <MenuItem value="month">Месяц</MenuItem>
            <MenuItem value="quarter">Квартал</MenuItem>
            <MenuItem value="year">Год</MenuItem>
          </Select>

          <IconButton
            size="small"
            onClick={() => {
              scrollByVisible(-1);
            }}
            sx={{
              background: "#fff",
              padding: "4px",
              "&:hover": { background: "#f3f3f3" },
            }}
          >
            <ChevronLeftIcon fontSize="small" />
          </IconButton>

          <Button
            onClick={() => {
              goToday();
            }}
            size="small"
            variant="contained"
            sx={{
              background: "#fff",
              color: "#6b6b6b",
              padding: "4px 8px",
              fontSize: 12,
            }}
          >
            Сегодня
          </Button>

          <IconButton
            size="small"
            onClick={() => {
              scrollByVisible(1);
            }}
            sx={{
              background: "#fff",
              padding: "4px",
              "&:hover": { background: "#f3f3f3" },
            }}
          >
            <ChevronRightIcon fontSize="small" />
          </IconButton>
        </div>

        {!sidebarOpen && (
          <div>
            <div
              style={{ position: "absolute", left: 12, top: 12, zIndex: 60 }}
            >
              <IconButton
                size="small"
                onClick={() => setSidebarOpen(true)}
                sx={{
                  background: "#fff",
                  padding: "4px",
                  "&:hover": { background: "#f3f3f3" },
                }}
              >
                <ChevronRightIcon fontSize="small" />
              </IconButton>
            </div>

            <div
              style={{
                position: "absolute",
                left: 0,
                top: HEADER_HEIGHT,
                zIndex: 50,
                pointerEvents: "none",
              }}
            >
              {streamsData.map((stream, index) => {
                let streamTop = HEADER_HEIGHT;

                for (let i = 0; i < index; i++) {
                  const prevStream = streamsData[i];
                  const goalsHeight =
                    prevStream.goals.length * (GOAL_ROW_HEIGHT + ROW_GAP);
                  const tasksHeight =
                    prevStream.tasks.length * (TASK_ROW_HEIGHT + ROW_GAP);
                  const streamHeight =
                    SEPARATOR_OFFSET +
                    LABEL_HEIGHT +
                    LABEL_MARGIN +
                    goalsHeight +
                    BETWEEN_GOALS_TASKS +
                    tasksHeight +
                    STREAM_BOTTOM_PADDING;
                  streamTop += streamHeight;
                }

                return (
                  <div
                    key={stream.id}
                    style={{
                      position: "absolute",
                      left: 0,
                      top: streamTop - HEADER_HEIGHT + 1,
                      padding: "2px 8px",
                      borderRadius: 4,
                      fontSize: FONT_SIZE - 2,
                      fontWeight: 600,
                      color: "#8f8f8f",
                      whiteSpace: "nowrap",
                      maxWidth: 200,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      pointerEvents: "none",
                    }}
                  >
                    {stream.name}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {sidebarOpen && (
          <div
            style={{
              position: "absolute",
              left: 12,
              top: HEADER_HEIGHT,
              zIndex: 50,
              pointerEvents: "none",
            }}
          >
            {streamsData.map((stream, index) => {
              let streamTop = HEADER_HEIGHT;

              for (let i = 0; i < index; i++) {
                const prevStream = streamsData[i];
                const goalsHeight =
                  prevStream.goals.length * (GOAL_ROW_HEIGHT + ROW_GAP);
                const tasksHeight =
                  prevStream.tasks.length * (TASK_ROW_HEIGHT + ROW_GAP);
                const streamHeight =
                  SEPARATOR_OFFSET +
                  LABEL_HEIGHT +
                  LABEL_MARGIN +
                  goalsHeight +
                  BETWEEN_GOALS_TASKS +
                  tasksHeight +
                  STREAM_BOTTOM_PADDING;
                streamTop += streamHeight;
              }

              return (
                <div
                  key={stream.id}
                  style={{
                    position: "absolute",
                    left: SIDEBAR_WIDTH,
                    top: streamTop - HEADER_HEIGHT + 1,
                    padding: "2px 8px",
                    borderRadius: 4,
                    fontSize: FONT_SIZE - 2,
                    fontWeight: 600,
                    color: "#8f8f8f",
                    whiteSpace: "nowrap",
                    maxWidth: 200,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    pointerEvents: "none",
                  }}
                >
                  {stream.name}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <GoalForm
        open={goalFormOpen}
        onClose={() => setGoalFormOpen(false)}
        streamId={goalStreamId}
        goal={selectedGoal}
        onSaved={handleGoalSaved}
      />

      <TaskForm
        open={taskFormOpen}
        onClose={() => setTaskFormOpen(false)}
        streamId={taskStreamId}
        task={selectedTask}
        statuses={statuses}
        priorities={priorities}
        projectId={projId}
        teamId={teamId}
        onSaved={handleTaskSaved}
      />

      <Menu
        open={Boolean(contextMenu)}
        onClose={closeContextMenu}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
      >
        <MenuItem onClick={handleEditFromMenu}>Редактировать</MenuItem>
        <MenuItem onClick={handleDeleteFromMenu}>Удалить</MenuItem>
      </Menu>
    </div>
  );
};

export default GanttChart;
