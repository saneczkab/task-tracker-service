import React, { useEffect, useMemo, useState } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button, FormControl, Select,
    MenuItem, Box, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import FormRow from "./FormRow.jsx";

const Row = ({ label, children }) => (
    <Box
        sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", sm: "220px 1fr" },
            alignItems: "center",
            gap: 2,
            px: 1.5,
            py: 1,
            borderRadius: 1,

            "&:hover": { backgroundColor: "#EDEDED" },

            "& .MuiOutlinedInput-root .MuiOutlinedInput-notchedOutline": {
                borderColor: "transparent"
            },
            "& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline": {
                borderColor: "transparent"
            },
            "& .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline": {
                borderColor: "transparent"
            }
        }}
    >
        <Typography
            sx={{
                color: "text.secondary",
                fontFamily: '"Roboto Flex","Roboto",sans-serif',
                fontWeight: 700
            }}
        >{label}
        </Typography>
        <Box>{children}</Box>
    </Box>
);

const TaskForm = ({ open, onClose, streamId, task = null, onSaved,
                      statuses: statusesProp, priorities: prioritiesProp }) => {
    const navigate = useNavigate();
    const token = useMemo(() => window.localStorage.getItem("auth_token") || "", []);

    const [statuses, setStatuses] = useState(statusesProp || []);
    const [priorities, setPriorities] = useState(prioritiesProp || []);

    const [name, setName] = useState("");
    const [assigneeEmail, setAssigneeEmail] = useState("");
    const [statusId, setStatusId] = useState("");
    const [priorityId, setPriorityId] = useState("");

    const [startDate, setStartDate] = useState("");
    const [startTime, setStartTime] = useState("");
    const [deadlineDate, setDeadlineDate] = useState("");
    const [deadlineTime, setDeadlineTime] = useState("");

    const isEdit = Boolean(task?.id);

    const toInputDate = (value) => {
        if (!value) {
            return "";
        }

        const datetime = new Date(value);
        return `${datetime.getFullYear()}-${String(datetime.getMonth() + 1).padStart(2, "0")}-${String(datetime.getDate()).padStart(2, "0")}`;
    };

    const toInputTime = (value) => {
        if (!value) {
            return "";
        }

        const datetime = new Date(value);
        return `${String(datetime.getHours()).padStart(2, "0")}:${String(datetime.getMinutes()).padStart(2, "0")}`;
    };

    const toISOStringOrNull = (dateStr, timeStr) => {
        if (!dateStr) {
            return null;
        }

        const combined = `${dateStr}T${timeStr || "00:00"}`;
        const date = new Date(combined);
        return Number.isNaN(date.getTime()) ? null : date.toISOString();
    };

    useEffect(() => {
        if (!open) {
            return;
        }

        setName(task?.name || "");
        setAssigneeEmail(task?.assignee_email || "");
        setStatusId(task?.status_id ?? "");
        setPriorityId(task?.priority_id ?? "");
        setStartDate(task?.start_date ? toInputDate(task.start_date) : "");
        setStartTime(task?.start_date ? toInputTime(task.start_date) : "");
        setDeadlineDate(task?.deadline ? toInputDate(task.deadline) : "");
        setDeadlineTime(task?.deadline ? toInputTime(task.deadline) : "");
    }, [open, task]);

    useEffect(() => {
        if (open) {
            loadRefs();
        }
    }, [open]);

    const loadRefs = async () => {
        if (statusesProp && prioritiesProp) {
            return;
        }

        try {
            if (!statusesProp) {
                const response = await fetch(`/api/taskStatuses`,{
                    method: "GET",
                    headers: {
                        "Accept": "application/json",
                    }
                });

                if (!response.ok){
                    // TODO
                    return;
                }

                const data = await response.json();
                setStatuses(data || []);
            } else {
                setStatuses(statusesProp);
            }

            if (!prioritiesProp) {
                const response = await fetch(`/api/priorities`, {
                    method: "GET",
                    headers: {
                        Accept: "application/json"
                    }
                });

                if (!response.ok) {
                    // TODO
                    return;
                }

                const data = await response.json();
                setPriorities(data || []);
            } else {
                setPriorities(prioritiesProp);
            }
        } catch {
            // TODO
        }
    };

    const handleSubmit = async ()=> {
        try {
            const payload = {
                name: name.trim(),
                status_id: Number(statusId) || null,
                priority_id: Number(priorityId) || null,
                assignee_email: assigneeEmail?.trim() || null,
                start_date: toISOStringOrNull(startDate, startTime),
                deadline: toISOStringOrNull(deadlineDate, deadlineTime)
            };

            const url = isEdit ? `/api/task/${task.id}` : `/api/stream/${streamId}/task/new`;
            const method = isEdit ? "PATCH" : "POST";

            const res = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                    Authorization: token
                },
                body: JSON.stringify(payload)
            });

            if (res.status === 404) {
                navigate("/error/404");
                return;
            }

            if (!res.ok) {
                // TODO
                return;
            }

            const saved = await res.json();
            onSaved?.(saved);
            onClose?.();
        } catch {
            // TODO
        }
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle>{isEdit ? "Редактировать задачу" : "Добавить задачу"}</DialogTitle>
            <DialogContent dividers>
                <Box component="form" onSubmit={handleSubmit} sx={{ display: "grid", gap: 1 }}>
                    <FormRow label="Название">
                        <TextField
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            variant="outlined"
                            size="small"
                            fullWidth
                            placeholder="Введите название"
                            required
                        />
                    </FormRow>

                    <FormRow label="Исполнитель (email)">
                        <TextField
                            value={assigneeEmail}
                            onChange={(e) => setAssigneeEmail(e.target.value)}
                            type="email"
                            variant="outlined"
                            size="small"
                            fullWidth
                            placeholder="user@example.com"
                        />
                    </FormRow>

                    <FormRow label="Статус">
                        <FormControl fullWidth size="small">
                            <Select
                                value={statusId === "" ? "" : Number(statusId)}
                                onChange={(e) => setStatusId(e.target.value)}
                            >
                                {(statuses || []).map((s) => (
                                    <MenuItem key={s.id} value={s.id}>
                                        {s.name}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </FormRow>

                    <FormRow label="Приоритет">
                        <FormControl fullWidth size="small">
                            <Select
                                value={priorityId === "" ? "" : Number(priorityId)}
                                onChange={(e) => setPriorityId(e.target.value)}
                            >
                                {(priorities || []).map((p) => (
                                    <MenuItem key={p.id} value={p.id}>
                                        {p.name}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </FormRow>

                    <FormRow label="Дата начала">
                        <div style={{ display: "flex", gap: 1 }}>
                            <TextField
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                size="small"
                                fullWidth
                            />
                            <TextField
                                type="time"
                                value={startTime}
                                onChange={(e) => setStartTime(e.target.value)}
                                size="small"
                                sx={{ minWidth: 140 }}
                            />
                        </div>
                    </FormRow>

                    <FormRow label="Дедлайн">
                        <div style={{ display: "flex", gap: 1 }}>
                            <TextField
                                type="date"
                                value={deadlineDate}
                                onChange={(e) => setDeadlineDate(e.target.value)}
                                size="small"
                                fullWidth
                            />
                            <TextField
                                type="time"
                                value={deadlineTime}
                                onChange={(e) => setDeadlineTime(e.target.value)}
                                size="small"
                                sx={{ minWidth: 140 }}
                            />
                        </div>
                    </FormRow>
                </Box>
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose}>Отмена</Button>
                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSubmit}
                    >
                    {isEdit ? "Сохранить" : "Создать"}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default TaskForm;
