import React, { useEffect, useState, useMemo } from "react";
import {
  CircularProgress,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
  Paper,
  IconButton,
  Button,
  Menu,
  MenuItem,
  ToggleButtonGroup,
  ToggleButton,
} from "@mui/material";
import { MoreVert as MoreVertIcon, Add as AddIcon } from "@mui/icons-material";
import TaskForm from "./TaskForm.jsx";

import { useProcessError } from "../../hooks/useProcessError.js";
import { fetchTasksApi, deleteTaskApi } from "../../api/task.js";
import { fetchStatusesApi, fetchPrioritiesApi } from "../../api/meta.js";
import { fetchUserEmailApi } from "../../api/user.js";
import {
  CELL_STYLES,
  HEADER_CELL_STYLES,
  LAST_CELL_STYLES,
  TASKS_TABLE_BODY_STYLES,
  TABLE_CONTAINER_STYLES,
  CREATE_BUTTON_STYLES,
  TOGGLE_BUTTON_STYLES,
} from "./tableStyles.js";
import { toLocaleDateWithTimeHM } from "../../utils/datetime.js";

const TaskList = ({ streamId }) => {
  const [tasks, setTasks] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);

  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [menuTaskId, setMenuTaskId] = useState(null);

  const [formOpen, setFormOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);

  const [filterMode, setFilterMode] = useState("all");
  const [userEmail, setUserEmail] = useState("");

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();

  const openMenu = (event, id) => {
    setMenuAnchorEl(event.currentTarget);
    setMenuTaskId(id);
  };

  const handleCreate = () => {
    setSelectedTask(null);
    setFormOpen(true);
  };

  const handleEdit = () => {
    const t = (tasks || []).find((x) => x.id === menuTaskId);
    setSelectedTask(t || null);
    setFormOpen(true);
    closeMenu();
  };

  const handleDelete = async () => {
    const response = await deleteTaskApi(menuTaskId, token);
    if (!response.ok) {
      processError(response.status);
      return;
    }

    await loadAll();
  };

  const statusMap = useMemo(() => {
    const map = {};
    (statuses || []).forEach((s) => (map[s.id] = s.name));
    return map;
  }, [statuses]);

  const priorityMap = useMemo(() => {
    const map = {};
    (priorities || []).forEach((p) => (map[p.id] = p.name));
    return map;
  }, [priorities]);

  const fetchTasks = async () => {
    const response = await fetchTasksApi(streamId, token);

    if (!response.ok) {
      processError(response.status);
      return [];
    }

    return response.tasks;
  };

  const fetchStatuses = async () => {
    const response = await fetchStatusesApi();

    if (!response.ok) {
      processError(response.status);
      return [];
    }

    return response.statuses;
  };

  const fetchPriorities = async () => {
    const response = await fetchPrioritiesApi();

    if (!response.ok) {
      processError(response.status);
      return [];
    }

    return response.priorities;
  };

  const fetchUserEmail = async () => {
    const response = await fetchUserEmailApi(token);

    if (!response.ok) {
      processError(response.status);
      return "";
    }

    return response.email;
  };

  const loadAll = async () => {
    setLoading(true);

    const tasks = await fetchTasks();
    const statuses = await fetchStatuses();
    const priorities = await fetchPriorities();
    const email = await fetchUserEmail();

    setTasks(tasks || []);
    setStatuses(statuses || []);
    setPriorities(priorities || []);
    setUserEmail(email || "");

    setLoading(false);
  };

  useEffect(() => {
    loadAll();
  }, [streamId]);

  const closeMenu = () => {
    setMenuAnchorEl(null);
    setMenuTaskId(null);
  };

  const filteredTasks = useMemo(() => {
    if (filterMode === "my") {
      return tasks.filter((task) => task.assignee_email === userEmail);
    }
    return tasks;
  }, [tasks, filterMode, userEmail]);

  if (loading) {
    return <CircularProgress size={32} />;
  }

  return (
    <>
      <div
        style={{
          backgroundColor: "#F5F6F7",
          padding: "12px",
          borderRadius: "8px",
          marginBottom: "16px",
          display: "inline-block",
        }}
      >
        <ToggleButtonGroup
          value={filterMode}
          exclusive
          onChange={(e, newValue) => {
            if (newValue !== null) {
              setFilterMode(newValue);
            }
          }}
          aria-label="task filter"
          size="small"
          sx={{
            "& .MuiToggleButtonGroup-grouped": {
              border: "none",
              "&:not(:first-of-type)": {
                borderRadius: "8px",
                marginLeft: "8px",
              },
              "&:first-of-type": {
                borderRadius: "8px",
              },
            },
          }}
        >
          <ToggleButton
            value="all"
            aria-label="all tasks"
            sx={TOGGLE_BUTTON_STYLES}
          >
            Все задачи
          </ToggleButton>
          <ToggleButton
            value="my"
            aria-label="my tasks"
            sx={TOGGLE_BUTTON_STYLES}
          >
            Назначенные мне
          </ToggleButton>
        </ToggleButtonGroup>
      </div>

      {filteredTasks.length > 0 ? (
        <div>
          <TableContainer component={Paper} sx={TABLE_CONTAINER_STYLES}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={HEADER_CELL_STYLES}>Название</TableCell>
                  <TableCell sx={HEADER_CELL_STYLES}>Исполнитель</TableCell>
                  <TableCell sx={HEADER_CELL_STYLES}>Статус</TableCell>
                  <TableCell sx={HEADER_CELL_STYLES}>Приоритет</TableCell>
                  <TableCell sx={HEADER_CELL_STYLES}>Дата начала</TableCell>
                  <TableCell sx={HEADER_CELL_STYLES}>Дедлайн</TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                {(filteredTasks || []).map((task) => (
                  <TableRow key={task.id} sx={TASKS_TABLE_BODY_STYLES}>
                    <TableCell sx={CELL_STYLES}>{task.name}</TableCell>

                    <TableCell sx={CELL_STYLES}>
                      {task.assignee_email || "-"}
                    </TableCell>

                    <TableCell sx={CELL_STYLES}>
                      {task.status_id ? statusMap[task.status_id] : "-"}
                    </TableCell>

                    <TableCell sx={CELL_STYLES}>
                      {task.priority_id ? priorityMap[task.priority_id] : "-"}
                    </TableCell>

                    <TableCell sx={CELL_STYLES}>
                      {task.start_date
                        ? toLocaleDateWithTimeHM(task.start_date)
                        : "-"}
                    </TableCell>

                    <TableCell sx={LAST_CELL_STYLES}>
                      {task.deadline
                        ? toLocaleDateWithTimeHM(task.deadline)
                        : "-"}

                      <IconButton
                        size="small"
                        onClick={(e) => openMenu(e, task.id)}
                        className="task-actions"
                        sx={{
                          position: "absolute",
                          right: 8,
                          top: "50%",
                          transform: "translateY(-50%)",
                        }}
                      >
                        <MoreVertIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}

                <Button
                  variant="text"
                  onClick={handleCreate}
                  startIcon={<AddIcon />}
                  sx={CREATE_BUTTON_STYLES}
                >
                  Создать
                </Button>
              </TableBody>
            </Table>
          </TableContainer>

          <Menu
            anchorEl={menuAnchorEl}
            open={Boolean(menuAnchorEl)}
            onClose={closeMenu}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "right" }}
          >
            <MenuItem onClick={handleEdit}>Редактировать</MenuItem>

            <MenuItem onClick={handleDelete}>Удалить</MenuItem>
          </Menu>
        </div>
      ) : (
        <div>
          <Button
            variant="text"
            onClick={handleCreate}
            startIcon={<AddIcon />}
            sx={CREATE_BUTTON_STYLES}
          >
            Создать
          </Button>
        </div>
      )}

      <TaskForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        streamId={streamId}
        task={selectedTask}
        statuses={statuses}
        priorities={priorities}
        onSaved={() => {
          setFormOpen(false);
          loadAll();
        }}
      />
    </>
  );
};

export default TaskList;
