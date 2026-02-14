import React, { useEffect, useMemo, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
} from "@mui/material";
import FormRow from "./FormRow.jsx";
import {
  toInputDate,
  toInputTime,
  toISOStringOrNull,
} from "../../utils/datetime.js";

import { useProcessError } from "../../hooks/useProcessError.js";
import { createGoalApi, updateGoalApi } from "../../api/goal.js";

const GoalForm = ({ open, onClose, streamId, goal = null, onSaved }) => {
  const [name, setName] = useState("");
  const [deadlineDate, setDeadlineDate] = useState("");
  const [deadlineTime, setDeadlineTime] = useState("");
  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("");

  const isEdit = Boolean(goal?.id);

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();

  useEffect(() => {
    if (!open) {
      return;
    }

    setName(goal?.name || "");
    setDeadlineDate(goal?.deadline ? toInputDate(goal.deadline) : "");
    setDeadlineTime(goal?.deadline ? toInputTime(goal.deadline) : "");
    setStartDate(goal?.start_date ? toInputDate(goal.start_date) : "");
    setStartTime(goal?.start_date ? toInputTime(goal.start_date) : "");
  }, [open, goal]);

  const handleSubmit = async () => {
    const finalName = name.trim() || "Новая цель";
    const payload = { name: finalName };

    if ((deadlineDate || "").trim() !== "") {
      const iso = toISOStringOrNull(deadlineDate, deadlineTime);
      if (iso) {
        payload.deadline = iso;
      }
    }

    if ((startDate || "").trim() !== "") {
      const isoStart = toISOStringOrNull(startDate, startTime);
      if (isoStart) {
        payload.start_date = isoStart;
      }
    }

    const response = isEdit
      ? await updateGoalApi(goal.id, payload, token)
      : await createGoalApi(payload, streamId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    onSaved?.(response.goal);
    onClose?.();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>
        {isEdit ? "Редактировать цель" : "Добавить цель"}
      </DialogTitle>
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

          <FormRow label="Дата начала">
            <div style={{ display: "flex", gap: 4 }}>
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
