import React, { useEffect, useMemo, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Typography,
  Box,
  CircularProgress,
  Chip,
} from "@mui/material";
import { Close as CloseIcon } from "@mui/icons-material";
import { fetchTaskHistoryApi } from "../../api/task.js";
import { useProcessError } from "../../hooks/useProcessError.js";
import { toLocaleDateWithTimeHM } from "../../utils/datetime.js";
import { getContrastColor } from "../../utils/taskUtils.js";
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

function safeJsonParse(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === "object") return value;
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  try {
    return JSON.parse(trimmed);
  } catch {
    return null;
  }
}

function pickCustomFieldRawValue(valueObj) {
  if (!valueObj || typeof valueObj !== "object") return null;
  const candidates = [
    valueObj.value_string,
    valueObj.value_text,
    valueObj.value_date,
    valueObj.value_datetime,
    valueObj.value_bool,
  ];
  const found = candidates.find(
    (v) => v !== null && v !== undefined && v !== "",
  );
  return found === undefined ? null : found;
}

function formatCustomFieldValue(valueObj) {
  const raw = pickCustomFieldRawValue(valueObj);
  if (raw === null || raw === undefined || raw === "") return "-";

  if (typeof raw === "boolean") return raw ? "Да" : "Нет";

  if (typeof raw === "string") {
    const dateRegex = /^\d{4}-\d{2}-\d{2}([\sT]\d{2}:\d{2})?/;
    if (dateRegex.test(raw)) {
      return toLocaleDateWithTimeHM(raw) || raw;
    }
  }

  return String(raw);
}

function expandCustomFieldsHistoryEntry(entry, customFields = []) {
  const oldObj = safeJsonParse(entry.old_value) || {};
  const newObj = safeJsonParse(entry.new_value) || {};

  const ids = new Set([
    ...Object.keys(oldObj || {}),
    ...Object.keys(newObj || {}),
  ]);

  const expanded = [];
  for (const idStr of ids) {
    const oldValObj = oldObj?.[idStr] ?? null;
    const newValObj = newObj?.[idStr] ?? null;

    const oldFmt = formatCustomFieldValue(oldValObj);
    const newFmt = formatCustomFieldValue(newValObj);
    if (oldFmt === newFmt) continue;

    const idNum = Number(idStr);
    const def = (customFields || []).find(
      (f) =>
        String(f.id) === String(idStr) ||
        (Number.isFinite(idNum) && f.id === idNum),
    );
    const label = def?.name || `Поле #${idStr}`;

    expanded.push({
      ...entry,
      id: `${entry.id}-cf-${idStr}`,
      field_name: `custom_field:${idStr}`,
      custom_field_id: idNum,
      custom_field_name: label,
      old_value: oldValObj,
      new_value: newValObj,
    });
  }

  return expanded;
}

function formatValue(value, fieldName, statuses, priorities, tags) {
  if (value === null || value === undefined || value === "") return "-";

  if (fieldName === "status_id") {
    const s = statuses.find((x) => String(x.id) === String(value));
    return s ? s.name : value;
  }
  if (fieldName === "priority_id") {
    const p = priorities.find((x) => String(x.id) === String(value));
    return p ? p.name : value;
  }
  if (fieldName === "tag_ids") {
    try {
      const tagIds = typeof value === "string" ? JSON.parse(value) : value;
      if (!Array.isArray(tagIds) || tagIds.length === 0) return "-";
      return tagIds
        .map((id) => {
          const tag = tags?.find((t) => String(t.id) === String(id));
          return tag ? tag.name : `ID: ${id}`;
        })
        .join(", ");
    } catch {
      return value;
    }
  }

  const dateRegex = /^\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}/;
  if (dateRegex.test(value)) {
    return toLocaleDateWithTimeHM(value) || value;
  }

  return value;
}

function parseTagIds(value) {
  try {
    return typeof value === "string" ? JSON.parse(value) : value;
  } catch {
    return [];
  }
}

function getAddedAndRemovedTags(oldValue, newValue, tags) {
  const oldIds = parseTagIds(oldValue);
  const newIds = parseTagIds(newValue);

  const removed = oldIds
    .filter((id) => !newIds.includes(id))
    .map((id) => tags?.find((t) => String(t.id) === String(id)))
    .filter(Boolean);

  const added = newIds
    .filter((id) => !oldIds.includes(id))
    .map((id) => tags?.find((t) => String(t.id) === String(id)))
    .filter(Boolean);

  return {
    removed: removed.length > 0 ? removed : null,
    added: added.length > 0 ? added : null,
  };
}

