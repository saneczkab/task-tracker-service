import React, { useEffect, useMemo, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import KanbanElement from "./KanbanElement.jsx";
import TaskForm from "./TaskForm.jsx";
import StreamLayout from "../layout/StreamLayout.jsx";

import { useProcessError } from "../../hooks/useProcessError.js";
import { fetchTasksApi, updateTaskApi, deleteTaskApi } from "../../api/task.js";
import { fetchStatusesApi, fetchPrioritiesApi } from "../../api/meta.js";

const KanbanBoard = () => {
  const { teamId, streamId } = useParams();

  const [tasks, setTasks] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [projId, setProjId] = useState(null);

  const [formOpen, setFormOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();

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
    const response = await deleteTaskApi(task.id, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setTasks((prev) => (prev || []).filter((t) => t.id !== task.id));
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

  const loadAll = useCallback(async () => {
    setLoading(true);

    const [tasksData, statusesData, prioritiesData] = await Promise.all([
      fetchTasks(),
      fetchStatuses(),
      fetchPriorities(),
    ]);

    setTasks(tasksData || []);
    setStatuses(statusesData);
    setPriorities(prioritiesData);

    setLoading(false);
  }, [streamId, token]);

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
          </StreamLayout>
        </div>
      </div>
    </div>
  );
};

export default KanbanBoard;
