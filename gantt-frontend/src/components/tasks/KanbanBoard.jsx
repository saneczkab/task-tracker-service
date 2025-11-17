import React, { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import Topbar from "../ui/Topbar.jsx";
import Sidebar from "../ui/Sidebar.jsx";
import KanbanElement from "./KanbanElement.jsx";
import TaskForm from "./TaskForm.jsx";

const KanbanBoard = () => {
    const { teamId, streamId } = useParams();
    const navigate = useNavigate();

    const token = useMemo(
        () => window.localStorage.getItem("auth_token") || "",
        []
    );

    const [streamName, setStreamName] = useState("");
    const [tasks, setTasks] = useState([]);
    const [statuses, setStatuses] = useState([]);
    const [priorities, setPriorities] = useState([]);
    const [loading, setLoading] = useState(true);

    const [formOpen, setFormOpen] = useState(false);
    const [selectedTask, setSelectedTask] = useState(null);

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
        try {
            const response = await fetch(`/api/task/${task.id}`, {
                method: "DELETE",
                headers: {
                    Accept: "application/json",
                    Authorization: token
                }
            });

            if (!response.ok) {
                // TODO
                return;
            }

            setTasks((prev) => (prev || []).filter((t) => t.id !== task.id));
        } catch {
            // TODO
        }
    };

    const fetchStream = async () => {
        try {
            const res = await fetch(`/api/stream/${streamId}`, {
                method: "GET",
                headers: {
                    Accept: "application/json",
                    Authorization: token
                }
            });

            if (res.status === 404) {
                navigate("/error/404");
                return;
            }

            if (!res.ok) {
                // TODO
                return;
            }

            return await res.json();
        } catch {
            // TODO
        }
    };

    const fetchTasks = async () => {
        try {
            const res = await fetch(`/api/stream/${streamId}/tasks`, {
                method: "GET",
                headers: {
                    Accept: "application/json",
                    Authorization: token
                }
            });

            if (res.status === 404) {
                navigate("/error/404");
                return [];
            }

            if (!res.ok) {
                // TODO
                return;
            }

            return await res.json();
        } catch {
            // TODO
        }
    };

    const fetchStatuses = async () => {
        try {
            const res = await fetch(`/api/taskStatuses`, {
                method: "GET",
                headers: {
                    Accept: "application/json"
                }
            });

            if (!res.ok) {
                // TODO
                return;
            }

            return await res.json();
        } catch {
            // TODO
        }
    };

    const fetchPriorities = async () => {
        try {
            const res = await fetch(`/api/priorities`, {
                method: "GET",
                headers: {
                    Accept: "application/json"
                }
            });

            if (!res.ok) {
                // TODO
                return;
            }

            return await res.json();
        } catch {
            // TODO
        }
    };

    const loadAll = async () => {
        setLoading(true);

        try {
            const [stream, tasksData, statusesData, prioritiesData] =
                await Promise.all([
                    fetchStream(),
                    fetchTasks(),
                    fetchStatuses(),
                    fetchPriorities()
                ]);

            if (stream) {
                setStreamName(stream.name);
            }

            setTasks(tasksData || []);
            setStatuses(statusesData);
            setPriorities(prioritiesData);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAll();
    }, [streamId]);

    const handleDragOver = (event) => {
        event.preventDefault();
    };

    const handleDrop = async (event, targetStatusId) => {
        event.preventDefault();
        const idStr = event.dataTransfer.getData("text/plain");
        const taskId = Number(idStr);
        const currentTask = tasks.find(t => t.id === taskId);

        try {
            const res = await fetch(`/api/task/${taskId}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                    Authorization: token
                },
                body: JSON.stringify({
                    status_id: Number(targetStatusId),
                    assignee_email: currentTask.assignee_email,
                    start_date: currentTask.start_date,
                    deadline: currentTask.deadline
                })
            });

            if (res.status === 404) {
                navigate("/error/404");
                return;
            }

            if (!res.ok) {
                // TODO
                return;
            }

            const updated = await res.json();

            setTasks((prev) =>
                (prev || []).map((t) =>
                    t.id === updated.id ? { ...t, ...updated } : t
                )
            );
        } catch {
            // TODO
        }
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
                    <h1 className="font-bold text-xl mb-4">
                        Стрим {streamName}
                    </h1>

                    <Box sx={{ display: "flex", gap: 2, alignItems: "flex-start", overflowX: "auto" }}>
                        {(statuses || []).map((status) => (
                            <div
                                key={status.id}
                                onDragOver={handleDragOver}
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
