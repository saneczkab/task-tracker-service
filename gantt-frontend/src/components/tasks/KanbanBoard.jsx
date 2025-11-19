import React, { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import Topbar from "../ui/Topbar.jsx";
import Sidebar from "../ui/Sidebar.jsx";
import KanbanElement from "./KanbanElement.jsx";
import TaskForm from "./TaskForm.jsx";

import { useProcessError } from "../../hooks/useProcessError.js";
import { fetchTasksApi, updateTaskApi, deleteTaskApi } from "../../api/task.js";
import { fetchStreamApi } from "../../api/stream.js";
import { fetchStatusesApi, fetchPrioritiesApi } from "../../api/meta.js";

const KanbanBoard = () => {
  const { teamId, streamId } = useParams();

  const [streamName, setStreamName] = useState("");
  const [tasks, setTasks] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);

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

  const handleAddTask = () => {
    setSelectedTask(null);
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

  const fetchStream = async () => {
    const response = await fetchStreamApi(streamId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    return response.stream;
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

  const loadAll = async () => {
    setLoading(true);

    const [stream, tasksData, statusesData, prioritiesData] = await Promise.all(
      [fetchStream(), fetchTasks(), fetchStatuses(), fetchPriorities()],
    );

    if (stream) {
      setStreamName(stream.name);
    }

    setTasks(tasksData || []);
    setStatuses(statusesData);
    setPriorities(prioritiesData);

    setLoading(false);
  };

  useEffect(() => {
    loadAll();
  }, [streamId]);

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
      <Box className="min-h-screen flex flex-col bg-white">
        <Topbar />
        <Box className="flex flex-1">
          <Sidebar teamId={teamId} />
          <Box className="flex-1 p-6 flex items-center justify-center">
            <CircularProgress size={32} />
          </Box>
        </Box>
      </Box>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-white">
      <Topbar />
      <div className="flex flex-1">
        <Sidebar teamId={teamId} />
        <main className="flex-1 p-6">
          <h1 className="font-bold text-xl mb-4">Стрим {streamName}</h1>

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
            onSaved={handleTaskSaved}
          />
        </main>
      </div>
    </div>
  );
};

export default KanbanBoard;
