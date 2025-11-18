import React, { useEffect, useMemo, useState } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button, FormControl, Select,
    MenuItem, Box } from "@mui/material";
import FormRow from "./FormRow.jsx";
import { toInputDate, toInputTime, toISOStringOrNull } from "../../utils/datetime.js";

import { useProcessError } from "../../hooks/useProcessError.js";
import { createTaskApi, updateTaskApi } from "../../api/task.js";

const TaskForm = ({ open, onClose, streamId, task = null, onSaved,
                      statuses: statusesProp, priorities: prioritiesProp }) => {
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
    const token = useMemo(() => window.localStorage.getItem("auth_token") || "", []);
    const processError = useProcessError();

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
            loadMeta();
        }
    }, [open]);

    const loadMeta = async () => {
        setStatuses(statusesProp);
        setPriorities(prioritiesProp);
    };

    const handleSubmit = async (e)=> {
        e.preventDefault();

        const payload = {
          name: name.trim(),
          status_id: Number(statusId) || null,
          priority_id: Number(priorityId) || null,
          assignee_email: assigneeEmail?.trim() || null,
          start_date: toISOStringOrNull(startDate, startTime),
          deadline: toISOStringOrNull(deadlineDate, deadlineTime)
        };

        const response = isEdit
          ? await updateTaskApi(task.id, payload, token)
          : await createTaskApi(payload, streamId, token);

        if (!response.ok) {
          processError(response.status);
          return;
        }

        const savedTask = response.task;
        onSaved?.(savedTask);
        onClose?.();
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
