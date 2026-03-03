import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Alert,
  CircularProgress,
  Tooltip,
} from "@mui/material";
import {
  Delete as DeleteIcon,
  Add as AddIcon,
  NotificationsActive as NotificationIcon,
} from "@mui/icons-material";
import {
  getTaskRemindersApi,
  createReminderApi,
  deleteReminderApi,
} from "../../api/reminder.js";
import { usePushNotifications } from "../../hooks/usePushNotifications.js";
import { toInputDate, toLocaleDateWithTimeHM } from "../../utils/datetime.js";

function localToUtcIso(dateStr, timeStr) {
  const combined = `${dateStr}T${timeStr || "00:00"}`;
  const date = new Date(combined);
  return date.toISOString();
}

const RemindersSection = ({ taskId, token }) => {
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [reminderDate, setReminderDate] = useState("");
  const [reminderTime, setReminderTime] = useState("");
  const [saving, setSaving] = useState(false);
  const [localError, setLocalError] = useState(null);

  const {
    isSupported,
    permission,
    error: pushError,
    requestPermissionAndSubscribe,
  } = usePushNotifications();

  useEffect(() => {
    if (!taskId) return;
    setLoading(true);
    getTaskRemindersApi(taskId, token)
      .then((res) => {
        if (res.ok) setReminders(res.reminders);
      })
      .finally(() => setLoading(false));
  }, [taskId, token]);

  const handleAdd = async () => {
    const remindAt = localToUtcIso(reminderDate, reminderTime);
    if (!remindAt) return;

    if (new Date(remindAt) <= new Date()) {
      setLocalError("Дата напоминания должна быть в будущем");
      return;
    }

    if (permission !== "granted") {
      const granted = await requestPermissionAndSubscribe();
      if (!granted) return;
    }

    setSaving(true);
    setLocalError(null);
    const res = await createReminderApi(taskId, remindAt, token);
    setSaving(false);

    if (res.ok) {
      setReminders((prev) => [...prev, res.reminder]);
      setReminderDate("");
      setReminderTime("");
    } else {
      setLocalError("Не удалось создать напоминание");
    }
  };

  const handleDelete = async (id) => {
    const res = await deleteReminderApi(id, token);
    if (res.ok) {
      setReminders((prev) => prev.filter((r) => r.id !== id));
    }
  };

  const displayError = localError || pushError;

  return (
    <Box sx={{ px: 1.5, py: 1 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
        <NotificationIcon fontSize="small" color="action" />
        <Typography
          sx={{
            color: "text.secondary",
            fontFamily: '"Montserrat", sans-serif',
            fontWeight: 700,
          }}
        >
          Напоминания
        </Typography>
      </Box>

      {!isSupported && (
        <Alert severity="warning" sx={{ mb: 1 }}>
          Ваш браузер не поддерживает push-уведомления
        </Alert>
      )}

      {displayError && (
        <Alert
          severity="error"
          sx={{ mb: 1 }}
          onClose={() => setLocalError(null)}
        >
          {displayError}
        </Alert>
      )}

      {permission === "denied" && (
        <Alert severity="warning" sx={{ mb: 1 }}>
          Уведомления заблокированы в настройках браузера. Разрешите их вручную.
        </Alert>
      )}

      {loading ? (
        <CircularProgress size={20} sx={{ my: 1 }} />
      ) : reminders.length > 0 ? (
        <List dense sx={{ mb: 1 }}>
          {reminders.map((r) => (
            <ListItem
              key={r.id}
              sx={{
                border: "1px solid #e0e0e0",
                borderRadius: 1,
                mb: 0.5,
                bgcolor: r.sent ? "#f5f5f5" : "#f0f7ff",
              }}
              secondaryAction={
                !r.sent && (
                  <IconButton
                    edge="end"
                    size="small"
                    onClick={() => handleDelete(r.id)}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                )
              }
            >
              <ListItemText
                primary={toLocaleDateWithTimeHM(r.remind_at.replace("Z", ""))}
                secondary={r.sent ? "Отправлено" : null}
                slotProps={{
                  primary: { variant: "body2" },
                  secondary: { variant: "caption", color: "text.secondary" },
                }}
              />
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Напоминаний нет
        </Typography>
      )}

      {isSupported && permission !== "denied" && (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          <Typography variant="body2" fontWeight={600}>
            Добавить напоминание
          </Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField
              type="date"
              value={reminderDate}
              onChange={(e) => setReminderDate(e.target.value)}
              size="small"
              fullWidth
              slotProps={{
                htmlInput: { min: toInputDate(new Date().toISOString()) },
              }}
            />
            <TextField
              type="time"
              value={reminderTime}
              onChange={(e) => setReminderTime(e.target.value)}
              size="small"
              sx={{ minWidth: 130 }}
            />
          </Box>
          <Tooltip title="">
            <span>
              <Button
                variant="outlined"
                startIcon={
                  saving ? <CircularProgress size={16} /> : <AddIcon />
                }
                onClick={handleAdd}
                disabled={!reminderDate || saving}
                fullWidth
              >
                {permission !== "granted" ? "Разрешить и добавить" : "Добавить"}
              </Button>
            </span>
          </Tooltip>
        </Box>
      )}
    </Box>
  );
};

export default RemindersSection;
