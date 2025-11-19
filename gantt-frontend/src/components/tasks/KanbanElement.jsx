import React, { useMemo } from "react";
import { Box, Paper, Typography, IconButton } from "@mui/material";
import TaskCard from "./TaskCard.jsx";
import { Add as AddIcon } from "@mui/icons-material";

const KanbanElement = ({
  title,
  statusId,
  tasks = [],
  priorityMap,
  onTaskEdit,
  onAddTask,
  onTaskDelete,
}) => {
  const columnTasks = useMemo(() => {
    const target = statusId ?? null;
    return (tasks || []).filter((t) => (t?.status_id ?? null) === target);
  }, [tasks, statusId]);

  // TODO: хранить цвета в бд
  const bgColor = useMemo(() => {
    if (title === "To do") return "#ffebee";
    if (title === "Doing") return "#fff9c4";
    if (title === "Done") return "#e8f5e9";
    return "#e3f2fd";
  }, [title]);

  return (
    <Paper
      elevation={0}
      sx={{
        p: 1.5,
        borderRadius: 2,
        border: "1px solid #ededed",
        backgroundColor: bgColor,
        minWidth: 280,
        maxWidth: 360,
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
          {title}
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <Typography variant="caption" sx={{ color: "text.secondary" }}>
            {columnTasks.length}
          </Typography>
          {onAddTask && (
            <IconButton
              size="small"
              onClick={() => onAddTask(statusId)}
              sx={{ p: 0.5 }}
            >
              <AddIcon fontSize="small" />
            </IconButton>
          )}
        </Box>
      </Box>

      <Box sx={{ display: "grid", gap: 1, pr: 0.5 }}>
        {columnTasks.length > 0 ? (
          columnTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              priorityMap={priorityMap}
              onEdit={onTaskEdit}
              onDelete={onTaskDelete}
            />
          ))
        ) : (
          <Typography
            variant="caption"
            sx={{ color: "text.secondary", textAlign: "center", py: 2 }}
          >
            Нет задач
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default KanbanElement;
