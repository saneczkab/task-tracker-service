import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
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
  Chip,
} from "@mui/material";
import { Delete as DeleteIcon, Add as AddIcon } from "@mui/icons-material";
import FormRow from "./FormRow.jsx";
import RemindersSection from "./RemindersSection.jsx";
import {
  toInputDate,
  toInputTime,
  toISOStringOrNull,
} from "../../utils/datetime.js";

import { useProcessError } from "../../hooks/useProcessError.js";
import { useConfirmDelete } from "../../context/ConfirmDeleteDialogContext.jsx";
import {
  createTaskApi,
  updateTaskApi,
  updateTaskKeepaliveApi,
  getProjectTasksApi,
  createTaskRelationApi,
  deleteTaskRelationApi,
} from "../../api/task.js";
import { fetchTeamMembersApi } from "../../api/team.js";
import { fetchConnectionTypesApi } from "../../api/meta.js";
import {
  fetchTeamTagsApi,
  createTeamTagApi,
  deleteTeamTagApi,
} from "../../api/tag.js";
import {
  fetchTeamCustomFieldsApi,
  createTeamCustomFieldApi,
  deleteTeamCustomFieldApi,
  deleteTaskCustomFieldValueApi,
} from "../../api/customField.js";
import TagSelector from "./TagSelector.jsx";
import { getContrastColor } from "../../utils/taskUtils.js";
import TaskCustomFieldsSection from "./TaskCustomFieldsSection.jsx";

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
  pageMode = false,
  autoSave = false,
  onSaveStateChange,
  skipSaveOnUnmount = false,
}) => {
  const [statuses, setStatuses] = useState(statusesProp || []);
  const [priorities, setPriorities] = useState(prioritiesProp || []);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [assigneeEmail, setAssigneeEmail] = useState("");
  const [assigneeError, setAssigneeError] = useState("");
  const [teamMembers, setTeamMembers] = useState([]);
  const [teamMembersLoading, setTeamMembersLoading] = useState(false);
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

  const [teamTags, setTeamTags] = useState([]);
  const [selectedTagIds, setSelectedTagIds] = useState([]);
  const [customFields, setCustomFields] = useState([]);
  const [customFieldValues, setCustomFieldValues] = useState({});
  const [initialCustomFieldValues, setInitialCustomFieldValues] = useState({});
  const [activeCustomFieldIds, setActiveCustomFieldIds] = useState([]);
  const [initialActiveCustomFieldIds, setInitialActiveCustomFieldIds] =
    useState([]);
  const [removedCustomFieldIds, setRemovedCustomFieldIds] = useState([]);
  const [creatingCustomField, setCreatingCustomField] = useState(false);
  const [initialized, setInitialized] = useState(false);

  const autoSaveTimerRef = useRef(null);
  const latestPayloadRef = useRef(null);
  const lastSavedPayloadRef = useRef(null);
  const queuedPayloadRef = useRef(null);
  const savingRef = useRef(false);
  const mountedRef = useRef(true);
  const skipSaveOnUnmountRef = useRef(skipSaveOnUnmount);
  const onSavedRef = useRef(onSaved);
  const flushAutoSaveRef = useRef(() => {});

  const isEdit = Boolean(task?.id);
  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();
  const { confirm } = useConfirmDelete();

  skipSaveOnUnmountRef.current = skipSaveOnUnmount;
  onSavedRef.current = onSaved;

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
    setAssigneeError("");
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
    const taskTags = task?.tag_list ?? [];
    setSelectedTagIds(taskTags.map((tag) => tag.id));
    setTeamTags(taskTags);
    setCustomFields([]);
    setCustomFieldValues({});
    setInitialCustomFieldValues({});
    setActiveCustomFieldIds([]);
    setInitialActiveCustomFieldIds([]);
    setRemovedCustomFieldIds([]);
    setInitialized(true);

    return () => {
      if (searchDebounceTimer) {
        clearTimeout(searchDebounceTimer);
      }
    };
  }, [open, task]);

  const filteredTeamMembers = useMemo(() => {
    if (!teamMembers.length) {
      return [];
    }

    const query = assigneeEmail.trim().toLowerCase();
    if (!query) {
      return teamMembers;
    }

    return teamMembers.filter(
      (user) =>
        user.email.toLowerCase().includes(query) ||
        user.nickname.toLowerCase().includes(query),
    );
  }, [teamMembers, assigneeEmail]);

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

    if (teamId) {
      setTeamMembersLoading(true);
      const membersResponse = await fetchTeamMembersApi(teamId, token);
      if (membersResponse.ok) {
        setTeamMembers(membersResponse.users);
      } else {
        setTeamMembers([]);
        processError(membersResponse.status);
      }
      setTeamMembersLoading(false);

      const tagsResponse = await fetchTeamTagsApi(teamId, token);
      if (tagsResponse.ok) {
        setTeamTags(tagsResponse.tags);
      }

      const customFieldsResponse = await fetchTeamCustomFieldsApi(
        teamId,
        token,
      );
      if (customFieldsResponse.ok) {
        const fieldDefs = customFieldsResponse.fields;
        const taskCustomFieldValues = task?.custom_field_values ?? [];
        const initialFieldIds = taskCustomFieldValues.map(
          (value) => value.custom_field_id,
        );
        const initialValues =
          TaskCustomFieldsSection.buildInitialCustomFieldValues(
            fieldDefs,
            taskCustomFieldValues,
          );

        setCustomFields(fieldDefs);
        setCustomFieldValues(initialValues);
        setInitialCustomFieldValues(initialValues);
        setActiveCustomFieldIds(initialFieldIds);
        setInitialActiveCustomFieldIds(initialFieldIds);
        setRemovedCustomFieldIds([]);
      } else {
        processError(customFieldsResponse.status);
      }
    } else {
      setTeamMembers([]);
      setCustomFields([]);
      setCustomFieldValues({});
      setInitialCustomFieldValues({});
      setActiveCustomFieldIds([]);
      setInitialActiveCustomFieldIds([]);
      setRemovedCustomFieldIds([]);
    }
  };

  const handleCustomFieldValueChange = (fieldId, value) => {
    setCustomFieldValues((prev) => ({
      ...prev,
      [fieldId]: value,
    }));
  };

  const handleCreateCustomField = async (field) => {
    if (!teamId) {
      return false;
    }

    setCreatingCustomField(true);
    const response = await createTeamCustomFieldApi(teamId, field, token);
    setCreatingCustomField(false);

    if (!response.ok) {
      processError(response.status);
      return false;
    }

    const createdField = response.field;
    setCustomFields((prev) => [...prev, createdField]);
    setCustomFieldValues((prev) => ({
      ...prev,
      [createdField.id]: "",
    }));
    setInitialCustomFieldValues((prev) => ({
      ...prev,
      [createdField.id]: "",
    }));
    setActiveCustomFieldIds((prev) => [...prev, createdField.id]);
    setRemovedCustomFieldIds((prev) =>
      prev.filter((id) => id !== createdField.id),
    );

    return createdField;
  };

  const handleAddExistingCustomField = (fieldId) => {
    setActiveCustomFieldIds((prev) =>
      prev.includes(fieldId) ? prev : [...prev, fieldId],
    );
    setRemovedCustomFieldIds((prev) => prev.filter((id) => id !== fieldId));
  };

  const handleRemoveCustomField = (fieldId) => {
    setActiveCustomFieldIds((prev) => prev.filter((id) => id !== fieldId));

    if (initialActiveCustomFieldIds.includes(fieldId)) {
      setRemovedCustomFieldIds((prev) =>
        prev.includes(fieldId) ? prev : [...prev, fieldId],
      );
    }

    if (autoSave && isEdit) {
      deleteTaskCustomFieldValueApi(task.id, fieldId, token).then(
        (response) => {
          if (!response.ok) {
            processError(response.status);
          }
        },
      );
    }
  };

  const handleDeleteCustomFieldDefinition = async (fieldId) => {
    const field = customFields.find((f) => f.id === fieldId);
    if (!(await confirm(`поле "${field?.name || ""}"`))) return;
    const response = await deleteTeamCustomFieldApi(fieldId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setCustomFields((prev) => prev.filter((field) => field.id !== fieldId));
    setActiveCustomFieldIds((prev) => prev.filter((id) => id !== fieldId));
    setInitialActiveCustomFieldIds((prev) =>
      prev.filter((id) => id !== fieldId),
    );
    setRemovedCustomFieldIds((prev) => prev.filter((id) => id !== fieldId));
    setCustomFieldValues((prev) => {
      const copy = { ...prev };
      delete copy[fieldId];
      return copy;
    });
    setInitialCustomFieldValues((prev) => {
      const copy = { ...prev };
      delete copy[fieldId];
      return copy;
    });
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

    if (!query?.length) {
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

    const relation = relations.find((r) => r.id === relationId);
    const label = relation
      ? `связь "${formatRelationText(relation)}"`
      : "эту связь";
    if (!(await confirm(label))) return;

    const response = await deleteTaskRelationApi(teamId, relationId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setRelations(relations.filter((r) => r.id !== relationId));
  };

  const handleTagToggle = (tagId) => {
    setSelectedTagIds((prev) =>
      prev.includes(tagId)
        ? prev.filter((id) => id !== tagId)
        : [...prev, tagId],
    );
  };

  const handleCreateTag = async (name, color) => {
    if (!teamId) return;
    const response = await createTeamTagApi(teamId, name, color, token);
    if (response.ok) {
      setTeamTags((prev) => [...prev, response.tag]);
      setSelectedTagIds((prev) => [...prev, response.tag.id]);
    } else {
      processError(response.status);
    }
  };

  const handleDeleteTag = async (tagId) => {
    if (!teamId) return;
    const tag = teamTags.find((t) => t.id === tagId);
    if (!(await confirm(`тег "${tag?.name || ""}"`))) return;
    const response = await deleteTeamTagApi(teamId, tagId, token);
    if (response.ok) {
      setTeamTags((prev) => prev.filter((tag) => tag.id !== tagId));
      setSelectedTagIds((prev) => prev.filter((id) => id !== tagId));
    } else {
      processError(response.status);
    }
  };

  const buildPayload = useCallback(
    () => ({
      name: isEdit ? name.trim() : name.trim() || "Новое название",
      description: description?.trim() || null,
      status_id: Number(statusId) || null,
      priority_id: Number(priorityId) || null,
      assignee_email: assigneeEmail?.trim() || null,
      start_date: toISOStringOrNull(startDate, startTime),
      deadline: toISOStringOrNull(deadlineDate, deadlineTime),
      tag_ids: selectedTagIds,
      custom_fields: TaskCustomFieldsSection.buildCustomFieldsPayload(
        customFields,
        customFieldValues,
        initialCustomFieldValues,
        activeCustomFieldIds,
        initialActiveCustomFieldIds,
      ),
      position: position,
    }),
    [
      activeCustomFieldIds,
      assigneeEmail,
      customFields,
      customFieldValues,
      deadlineDate,
      deadlineTime,
      description,
      initialActiveCustomFieldIds,
      initialCustomFieldValues,
      isEdit,
      name,
      position,
      priorityId,
      selectedTagIds,
      startDate,
      startTime,
      statusId,
    ],
  );

  const saveQueuedPayload = useCallback(
    async (payload) => {
      queuedPayloadRef.current = payload;
      if (savingRef.current) return;

      savingRef.current = true;
      while (queuedPayloadRef.current) {
        const nextPayload = queuedPayloadRef.current;
        queuedPayloadRef.current = null;
        const serializedPayload = JSON.stringify(nextPayload);

        if (!nextPayload.name) {
          if (mountedRef.current) onSaveStateChange?.("error");
          continue;
        }

        if (mountedRef.current) onSaveStateChange?.("saving");
        const response = await updateTaskApi(task.id, nextPayload, token);

        if (!response.ok) {
          const errorDetail = String(response.details?.detail || "");
          if (
            response.status === 404 &&
            nextPayload.assignee_email &&
            errorDetail.includes("Пользователь не найден")
          ) {
            if (mountedRef.current) {
              setAssigneeError(
                "Пользователя не существует или он не состоит в команде",
              );
            }
          } else {
            processError(response.status);
          }
          queuedPayloadRef.current = null;
          if (mountedRef.current) onSaveStateChange?.("error");
          break;
        }

        lastSavedPayloadRef.current = serializedPayload;
        if (mountedRef.current && !queuedPayloadRef.current) {
          setAssigneeError("");
          onSavedRef.current?.(response.task);
          onSaveStateChange?.("saved");
        }
      }

      savingRef.current = false;
    },
    [onSaveStateChange, processError, task?.id, token],
  );

  const flushAutoSave = useCallback(() => {
    if (!autoSave || !isEdit || !latestPayloadRef.current) return;
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }

    const serializedPayload = JSON.stringify(latestPayloadRef.current);
    if (serializedPayload !== lastSavedPayloadRef.current) {
      saveQueuedPayload(latestPayloadRef.current);
    }
  }, [autoSave, isEdit, saveQueuedPayload]);

  flushAutoSaveRef.current = flushAutoSave;

  useEffect(() => {
    if (!autoSave || !isEdit || !initialized) return;

    const payload = buildPayload();
    latestPayloadRef.current = payload;
    const serializedPayload = JSON.stringify(payload);

    if (lastSavedPayloadRef.current === null) {
      lastSavedPayloadRef.current = serializedPayload;
      onSaveStateChange?.("saved");
      return;
    }

    if (serializedPayload === lastSavedPayloadRef.current) return;
    onSaveStateChange?.("pending");
    if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
    autoSaveTimerRef.current = setTimeout(flushAutoSave, 900);

    return () => {
      if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
    };
  }, [
    autoSave,
    buildPayload,
    flushAutoSave,
    initialized,
    isEdit,
    onSaveStateChange,
  ]);

  useEffect(() => {
    mountedRef.current = true;
    const handleBeforeUnload = () => {
      const payload = latestPayloadRef.current;
      if (
        autoSave &&
        isEdit &&
        payload &&
        JSON.stringify(payload) !== lastSavedPayloadRef.current
      ) {
        void updateTaskKeepaliveApi(task.id, payload, token).catch(
          () => undefined,
        );
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      mountedRef.current = false;
      if (!skipSaveOnUnmountRef.current) flushAutoSaveRef.current();
    };
  }, [autoSave, isEdit, task?.id, token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAssigneeError("");

    const payload = buildPayload();

    if (!isEdit && position != null && onBeforeCreate) {
      await onBeforeCreate(position);
    }

    const response = isEdit
      ? await updateTaskApi(task.id, payload, token)
      : await createTaskApi(payload, streamId, token);

    if (!response.ok) {
      const errorDetail = String(response.details?.detail || "");
      if (
        response.status === 404 &&
        payload.assignee_email &&
        errorDetail.includes("Пользователь не найден")
      ) {
        setAssigneeError(
          "Пользователя не существует или он не состоит в команде",
        );
        return;
      }
      processError(response.status);
      return;
    }

    const savedTask = response.task;

    for (const fieldId of removedCustomFieldIds) {
      await deleteTaskCustomFieldValueApi(savedTask.id, fieldId, token);
    }

    onSaved?.(savedTask);
    onClose?.();
  };

  const descriptionField = (
    <Box className="task-form-description" sx={{ px: 1.5, py: 1 }}>
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
        rows={6}
      />
    </Box>
  );

  const assigneeField = (
    <FormRow label="Исполнитель">
      {teamId ? (
        <Autocomplete
          freeSolo
          size="small"
          fullWidth
          openOnFocus
          options={filteredTeamMembers}
          getOptionLabel={(option) =>
            typeof option === "string" ? option : option.email
          }
          filterOptions={(options) => options}
          inputValue={assigneeEmail}
          onInputChange={(_, newValue) => {
            setAssigneeEmail(newValue);
            setAssigneeError("");
          }}
          onChange={(_, newValue) => {
            if (newValue && typeof newValue !== "string") {
              setAssigneeEmail(newValue.email);
            }
            setAssigneeError("");
          }}
          loading={teamMembersLoading}
          renderOption={(props, option) => (
            <li {...props} key={option.id}>
              <Box>
                <Typography variant="body2">{option.nickname}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {option.email}
                </Typography>
              </Box>
            </li>
          )}
          renderInput={(params) => (
            <TextField
              {...params}
              placeholder="Email или никнейм"
              error={Boolean(assigneeError)}
              helperText={assigneeError}
              slotProps={{
                input: {
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {teamMembersLoading ? (
                        <CircularProgress color="inherit" size={20} />
                      ) : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                },
              }}
            />
          )}
          noOptionsText="Пользователи не найдены"
        />
      ) : (
        <TextField
          value={assigneeEmail}
          onChange={(e) => {
            setAssigneeEmail(e.target.value);
            setAssigneeError("");
          }}
          variant="outlined"
          size="small"
          fullWidth
          placeholder="user@example.com"
          error={Boolean(assigneeError)}
          helperText={assigneeError}
        />
      )}
    </FormRow>
  );

  const statusField = (
    <FormRow label="Статус">
      <FormControl fullWidth size="small">
        <Select
          variant="outlined"
          value={statusId === "" ? "" : Number(statusId)}
          onChange={(e) => setStatusId(e.target.value)}
        >
          {(statuses || []).map((status) => (
            <MenuItem key={status.id} value={status.id}>
              {status.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </FormRow>
  );

  const priorityField = (
    <FormRow label="Приоритет">
      <FormControl fullWidth size="small">
        <Select
          variant="outlined"
          value={priorityId === "" ? "" : Number(priorityId)}
          onChange={(e) => setPriorityId(e.target.value)}
        >
          {(priorities || []).map((priority) => (
            <MenuItem key={priority.id} value={priority.id}>
              {priority.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </FormRow>
  );

  const startDateField = (
    <FormRow label="Дата начала">
      <Box sx={{ display: "flex", gap: 1 }}>
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
          sx={{ minWidth: 110 }}
        />
      </Box>
    </FormRow>
  );

  const deadlineField = (
    <FormRow label="Дедлайн">
      <Box sx={{ display: "flex", gap: 1 }}>
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
          sx={{ minWidth: 110 }}
        />
      </Box>
    </FormRow>
  );

  const tagsField = teamId ? (
    <FormRow label="Теги">
      <Box sx={{ display: "flex", flexDirection: "column", gap: 0.75 }}>
        {selectedTagIds.length > 0 && (
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
            {teamTags
              .filter((tag) => selectedTagIds.includes(tag.id))
              .map((tag) => (
                <Chip
                  key={tag.id}
                  label={tag.name}
                  size="small"
                  onDelete={() => handleTagToggle(tag.id)}
                  sx={{
                    bgcolor: tag.color,
                    color: getContrastColor(tag.color),
                    "& .MuiChip-deleteIcon": {
                      color: getContrastColor(tag.color),
                      opacity: 0.7,
                      "&:hover": { opacity: 1 },
                    },
                    fontWeight: 500,
                  }}
                />
              ))}
          </Box>
        )}
        <TagSelector
          teamTags={teamTags}
          selectedTagIds={selectedTagIds}
          onTagToggle={handleTagToggle}
          onCreateTag={handleCreateTag}
          onDeleteTag={handleDeleteTag}
        />
      </Box>
    </FormRow>
  ) : null;

  const customFieldsSection = (
    <TaskCustomFieldsSection
      fields={customFields}
      activeFieldIds={activeCustomFieldIds}
      values={customFieldValues}
      onChange={handleCustomFieldValueChange}
      onRemoveField={handleRemoveCustomField}
      onAddExistingField={handleAddExistingCustomField}
      onCreateField={handleCreateCustomField}
      onDeleteFieldDefinition={handleDeleteCustomFieldDefinition}
      creatingField={creatingCustomField}
    />
  );

  const remindersSection = isEdit ? (
    <RemindersSection
      taskId={task.id}
      token={token}
      deadline={
        deadlineDate ? toISOStringOrNull(deadlineDate, deadlineTime) : null
      }
    />
  ) : null;

  const relationsSection = isEdit && projectId && teamId && (
    <Box className="task-relations-section" sx={{ px: 1.5, py: 1 }}>
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
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
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
            <Typography variant="body2">{selectedTask.name}</Typography>
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
                          <CircularProgress color="inherit" size={20} />
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
            onChange={(e) => setSelectedConnectionType(e.target.value)}
            displayEmpty
          >
            <MenuItem value="" disabled>
              Выберите тип связи
            </MenuItem>
            {connectionTypes.map((connectionType) => (
              <MenuItem key={connectionType.id} value={connectionType.id}>
                {connectionType.name}
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
  );

  if (pageMode) {
    return (
      <Box
        component="form"
        onSubmit={handleSubmit}
        onBlurCapture={() => setTimeout(flushAutoSave, 0)}
        sx={{
          width: "100%",
          px: { xs: 0, md: 2 },
          pb: 6,
          "& .task-page-sidebar .task-form-row": {
            gridTemplateColumns: "minmax(0, 1fr)",
            gap: 1,
          },
          "& .task-form-row, & .task-form-description": {
            px: 0,
            py: 2,
            borderRadius: 0,
            borderBottom: "1px solid #EEF0F4",
          },
          "& .task-form-row:hover": { backgroundColor: "transparent" },
          "& .MuiOutlinedInput-root": {
            backgroundColor: "#F7F8FA",
            borderRadius: 2,
          },
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "#E3E6EC !important",
          },
          "& .task-custom-fields-section, & .task-reminders-section, & .task-relations-section":
            {
              px: 0,
              py: 2.5,
              borderBottom: "1px solid #EEF0F4",
            },
          "& .task-custom-fields-section .task-form-row": {
            gridTemplateColumns: "minmax(0, 1fr)",
            gap: 1,
          },
        }}
      >
        <Box sx={{ pb: 3, borderBottom: "1px solid #E8EAF0" }}>
          <Typography
            variant="overline"
            sx={{
              color: "#7A8194",
              fontWeight: 700,
              letterSpacing: "0.12em",
            }}
          >
            Название задачи
          </Typography>
          <TextField
            value={name}
            onChange={(e) => setName(e.target.value)}
            variant="standard"
            fullWidth
            placeholder="Введите название"
            slotProps={{
              input: {
                disableUnderline: true,
                sx: {
                  mt: 0.5,
                  fontSize: { xs: 26, md: 36 },
                  lineHeight: 1.2,
                  fontWeight: 750,
                  color: "#252936",
                },
              },
            }}
          />
        </Box>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "minmax(0, 1fr)", md: "2fr 1fr" },
            gap: { xs: 3, md: 5 },
            alignItems: "start",
          }}
        >
          <Box sx={{ minWidth: 0 }}>
            {descriptionField}
            {remindersSection}
            {relationsSection}
          </Box>
          <Box
            className="task-page-sidebar"
            sx={{
              minWidth: 0,
              borderLeft: { xs: 0, md: "1px solid #EEF0F4" },
              pl: { xs: 0, md: 4 },
            }}
          >
            {assigneeField}
            {statusField}
            {priorityField}
            {startDateField}
            {deadlineField}
            {tagsField}
            {customFieldsSection}
          </Box>
        </Box>
      </Box>
    );
  }

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Добавить задачу</DialogTitle>
      <DialogContent dividers>
        <Box
          component="form"
          id="task-modal-form"
          onSubmit={handleSubmit}
          sx={{ display: "grid", gap: 2 }}
        >
          <TextField
            value={name}
            onChange={(e) => setName(e.target.value)}
            variant="outlined"
            size="small"
            fullWidth
            autoFocus
            placeholder="Введите название"
          />
          <Typography variant="body2" color="text.secondary">
            Введите название задачи и перейдите к заполнению деталей
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Отмена</Button>
        <Button
          type="submit"
          form="task-modal-form"
          variant="contained"
          disabled={!name.trim()}
        >
          Создать
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TaskForm;
