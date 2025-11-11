import React, { useEffect, useMemo, useState } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button, Box, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

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

const GoalForm = ({ open, onClose, streamId, goal = null, onSaved }) => {
    const navigate = useNavigate();
    const token = useMemo(() => window.localStorage.getItem("auth_token") || "", []);

    const [name, setName] = useState("");
    const [deadlineDate, setDeadlineDate] = useState("");
    const [deadlineTime, setDeadlineTime] = useState("");

    const isEdit = Boolean(goal?.id);

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
                    <Row label="Название">
                        <TextField
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            variant="outlined"
                            size="small"
                            fullWidth
                            placeholder="Введите название"
                            required
                        />
                    </Row>

                    <Row label="Дедлайн">
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
                    </Row>
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