const TaskHistory = ({
  open,
  onClose,
  task,
  statuses = [],
  priorities = [],
  tags = [],
  customFields = [],
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

      const expandedHistory = (response.history || []).flatMap((entry) => {
        if (entry.field_name === "custom_fields") {
          return expandCustomFieldsHistoryEntry(entry, customFields);
        }
        return [entry];
      });

      const filtered = expandedHistory.filter((entry) => {
        if (entry.field_name?.startsWith("custom_field:")) {
          const oldFmt = formatCustomFieldValue(entry.old_value);
          const newFmt = formatCustomFieldValue(entry.new_value);
          return oldFmt !== newFmt;
        }

        if (!entry.old_value && !entry.new_value) return false;

        if (
          entry.field_name === "start_date" ||
          entry.field_name === "deadline"
        ) {
          const oldTime = entry.old_value
            ? new Date(entry.old_value).getTime()
            : null;
          const newTime = entry.new_value
            ? new Date(entry.new_value).getTime()
            : null;
          if (oldTime === newTime) return false;
        }

        const oldVal = formatValue(
          entry.old_value,
          entry.field_name,
          statuses,
          priorities,
        );
        const newVal = formatValue(
          entry.new_value,
          entry.field_name,
          statuses,
          priorities,
        );

        return oldVal !== newVal && entry.old_value !== entry.new_value;
      });

      const sorted = [...filtered].sort(
        (a, b) => new Date(b.changed_at) - new Date(a.changed_at),
      );
      setHistory(sorted);
      setLoading(false);
    };

    load();
  }, [open, task?.id, token, statuses, priorities, tags, customFields]);

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
                    {entry.field_name?.startsWith("custom_field:")
                      ? entry.custom_field_name ||
                        `Поле #${String(entry.field_name).split(":")[1]}`
                      : FIELD_LABELS[entry.field_name] || entry.field_name}
                  </Typography>

                  {entry.field_name === "tag_ids" ? (
                    (() => {
                      const { removed, added } = getAddedAndRemovedTags(
                        entry.old_value,
                        entry.new_value,
                        tags,
                      );
                      return (
                        <Box
                          sx={{
                            display: "flex",
                            flexDirection: "column",
                            gap: 1,
                          }}
                        >
                          {removed && removed.length > 0 && (
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1,
                              }}
                            >
                              <Typography
                                variant="body2"
                                sx={{
                                  fontFamily: "Montserrat, sans-serif",
                                  minWidth: "fit-content",
                                }}
                              >
                                Удалено:
                              </Typography>
                              <Box
                                sx={{
                                  display: "flex",
                                  flexWrap: "wrap",
                                  gap: 0.5,
                                }}
                              >
                                {removed.map((tag) => (
                                  <Chip
                                    key={tag.id}
                                    size="small"
                                    label={tag.name}
                                    sx={{
                                      fontSize: "0.7rem",
                                      backgroundColor: tag.color,
                                      color: getContrastColor(tag.color),
                                      fontWeight: 600,
                                      opacity: 0.6,
                                      textDecoration: "line-through",
                                    }}
                                  />
                                ))}
                              </Box>
                            </Box>
                          )}
                          {added && added.length > 0 && (
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1,
                              }}
                            >
                              <Typography
                                variant="body2"
                                sx={{
                                  fontFamily: "Montserrat, sans-serif",
                                  minWidth: "fit-content",
                                }}
                              >
                                Добавлено:
                              </Typography>
                              <Box
                                sx={{
                                  display: "flex",
                                  flexWrap: "wrap",
                                  gap: 0.5,
                                }}
                              >
                                {added.map((tag) => (
                                  <Chip
                                    key={tag.id}
                                    size="small"
                                    label={tag.name}
                                    sx={{
                                      fontSize: "0.7rem",
                                      backgroundColor: tag.color,
                                      color: getContrastColor(tag.color),
                                      fontWeight: 600,
                                    }}
                                  />
                                ))}
                              </Box>
                            </Box>
                          )}
                        </Box>
                      );
                    })()
                  ) : entry.field_name?.startsWith("custom_field:") ? (
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        flexWrap: "wrap",
                      }}
                    >
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
                        {formatCustomFieldValue(entry.old_value)}
                      </Typography>

                      <Typography
                        variant="body2"
                        sx={{
                          color: "text.secondary",
                          fontFamily: "Montserrat, sans-serif",
                        }}
                      >
                        ➡️
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
                        {formatCustomFieldValue(entry.new_value)}
                      </Typography>
                    </Box>
                  ) : (
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
                            <StatusBadge
                              statusName={formatValue(
                                entry.old_value,
                                entry.field_name,
                                statuses,
                                priorities,
                              )}
                            />
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
                              tags,
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
                        <StatusBadge
                          statusName={formatValue(
                            entry.new_value,
                            entry.field_name,
                            statuses,
                            priorities,
                          )}
                        />
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
                            tags,
                          )}
                        </Typography>
                      )}
                    </Box>
                  )}
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
