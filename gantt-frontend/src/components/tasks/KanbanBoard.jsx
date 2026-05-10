import React, { useEffect, useMemo, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import KanbanElement from "./KanbanElement.jsx";
import TaskForm from "./TaskForm.jsx";
import TaskHistory from "./TaskHistory.jsx";
import ExportTasksButton from "../ui/ExportTasksButton.jsx";
import StreamLayout from "../layout/StreamLayout.jsx";

import { useProcessError } from "../../hooks/useProcessError.js";
import { useConfirmDelete } from "../../context/ConfirmDeleteDialogContext.jsx";
import { fetchTasksApi, updateTaskApi, deleteTaskApi } from "../../api/task.js";
import { fetchStatusesApi, fetchPrioritiesApi } from "../../api/meta.js";
import { fetchTeamTagsApi } from "../../api/tag.js";
import { fetchTeamCustomFieldsApi } from "../../api/customField.js";

const KanbanBoard = () => {
  const { teamId, streamId } = useParams();

  const [tasks, setTasks] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [tags, setTags] = useState([]);
  const [customFields, setCustomFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [projId, setProjId] = useState(null);

  const [formOpen, setFormOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);

  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyTask, setHistoryTask] = useState(null);

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();
  const { confirm } = useConfirmDelete();

  const priorityMap = useMemo(() => {
    const map = {};
    (priorities || []).forEach((p) => {
      map[p.id] = p.name;
    });
    return map;
  }, [priorities]);

  const handleAddTask = (statusId = null) => {
    setSelectedTask({ status_id: statusId });
    setFormOpen(true);
  };

  const handleEditTask = (task) => {
    setSelectedTask(task);
    setFormOpen(true);
  };

  const handleTaskSaved = (saved) => {
    setFormOpen(false);
    setTasks((prev) => {
      const idx = prev.findIndex((t) => t.id === saved.id);
      if (idx === -1) {
        return [...prev, saved];
      }

      const copy = [...prev];
      copy[idx] = saved;
      return copy;
    });
    setSelectedTask(null);
  };

  const handleTaskDelete = async (task) => {
    if (!(await confirm(`задачу "${task.name}"`))) return;

    const response = await deleteTaskApi(task.id, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setTasks((prev) => (prev || []).filter((t) => t.id !== task.id));
  };

  const handleTaskHistory = (task) => {
    setHistoryTask(task);
    setHistoryOpen(true);
  };

  const fetchTasks = async () => {
    const response = await fetchTasksApi(streamId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    return response.tasks;
  };

  const fetchStatuses = async () => {
    const response = await fetchStatusesApi();

    if (!response.ok) {
      processError(response.status);
      return;
    }

    return response.statuses;
  };

  const fetchPriorities = async () => {
    const response = await fetchPrioritiesApi();

    if (!response.ok) {
      processError(response.status);
      return;
    }

    return response.priorities;
  };

  const fetchTags = async () => {
    if (!teamId) return [];
    const response = await fetchTeamTagsApi(teamId, token);

    if (!response.ok) {
      processError(response.status);
      return [];
    }

    return response.tags || [];
  };

  const fetchCustomFields = async () => {
    if (!teamId) return [];
    const response = await fetchTeamCustomFieldsApi(teamId, token);

    if (!response.ok) {
      processError(response.status);
      return [];
    }

    return response.fields || [];
  };

  const loadAll = useCallback(async () => {
    setLoading(true);

    const [
      tasksData,
      statusesData,
      prioritiesData,
      tagsData,
      customFieldsData,
    ] = await Promise.all([
      fetchTasks(),
      fetchStatuses(),
      fetchPriorities(),
      fetchTags(),
      fetchCustomFields(),
    ]);

    setTasks(tasksData || []);
    setStatuses(statusesData);
    setPriorities(prioritiesData);
    setTags(tagsData || []);
    setCustomFields(customFieldsData || []);

    setLoading(false);
  }, [streamId, token, teamId]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const handleDrop = async (event, targetStatusId) => {
    event.preventDefault();
    const idStr = event.dataTransfer.getData("text/plain");
    const taskId = Number(idStr);
    const currentTask = tasks.find((t) => t.id === taskId);
    const payload = {
      status_id: Number(targetStatusId),
      assignee_email: currentTask.assignee_email,
      start_date: currentTask.start_date,
      deadline: currentTask.deadline,
    };

    const response = await updateTaskApi(taskId, payload, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    const updated = response.task;
    setTasks((prev) =>
      (prev || []).map((t) => (t.id === updated.id ? { ...t, ...updated } : t)),
    );
  };

  const handleTaskReorder = async (
    draggedId,
    targetTask,
    targetStatusId,
    insertAfter = false,
  ) => {
    if (!draggedId || draggedId === targetTask.id) return;

    const draggedTask = tasks.find((t) => t.id === draggedId);
    if (!draggedTask) return;

    const targetCol = (tasks || [])
      .filter(
        (t) =>
          (t.status_id ?? null) === (targetStatusId ?? null) &&
          t.id !== draggedId,
      )
      .sort((a, b) => (a.kanban_position ?? 0) - (b.kanban_position ?? 0));

    const targetIdx = targetCol.findIndex((t) => t.id === targetTask.id);
    if (targetIdx === -1) return;

    const insertIdx = insertAfter ? targetIdx + 1 : targetIdx;

    const reordered = [...targetCol];
    reordered.splice(insertIdx, 0, draggedTask);

    const updates = reordered.map((t, idx) => ({
      id: t.id,
      kanban_position: idx + 1,
      status_id: targetStatusId ?? null,
    }));

    for (const u of updates) {
      const cur = tasks.find((t) => t.id === u.id);
      if (!cur) continue;

      const payload = {};
      if ((cur.kanban_position ?? 0) !== u.kanban_position) {
        payload.kanban_position = u.kanban_position;
      }
      if ((cur.status_id ?? null) !== u.status_id) {
        payload.status_id = u.status_id;
      }

      if (Object.keys(payload).length === 0) continue;

      const response = await updateTaskApi(u.id, payload, token);
      if (!response.ok) {
        processError(response.status);
        return;
      }
    }

    setTasks((prev) =>
      (prev || []).map((t) => {
        const u = updates.find((x) => x.id === t.id);
        if (!u) return t;
        return {
          ...t,
          kanban_position: u.kanban_position,
          status_id: u.status_id,
        };
      }),
    );
  };

  if (loading) {
    return (
      <div>
        <StreamLayout
          teamId={teamId}
          streamId={streamId}
          onProjIdLoaded={setProjId}
        >
          <Box className="flex items-center justify-center h-full">
            <CircularProgress size={32} />
          </Box>
        </StreamLayout>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F6F7]">
      <div className="flex flex-1 gap-4">
        <div className="flex flex-1">
          <StreamLayout
            teamId={teamId}
            streamId={streamId}
            onProjIdLoaded={setProjId}
          >
            <div className="mb-4">
              <ExportTasksButton />
            </div>

            <Box
              sx={{
                display: "flex",
                gap: 2,
                alignItems: "flex-start",
                overflowX: "auto",
              }}
            >
              {(statuses || []).map((status) => (
                <div
                  key={status.id}
                  onDragOver={(event) => {
                    event.preventDefault();
                  }}
                  onDrop={(e) => handleDrop(e, status.id)}
                >
                  <KanbanElement
                    title={status.name}
                    statusId={status.id}
                    tasks={tasks}
                    priorityMap={priorityMap}
                    onTaskEdit={handleEditTask}
                    onAddTask={handleAddTask}
                    onTaskDelete={handleTaskDelete}
                    onTaskHistory={handleTaskHistory}
                    onTaskReorder={handleTaskReorder}
                  />
                </div>
              ))}
            </Box>

            <TaskForm
              open={formOpen}
              onClose={() => {
                setFormOpen(false);
                setSelectedTask(null);
              }}
              streamId={streamId}
              task={selectedTask}
              statuses={statuses}
              priorities={priorities}
              projectId={projId}
              teamId={teamId}
              onSaved={handleTaskSaved}
            />

            <TaskHistory
              open={historyOpen}
              onClose={() => setHistoryOpen(false)}
              task={historyTask}
              statuses={statuses}
              priorities={priorities}
              tags={tags}
              customFields={customFields}
            />
          </StreamLayout>
        </div>
      </div>
    </div>
  );
};

export default KanbanBoard;
