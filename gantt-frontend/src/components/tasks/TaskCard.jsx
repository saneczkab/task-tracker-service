import React, { useMemo, useState } from "react";
import {
  Paper,
  Typography,
  Chip,
  Box,
  IconButton,
  Menu,
  MenuItem,
} from "@mui/material";
import { MoreVert as MoreVertIcon } from "@mui/icons-material";
import { formatDatetime } from "../../utils/datetime.js";

const TaskCard = ({ task, priorityMap, onEdit, onDelete }) => {
  const { name, assignee_email, deadline, priority_id } = task || {};

  const [menuAnchor, setMenuAnchor] = useState(null);
  const menuOpen = Boolean(menuAnchor);

  const priorityLabel = useMemo(() => {
    if (!priority_id) {
      return "-";
    }

    return priorityMap?.[priority_id];
  }, [priority_id, priorityMap]);

  const deadlineLabel = useMemo(() => {
    return deadline ? formatDatetime(deadline) : "-";
  }, [deadline]);

  const assigneeLabel = useMemo(() => {
    return assignee_email || "-";
  }, [assignee_email]);

  const handleDragStart = (e) => {
    e.dataTransfer.setData("text/plain", String(task.id));
  };

  // TODO: хранить цвета в бд
  const priorityColor = useMemo(() => {
    const label = priorityLabel.toLowerCase();
    if (label === "low") return "#4caf50";
    if (label === "medium") return "#ffeb3b";
    if (label === "high") return "#ff9800";
    if (label === "highest") return "#f44336";
    return "white";
  }, [priorityLabel]);

  return (
    <Paper
      draggable
      onDragStart={handleDragStart}
      sx={{
        p: 1.5,
        borderRadius: 2,
        border: "1px solid #ededed",
        display: "grid",
        gap: 0.5,
        cursor: "grab",
        position: "relative",
        "&:hover": { boxShadow: 3 },
        "&:active": { cursor: "grabbing" },
      }}
    >
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
        }}
      >
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          {name}
        </Typography>

        {onEdit && (
          <>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                setMenuAnchor(e.currentTarget);
              }}
              sx={{ p: 0.25 }}
            >
              <MoreVertIcon fontSize="small" />
            </IconButton>
            <Menu
              anchorEl={menuAnchor}
              open={menuOpen}
              onClose={() => setMenuAnchor(null)}
              onClick={(e) => e.stopPropagation()}
            >
              {onEdit && (
                <MenuItem
                  onClick={() => {
                    onEdit(task);
                    setMenuAnchor(null);
                  }}
                >
                  Изменить
                </MenuItem>
              )}

              <MenuItem
                onClick={() => {
                  onDelete(task);
                  setMenuAnchor(null);
                }}
              >
                Удалить
              </MenuItem>
            </Menu>
          </>
        )}
      </Box>

      {priorityLabel !== "No priority" && (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 0.5 }}>
          <Chip
            size="small"
            label={priorityLabel}
            sx={{
              fontSize: "0.7rem",
              backgroundColor: priorityColor,
              color: "white",
              fontWeight: 600,
            }}
          />
        </Box>
      )}

      <Typography variant="caption" sx={{ color: "text.secondary" }}>
        Дедлайн: {deadlineLabel}
      </Typography>

      <Typography variant="caption" sx={{ color: "text.secondary" }}>
        Исполнитель: {assigneeLabel}
      </Typography>
    </Paper>
  );
};

export default TaskCard;
