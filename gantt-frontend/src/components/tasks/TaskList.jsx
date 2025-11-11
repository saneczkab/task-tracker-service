import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { CircularProgress, Table, TableHead, TableRow, TableCell, TableBody, TableContainer, Paper, IconButton,
    Button, Menu, MenuItem } from "@mui/material";
import { MoreVert as MoreVertIcon }
    from '@mui/icons-material';
import TaskForm from "./TaskForm.jsx";

const TaskList = ({ streamId }) => {
    const navigate = useNavigate();

    const [tasks, setTasks] = useState([]);
    const [statuses, setStatuses] = useState([]);
    const [priorities, setPriorities] = useState([]);
    const [loading, setLoading] = useState(true);

    const [menuAnchorEl, setMenuAnchorEl] = useState(null);
    const [menuTaskId, setMenuTaskId] = useState(null);

    const [formOpen, setFormOpen] = useState(false);
    const [selectedTask, setSelectedTask] = useState(null);

    const token = useMemo(() => window.localStorage.getItem("auth_token") || "", []);

    const openMenu = (event, id) => {
        setMenuAnchorEl(event.currentTarget);
        setMenuTaskId(id);
    };

    const handleCreate = () => {
        setSelectedTask(null);
        setFormOpen(true);
    };

    const handleEdit = () => {
        const t = (tasks || []).find(x => x.id === menuTaskId);
        setSelectedTask(t || null);
        setFormOpen(true);
        closeMenu();
    };

    const handleDelete = async () => {
        try {
            const response = await fetch(`/api/task/${menuTaskId}`, {
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

            await loadAll();
        } catch {
            // TODO
        } finally {
            closeMenu();
        }
    };

    const statusMap = useMemo(() => {
        const map = {};
        (statuses || []).forEach((s) => (map[s.id] = s.name));
        return map;
    }, [statuses]);

    const priorityMap = useMemo(() => {
        const map = {};
        (priorities || []).forEach((p) => (map[p.id] = p.name));
        return map;
    }, [priorities]);

    const fetchTasks = async () => {
        const response = await fetch(`/api/stream/${streamId}/tasks`, {
            method: "GET",
            headers: {
                Accept: "application/json",
                Authorization: token
            }
        });

        if (response.status === 404) {
            navigate("/error/404");
            return [];
        }

        if (!response.ok) {
            // TODO
            return [];
        }

        return await response.json();
    };

    const fetchStatuses = async () => {
        const response = await fetch(`/api/taskStatuses`, {
            method: "GET",
            headers: {
                Accept: "application/json"
            }
        });

        if (!response.ok) {
            return [];
            // TODO
        }

        return await response.json();
    };

    const fetchPriorities = async () => {
        const response = await fetch(`/api/priorities`, {
            method: "GET",
            headers: {
                Accept: "application/json"
            }
        });
        if (!response.ok) {
            return [];
            // TODO
        }

        return await response.json();
    };

    const loadAll = async () => {
        setLoading(true);

        try {
            const tasks = await fetchTasks();
            const statuses = await fetchStatuses();
            const priorities = await fetchPriorities();

            setTasks(tasks || []);
            setStatuses(statuses || []);
            setPriorities(priorities || []);
        } catch {
            // TODO
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAll();
    }, [streamId]);

    const closeMenu = () => {
        setMenuAnchorEl(null);
        setMenuTaskId(null);
    };

    if (loading) {
        return <CircularProgress size={32} />;
    }

    return (
        <>
            {
                tasks.length > 0 ? (
                    <div>
                        <TableContainer component={Paper} sx={{ borderRadius: 2, overflow: "hidden" }}>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell
                                            sx={{
                                                backgroundColor: "#EDEDED",
                                                fontWeight: "bold",
                                                // borderRight: "1px solid rgba(0,0,0,0.12)"
                                            }}
                                        >Название
                                        </TableCell>

                                        <TableCell
                                            sx={{
                                                backgroundColor: "#EDEDED",
                                                fontWeight: "bold",
                                                // borderRight: "1px solid rgba(0,0,0,0.12)"
                                            }}
                                        >Исполнитель
                                        </TableCell>

                                        <TableCell
                                            sx={{
                                                backgroundColor: "#EDEDED",
                                                fontWeight: "bold",
                                                // borderRight: "1px solid rgba(0,0,0,0.12)"
                                            }}
                                        >Статус
                                        </TableCell>

                                        <TableCell
                                            sx={{
                                                backgroundColor: "#EDEDED",
                                                fontWeight: "bold",
                                                // borderRight: "1px solid rgba(0,0,0,0.12)"
                                            }}
                                        >Приоритет
                                        </TableCell>

                                        <TableCell
                                            sx={{
                                                backgroundColor: "#EDEDED",
                                                fontWeight: "bold",
                                                // borderRight: "1px solid rgba(0,0,0,0.12)"
                                            }}
                                        >Дата начала
                                        </TableCell>

                                        <TableCell
                                            sx={{
                                                backgroundColor: "#EDEDED",
                                                fontWeight: "bold",
                                                // borderRight: "1px solid rgba(0,0,0,0.12)"
                                            }}
                                        >Дедлайн
                                        </TableCell>
                                    </TableRow>
                                </TableHead>

                                <TableBody>
                                    {(tasks || []).map((task) => (
                                        <TableRow
                                            key={task.id}
                                            sx={{
                                                "&:hover": { backgroundColor: "#fafafa" },
                                                "& .task-actions": { opacity: 0, transition: "opacity 0.2s" },
                                                "&:hover .task-actions": { opacity: 1 },
                                            }}
                                        >
                                            <TableCell
                                                // sx={{ borderRight: "1px solid rgba(0,0,0,0.12)" }}
                                            >
                                                {task.name}
                                            </TableCell>

                                            <TableCell
                                                // sx={{ borderRight: "1px solid rgba(0,0,0,0.12)" }}
                                            >
                                                {task.assignee_email || "-"}
                                            </TableCell>

                                            <TableCell
                                                // sx={{ borderRight: "1px solid rgba(0,0,0,0.12)" }}
                                            >
                                                {task.status_id ? statusMap[task.status_id] : "-"}
                                            </TableCell>

                                            <TableCell
                                                // sx={{ borderRight: "1px solid rgba(0,0,0,0.12)" }}
                                            >
                                                {task.priority_id ? priorityMap[task.priority_id] : "-"}
                                            </TableCell>

                                            <TableCell
                                                // sx={{ borderRight: "1px solid rgba(0,0,0,0.12)" }}
                                            >
                                                {task.start_date ? new Date(task.start_date).toLocaleString() : "-"}
                                            </TableCell>

                                            <TableCell
                                                sx={{
                                                    // borderRight: "1px solid rgba(0,0,0,0.12)",
                                                    position: "relative",
                                                    pr: 5
                                                }}
                                            >
                                                {task.deadline ? new Date(task.deadline).toLocaleString() : "-"}

                                                <IconButton
                                                    size="small"
                                                    onClick={(e) => openMenu(e, task.id)}
                                                    className="task-actions"
                                                    sx={{
                                                        position: "absolute",
                                                        right: 8,
                                                        top: "50%",
                                                        transform: "translateY(-50%)"
                                                    }}
                                                >
                                                    <MoreVertIcon fontSize="small" />
                                                </IconButton>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>

                        <Menu
                            anchorEl={menuAnchorEl}
                            open={Boolean(menuAnchorEl)}
                            onClose={closeMenu}
                            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
                            transformOrigin={{ vertical: "top", horizontal: "right" }}
                        >
                            <MenuItem
                                onClick={handleEdit}
                            >Редактировать
                            </MenuItem>

                            <MenuItem
                                onClick={handleDelete}
                            >Удалить
                            </MenuItem>
                        </Menu>

                        <div style={{ marginTop: 8, display: "flex" }}>
                            <Button
                                variant="text"
                                size="small"
                                onClick={handleCreate}
                            >
                                Добавить задачу
                            </Button>
                        </div>
                    </div>
                ) : (
                    <div>
                        Задачи не заданы. Создайте задачу!
                        <div style={{ marginTop: 8, display: "flex" }}>
                            <Button
                                variant="text"
                                size="small"
                                onClick={handleCreate}
                            >Добавить задачу
                            </Button>
                        </div>
                    </div>
                )
            }

            <TaskForm
                open={formOpen}
                onClose={() => setFormOpen(false)}
                streamId={streamId}
                task={selectedTask}
                statuses={statuses}
                priorities={priorities}
                onSaved={() => {
                    setFormOpen(false);
                    loadAll();
                }}
            />
        </>
    );
}

export default TaskList;
