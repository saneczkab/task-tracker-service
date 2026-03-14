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

      const sorted = [...response.history].sort(
        (a, b) => new Date(b.changed_at) - new Date(a.changed_at),
      );
      setHistory(sorted);
      setLoading(false);
    };

    load();
  }, [open, task?.id, token]);

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
        ) : history.length === 0 ? (
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
          history.map((entry) => (
            <Box
              key={entry.id}
              sx={{
                borderBottom: "1px solid #e0e0e0",
                px: 3,
                py: 2,
                "&:last-child": { borderBottom: "none" },
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  gap: 1.5,
                  alignItems: "center",
                  mb: 1,
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
                  {toLocaleDateWithTimeHM(entry.changed_at)}
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
                  {entry.changed_by_email}
                </Typography>
              </Box>

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
                  ->
                </Typography>

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
              </Box>
            </Box>
          ))
        )}
      </DialogContent>
    </Dialog>
  );
};

export default TaskHistory;
