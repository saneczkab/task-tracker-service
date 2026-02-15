import React, { useEffect, useMemo, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  Select,
  MenuItem,
  Box,
  Typography,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Autocomplete,
  CircularProgress,
} from "@mui/material";
import { Delete as DeleteIcon, Add as AddIcon } from "@mui/icons-material";
import FormRow from "./FormRow.jsx";
import {
  toInputDate,
  toInputTime,
  toISOStringOrNull,
} from "../../utils/datetime.js";

import { useProcessError } from "../../hooks/useProcessError.js";
import {
  createTaskApi,
  updateTaskApi,
  getProjectTasksApi,
  createTaskRelationApi,
  deleteTaskRelationApi,
} from "../../api/task.js";
import { fetchConnectionTypesApi } from "../../api/meta.js";

const TaskForm = ({
  open,
  onClose,
  streamId,
  task = null,
  onSaved,
  onBeforeCreate,
  statuses: statusesProp,
  priorities: prioritiesProp,
  projectId = null,
  teamId = null,
}) => {
  const [statuses, setStatuses] = useState(statusesProp || []);
  const [priorities, setPriorities] = useState(prioritiesProp || []);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [assigneeEmail, setAssigneeEmail] = useState("");
  const [statusId, setStatusId] = useState("");
  const [priorityId, setPriorityId] = useState("");
  const [position, setPosition] = useState(null);

  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [deadlineDate, setDeadlineDate] = useState("");
  const [deadlineTime, setDeadlineTime] = useState("");

  const [relations, setRelations] = useState([]);
  const [connectionTypes, setConnectionTypes] = useState([]);
  const [projectTasks, setProjectTasks] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [selectedConnectionType, setSelectedConnectionType] = useState("");
  const [searchDebounceTimer, setSearchDebounceTimer] = useState(null);

  const isEdit = Boolean(task?.id);
  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();

  useEffect(() => {
    if (!open) {
      if (searchDebounceTimer) {
        clearTimeout(searchDebounceTimer);
        setSearchDebounceTimer(null);
      }
      return;
    }

    setName(task?.name || "");
    setDescription(task?.description || "");
    setAssigneeEmail(task?.assignee_email || "");
    setStatusId(task?.status_id ?? "");
    setPriorityId(task?.priority_id ?? "");
    setPosition(task?.position ?? null);
    setStartDate(task?.start_date ? toInputDate(task.start_date) : "");
    setStartTime(task?.start_date ? toInputTime(task.start_date) : "");
    setDeadlineDate(task?.deadline ? toInputDate(task.deadline) : "");
    setDeadlineTime(task?.deadline ? toInputTime(task.deadline) : "");
    setRelations(task?.relations || []);
    setSearchQuery("");
    setSearchResults([]);
    setSelectedTask(null);
    setSelectedConnectionType("");

    return () => {
      if (searchDebounceTimer) {
        clearTimeout(searchDebounceTimer);
      }
    };
  }, [open, task]);

  useEffect(() => {
    if (open) {
      loadMeta();
    }
  }, [open]);

  const loadMeta = async () => {
    setStatuses(statusesProp);
    setPriorities(prioritiesProp);

    const connResponse = await fetchConnectionTypesApi();
    if (connResponse.ok) {
      const russianConnectionTypes = [
        { id: 1, name: "Блокирующая" },
        { id: 2, name: "Дублирующая" },
        { id: 3, name: "Связь" },
      ];
      setConnectionTypes(russianConnectionTypes);
    }

    if (projectId) {
      const tasksResponse = await getProjectTasksApi(projectId, token);
      if (tasksResponse.ok) {
        setProjectTasks(tasksResponse.tasks);
      }
    }
  };

  const getTaskNameById = (taskId) => {
    const foundTask = projectTasks.find((t) => t.id === taskId);
    return foundTask?.name || `Задача ${taskId}`;
    // TODO: разобраться c can't access property "name", foundTask is undefined
    // `Задача ${taskId}` убирает ошибку, но при этом название всегда отображается корректно - не как `Задача ${taskId}`
  };

  const formatRelationText = (relation) => {
    const currentTaskName = task.name;
    const currentTaskId = task.id;
    const relatedTaskName =
      currentTaskId === relation.task_id_1
        ? getTaskNameById(relation.task_id_2)
        : getTaskNameById(relation.task_id_1);

    switch (relation.connection_id) {
      case 1:
        return currentTaskId === relation.task_id_1
          ? `"${currentTaskName}" блокирует выполнение "${relatedTaskName}"`
          : `"${relatedTaskName}" блокирует выполнение "${currentTaskName}"`;
      case 2:
        return `"${currentTaskName}" дублирует "${relatedTaskName}"`;
      case 3:
        return `"${currentTaskName}" связана с "${relatedTaskName}"`;
    }
  };

  const handleSearchTasks = (query) => {
    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer);
    }

    if (!query || query.length < 2) {
      setSearchResults([]);
      setSearchLoading(false);
      return;
    }

    setSearchLoading(true);

    const timer = setTimeout(() => {
      try {
        const queryLower = query.toLowerCase();
        const filtered = projectTasks.filter(
          (t) =>
            t.id !== task?.id &&
            (t.name.toLowerCase().includes(queryLower) ||
              t.description?.toLowerCase().includes(queryLower)),
        );
        setSearchResults(filtered);
      } catch {
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    }, 300);

    setSearchDebounceTimer(timer);
  };

  const handleCreateRelation = async () => {
    if (!selectedTask || !selectedConnectionType || !isEdit) {
      return;
    }

    const payload = {
      task_id: selectedTask.id,
      connection_id: Number(selectedConnectionType),
    };

    const response = await createTaskRelationApi(task.id, payload, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setRelations([...relations, response.relation]);
    setSelectedTask(null);
    setSelectedConnectionType("");
    setSearchQuery("");
    setSearchResults([]);
  };

  const handleDeleteRelation = async (relationId) => {
    if (!teamId) {
      return;
    }

    const response = await deleteTaskRelationApi(teamId, relationId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setRelations(relations.filter((r) => r.id !== relationId));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      name: name.trim(),
      description: description?.trim() || null,
      status_id: Number(statusId) || null,
      priority_id: Number(priorityId) || null,
      assignee_email: assigneeEmail?.trim() || null,
      start_date: toISOStringOrNull(startDate, startTime),
      deadline: toISOStringOrNull(deadlineDate, deadlineTime),
      position: position,
    };

    if (!isEdit && position != null && onBeforeCreate) {
      await onBeforeCreate(position);
    }

    const response = isEdit
      ? await updateTaskApi(task.id, payload, token)
      : await createTaskApi(payload, streamId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    const savedTask = response.task;
    onSaved?.(savedTask);
    onClose?.();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>
        {isEdit ? "Редактировать задачу" : "Добавить задачу"}
      </DialogTitle>
      <DialogContent dividers>
        <Box
          component="form"
          onSubmit={handleSubmit}
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

          <Box sx={{ px: 1.5, py: 1 }}>
            <Typography
              sx={{
                color: "text.secondary",
                fontFamily: '"Montserrat", sans-serif',
                fontWeight: 700,
                mb: 1,
              }}
            >
              Описание
            </Typography>
            <TextField
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              variant="outlined"
              size="small"
              fullWidth
              placeholder="Введите описание"
              multiline
              rows={4}
            />
          </Box>

          <FormRow label="Исполнитель (email)">
            <TextField
              value={assigneeEmail}
              onChange={(e) => setAssigneeEmail(e.target.value)}
              type="email"
              variant="outlined"
              size="small"
              fullWidth
              placeholder="user@example.com"
            />
          </FormRow>

          <FormRow label="Статус">
            <FormControl fullWidth size="small">
              <Select
                variant="outlined"
                value={statusId === "" ? "" : Number(statusId)}
                onChange={(e) => setStatusId(e.target.value)}
              >
                {(statuses || []).map((s) => (
                  <MenuItem key={s.id} value={s.id}>
                    {s.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </FormRow>

          <FormRow label="Приоритет">
            <FormControl fullWidth size="small">
              <Select
                variant="outlined"
                value={priorityId === "" ? "" : Number(priorityId)}
                onChange={(e) => setPriorityId(e.target.value)}
              >
                {(priorities || []).map((p) => (
                  <MenuItem key={p.id} value={p.id}>
                    {p.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </FormRow>

          <FormRow label="Дата начала">
            <div style={{ display: "flex", gap: 1 }}>
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
            <div style={{ display: "flex", gap: 1 }}>
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

          {isEdit && projectId && teamId && (
            <>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ px: 1.5, py: 1 }}>
                <Typography
                  sx={{
                    color: "text.secondary",
                    fontFamily: '"Montserrat", sans-serif',
                    fontWeight: 700,
                    mb: 1,
                  }}
                >
                  Связи задач
                </Typography>

                {relations.length > 0 ? (
                  <List dense sx={{ mb: 2 }}>
                    {relations.map((relation) => (
                      <ListItem
                        key={relation.id}
                        sx={{
                          border: "1px solid #e0e0e0",
                          borderRadius: 1,
                          mb: 1,
                          bgcolor: "#f9f9f9",
                        }}
                        secondaryAction={
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => handleDeleteRelation(relation.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        }
                      >
                        <ListItemText primary={formatRelationText(relation)} />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    Связей пока нет
                  </Typography>
                )}

                <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                  <Typography variant="body2" fontWeight={600}>
                    Создать новую связь
                  </Typography>

                  {selectedTask && (
                    <Box
                      sx={{
                        p: 1,
                        bgcolor: "#f0f7ff",
                        border: "1px solid #90caf9",
                        borderRadius: 1,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                      }}
                    >
                      <Typography variant="body2">
                        {selectedTask.name}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedTask(null);
                          setSearchQuery("");
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  )}

                  {!selectedTask && (
                    <Autocomplete
                      size="small"
                      options={searchResults}
                      getOptionLabel={(option) => `${option.name}`}
                      loading={searchLoading}
                      value={null}
                      onChange={(e, newValue) => {
                        if (newValue) {
                          setSelectedTask(newValue);
                          setSearchQuery("");
                          setSearchResults([]);
                        }
                      }}
                      inputValue={searchQuery}
                      onInputChange={(e, newInputValue, reason) => {
                        if (reason === "input") {
                          setSearchQuery(newInputValue);
                          handleSearchTasks(newInputValue);
                        } else if (reason === "clear") {
                          setSearchQuery("");
                          setSearchResults([]);
                        }
                      }}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          placeholder="Начните вводить название задачи..."
                          slotProps={{
                            input: {
                              ...params.InputProps,
                              endAdornment: (
                                <>
                                  {searchLoading ? (
                                    <CircularProgress
                                      color="inherit"
                                      size={20}
                                    />
                                  ) : null}
                                  {params.InputProps.endAdornment}
                                </>
                              ),
                            },
                          }}
                        />
                      )}
                      noOptionsText="Задачи не найдены"
                    />
                  )}

                  <FormControl fullWidth size="small">
                    <Select
                      variant="outlined"
                      value={selectedConnectionType}
                      onChange={(e) =>
                        setSelectedConnectionType(e.target.value)
                      }
                      displayEmpty
                    >
                      <MenuItem value="" disabled>
                        Выберите тип связи
                      </MenuItem>
                      {connectionTypes.map((ct) => (
                        <MenuItem key={ct.id} value={ct.id}>
                          {ct.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <Button
                    variant="outlined"
                    startIcon={<AddIcon />}
                    onClick={handleCreateRelation}
                    disabled={!selectedTask || !selectedConnectionType}
                    fullWidth
                  >
                    Добавить связь
                  </Button>
                </Box>
              </Box>
            </>
          )}
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

export default TaskForm;
