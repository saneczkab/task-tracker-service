import React, { useEffect, useMemo, useState } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button, Box } from "@mui/material";
import { useNavigate } from "react-router-dom";
import FormRow from "./FormRow.jsx";
import { toInputDate, toInputTime, toISOStringOrNull } from "../../utils/datetime.js";

const GoalForm = ({ open, onClose, streamId, goal = null, onSaved }) => {
    const navigate = useNavigate();
    const token = useMemo(() => window.localStorage.getItem("auth_token") || "", []);

    const [name, setName] = useState("");
    const [deadlineDate, setDeadlineDate] = useState("");
    const [deadlineTime, setDeadlineTime] = useState("");

    const isEdit = Boolean(goal?.id);

    useEffect(() => {
        if (!open) {
            return;
        }

        setName(goal?.name || "");
        setDeadlineDate(goal?.deadline ? toInputDate(goal.deadline) : "");
        setDeadlineTime(goal?.deadline ? toInputTime(goal.deadline) : "");
    }, [open, goal]);

    const handleSubmit = async () => {
        try {
            const finalName = name.trim() || "Новая цель";
            const payload = { name: finalName };

            if ((deadlineDate || "").trim() !== "") {
                const iso = toISOStringOrNull(deadlineDate, deadlineTime);
                if (iso) {
                    payload.deadline = iso;
                }
            }

            const url = isEdit ? `/api/goal/${goal.id}` : `/api/stream/${streamId}/goal/new`;
            const method = isEdit ? "PATCH" : "POST";

            const res = await fetch(url, {
                method,
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
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
            <DialogTitle>{isEdit ? "Редактировать цель" : "Добавить цель"}</DialogTitle>
            <DialogContent dividers>
                <Box
                    component="form"
                    onSubmit={(e) => {
                        e.preventDefault();
                        handleSubmit();
                    }}
                    sx={{ display: "grid", gap: 1 }}
                >
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

                    <FormRow label="Дедлайн">
                        <div style={{ display: "flex", gap: 4 }}>
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
                <Button variant="contained" color="primary" onClick={handleSubmit}>
                    {isEdit ? "Сохранить" : "Создать"}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default GoalForm;
