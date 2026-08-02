import React, { useMemo, useState } from "react";
import { Box, Paper, Typography, IconButton } from "@mui/material";
import TaskCard from "./TaskCard.jsx";
import { Add as AddIcon } from "@mui/icons-material";
import { getStatusColors } from "../ui/StatusBadge.jsx";

const KanbanElement = ({
  title,
  statusId,
  tasks = [],
  priorityMap,
  onTaskEdit,
  onTaskOpen,
  onAddTask,
  onTaskDelete,
  onTaskHistory,
  onTaskReorder,
}) => {
  const columnTasks = useMemo(() => {
    const target = statusId ?? null;
    return (tasks || [])
      .filter((t) => (t?.status_id ?? null) === target)
      .sort((a, b) => (a?.kanban_position ?? 0) - (b?.kanban_position ?? 0));
  }, [tasks, statusId]);

  const [dragOverTaskId, setDragOverTaskId] = useState(null);

  // TODO: хранить цвета в бд
  const bgColor = useMemo(() => {
    return getStatusColors(title).bg;
  }, [title]);

  const handleCardDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleCardDragEnter = (e, taskId) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverTaskId(taskId);
  };

  const handleCardDrop = (e, targetTask) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverTaskId(null);
    const draggedId = Number(e.dataTransfer.getData("text/plain"));
    if (!draggedId || draggedId === targetTask.id) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const insertAfter = e.clientY > rect.top + rect.height / 2;
    if (onTaskReorder) {
      onTaskReorder(draggedId, targetTask, statusId, insertAfter);
    }
  };

  const handleCardDragLeave = (e, taskId) => {
    if (dragOverTaskId === taskId) {
      const related = e.relatedTarget;
      if (related && e.currentTarget.contains(related)) return;
      setDragOverTaskId(null);
    }
  };

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
            <Box
              key={task.id}
              onDragOver={handleCardDragOver}
              onDragEnter={(e) => handleCardDragEnter(e, task.id)}
              onDragLeave={(e) => handleCardDragLeave(e, task.id)}
              onDrop={(e) => handleCardDrop(e, task)}
              sx={{
                borderRadius: 2,
                outline:
                  dragOverTaskId === task.id ? "2px solid #3A7AFE" : "none",
                transition: "outline 0.1s ease",
              }}
            >
              <TaskCard
                task={task}
                priorityMap={priorityMap}
                onOpen={onTaskOpen}
                onEdit={onTaskEdit}
                onDelete={onTaskDelete}
                onHistory={onTaskHistory}
              />
            </Box>
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
