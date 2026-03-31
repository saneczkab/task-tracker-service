import React, { useEffect, useMemo, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Typography,
  Box,
  CircularProgress,
} from "@mui/material";
import { Close as CloseIcon } from "@mui/icons-material";
import { fetchTaskHistoryApi } from "../../api/task.js";
import { useProcessError } from "../../hooks/useProcessError.js";
import { toLocaleDateWithTimeHM } from "../../utils/datetime.js";
import StatusBadge from "../ui/StatusBadge.jsx";

const FIELD_LABELS = {
  name: "Название",
  description: "Описание",
  status_id: "Статус",
  priority_id: "Приоритет",
  assignee_email: "Исполнитель",
  start_date: "Дата начала",
  deadline: "Дедлайн",
  position: "Позиция",
  tag_ids: "Теги",
};

function formatValue(value, fieldName, statuses, priorities) {
  if (value === null || value === undefined || value === "") return "-";

  if (fieldName === "status_id") {
    const s = statuses.find((x) => String(x.id) === String(value));
    return s ? s.name : value;
  }
  if (fieldName === "priority_id") {
    const p = priorities.find((x) => String(x.id) === String(value));
    return p ? p.name : value;
  }

  const dateRegex = /^\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}/;
  if (dateRegex.test(value)) {
    return toLocaleDateWithTimeHM(value) || value;
  }

  return value;
}

const TaskHistory = ({
  open,
  onClose,
  task,
  statuses = [],
  priorities = [],
}) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();

  useEffect(() => {
    if (!open || !task?.id) return;

    const load = async () => {
      setLoading(true);
      const response = await fetchTaskHistoryApi(task.id, token);
      if (!response.ok) {
        processError(response.status);
        setLoading(false);
        return;
      }

      const filtered = response.history.filter((entry) => {
        if (!entry.old_value && !entry.new_value) return false;

        if (entry.field_name === "start_date" || entry.field_name === "deadline") {
          const oldTime = entry.old_value ? new Date(entry.old_value).getTime() : null;
          const newTime = entry.new_value ? new Date(entry.new_value).getTime() : null;
          if (oldTime === newTime) return false;
        }

        const oldVal = formatValue(entry.old_value, entry.field_name, statuses, priorities);
        const newVal = formatValue(entry.new_value, entry.field_name, statuses, priorities);
        
        return oldVal !== newVal && entry.old_value !== entry.new_value;
      });

      const sorted = [...filtered].sort(
        (a, b) => new Date(b.changed_at) - new Date(a.changed_at),
      );
      setHistory(sorted);
      setLoading(false);
    };

    load();
  }, [open, task?.id, token, statuses, priorities]);

  const groupedHistory = useMemo(() => {
    const groups = [];
    history.forEach((entry) => {
      const lastGroup = groups[groups.length - 1];
      if (
        lastGroup &&
        lastGroup.changed_at === entry.changed_at &&
        lastGroup.changed_by_email === entry.changed_by_email
      ) {
        lastGroup.entries.push(entry);
      } else {
        groups.push({
          id: entry.id,
          changed_at: entry.changed_at,
          changed_by_email: entry.changed_by_email,
          entries: [entry],
        });
      }
    });
    return groups;
  }, [history]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      slotProps={{
        paper: { sx: { borderRadius: 3, maxHeight: "80vh" } },
      }}
    >
      <DialogTitle
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          pb: 1,
          fontFamily: "Montserrat, sans-serif",
          fontWeight: 700,
        }}
      >
        История изменений: {task?.name}
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers sx={{ overflowY: "auto", p: 0 }}>
        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
            <CircularProgress size={32} />
          </Box>
        ) : groupedHistory.length === 0 ? (
          <Box sx={{ py: 4, px: 3, textAlign: "center" }}>
            <Typography
              variant="body2"
              sx={{
                color: "text.secondary",
                fontFamily: "Montserrat, sans-serif",
              }}
            >
              История изменений пуста
            </Typography>
          </Box>
        ) : (
          groupedHistory.map((group) => (
            <Box
              key={group.id}
              sx={{
                border: "1px solid #e0e0e0",
                borderRadius: 2,
                backgroundColor: "#ffffff",
                m: 2,
                p: 2,
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  gap: 1.5,
                  alignItems: "center",
                  mb: 1.5,
                  flexWrap: "wrap",
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: "text.secondary",
                    fontFamily: "Montserrat, sans-serif",
                  }}
                >
                  {toLocaleDateWithTimeHM(group.changed_at)}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    color: "text.secondary",
                    fontFamily: "Montserrat, sans-serif",
                  }}
                >
                  ·
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    fontWeight: 600,
                    fontFamily: "Montserrat, sans-serif",
                    color: "text.primary",
                  }}
                >
                  {group.changed_by_email}
                </Typography>
              </Box>

              {group.entries.map((entry) => (
                <Box key={entry.id} sx={{ mb: 1.5, "&:last-child": { mb: 0 } }}>
                  <Typography
                    variant="subtitle2"
                    sx={{
                      fontWeight: 700,
                      fontFamily: "Montserrat, sans-serif",
                      mb: 0.75,
                      color: "text.primary",
                    }}
                  >
                    {FIELD_LABELS[entry.field_name] || entry.field_name}
                  </Typography>

                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      flexWrap: "wrap",
                    }}
                  >
                    {entry.old_value ? (
                      entry.field_name === "status_id" ? (
                        <Box sx={{ opacity: 0.6 }}>
                          <StatusBadge statusName={formatValue(entry.old_value, entry.field_name, statuses, priorities)} />
                        </Box>
                      ) : (
                        <Typography
                          variant="body2"
                          sx={{
                            textDecoration: "line-through",
                            color: "text.secondary",
                            fontFamily: "Montserrat, sans-serif",
                            maxWidth: 180,
                            wordBreak: "break-word",
                          }}
                        >
                          {formatValue(
                            entry.old_value,
                            entry.field_name,
                            statuses,
                            priorities,
                          )}
                        </Typography>
                      )
                    ) : (
                      <Typography
                        variant="body2"
                        sx={{
                          textDecoration: "line-through",
                          color: "text.secondary",
                          fontFamily: "Montserrat, sans-serif",
                        }}
                      >
                        -
                      </Typography>
                    )}

                    <Typography
                      variant="body2"
                      sx={{
                        color: "text.secondary",
                        fontFamily: "Montserrat, sans-serif",
                      }}
                    >
                      ➡️
                    </Typography>

                    {entry.field_name === "status_id" ? (
                      <StatusBadge statusName={formatValue(entry.new_value, entry.field_name, statuses, priorities)} />
                    ) : (
                      <Typography
                        variant="body2"
                        sx={{
                          color: "text.primary",
                          fontWeight: 500,
                          fontFamily: "Montserrat, sans-serif",
                          maxWidth: 180,
                          wordBreak: "break-word",
                        }}
                      >
                        {formatValue(
                          entry.new_value,
                          entry.field_name,
                          statuses,
                          priorities,
                        )}
                      </Typography>
                    )}
                  </Box>
                </Box>
              ))}
            </Box>
          ))
        )}
      </DialogContent>
    </Dialog>
  );
};

export default TaskHistory;
