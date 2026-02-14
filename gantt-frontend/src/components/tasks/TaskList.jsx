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
import {
  MoreVert as MoreVertIcon,
  Add as AddIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
} from "@mui/icons-material";
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

const TaskList = ({ streamId, projectId = null, teamId = null }) => {
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
  const [sortField, setSortField] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

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

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  const renderSortIcon = (field) => {
    if (sortField !== field) {
      return null;
    }

    return sortOrder === "asc" ? (
      <ArrowUpwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    ) : (
      <ArrowDownwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    );
  };

  const filteredTasks = useMemo(() => {
    if (filterMode === "my") {
      return tasks.filter((task) => task.assignee_email === userEmail);
    }
    return tasks;
  }, [tasks, filterMode, userEmail]);

  const sortedTasks = useMemo(() => {
    const sorted = [...filteredTasks];

    sorted.sort((a, b) => {
      let aValue, bValue;

      switch (sortField) {
        case "name":
          aValue = (a.name || "").toLowerCase();
          bValue = (b.name || "").toLowerCase();
          break;
        case "assignee":
          aValue = (a.assignee_email || "").toLowerCase();
          bValue = (b.assignee_email || "").toLowerCase();
          break;
        case "status":
          aValue = a.status_id
            ? (statusMap[a.status_id] || "").toLowerCase()
            : "";
          bValue = b.status_id
            ? (statusMap[b.status_id] || "").toLowerCase()
            : "";
          break;
        case "priority":
          aValue = a.priority_id
            ? (priorityMap[a.priority_id] || "").toLowerCase()
            : "";
          bValue = b.priority_id
            ? (priorityMap[b.priority_id] || "").toLowerCase()
            : "";
          break;
        case "start_date":
          aValue = a.start_date ? new Date(a.start_date).getTime() : 0;
          bValue = b.start_date ? new Date(b.start_date).getTime() : 0;
          break;
        case "deadline":
          aValue = a.deadline ? new Date(a.deadline).getTime() : 0;
          bValue = b.deadline ? new Date(b.deadline).getTime() : 0;
          break;
        default:
          return 0;
      }

      if (aValue < bValue) {
        return sortOrder === "asc" ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortOrder === "asc" ? 1 : -1;
      }

      if (sortField !== "name") {
        const na = (a.name || "").toLowerCase();
        const nb = (b.name || "").toLowerCase();
        return na < nb ? -1 : 1;
      }

      return 0;
    });

    return sorted;
  }, [filteredTasks, sortField, sortOrder, statusMap, priorityMap]);

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
                  <TableCell
                    sx={HEADER_CELL_STYLES}
                    onClick={() => handleSort("name")}
                  >
                    <div style={{ display: "flex", alignItems: "center" }}>
                      Название
                      {renderSortIcon("name")}
                    </div>
                  </TableCell>
                  <TableCell
                    sx={HEADER_CELL_STYLES}
                    onClick={() => handleSort("assignee")}
                  >
                    <div style={{ display: "flex", alignItems: "center" }}>
                      Исполнитель
                      {renderSortIcon("assignee")}
                    </div>
                  </TableCell>
                  <TableCell
                    sx={HEADER_CELL_STYLES}
                    onClick={() => handleSort("status")}
                  >
                    <div style={{ display: "flex", alignItems: "center" }}>
                      Статус
                      {renderSortIcon("status")}
                    </div>
                  </TableCell>
                  <TableCell
                    sx={HEADER_CELL_STYLES}
                    onClick={() => handleSort("priority")}
                  >
                    <div style={{ display: "flex", alignItems: "center" }}>
                      Приоритет
                      {renderSortIcon("priority")}
                    </div>
                  </TableCell>
                  <TableCell
                    sx={HEADER_CELL_STYLES}
                    onClick={() => handleSort("start_date")}
                  >
                    <div style={{ display: "flex", alignItems: "center" }}>
                      Дата начала
                      {renderSortIcon("start_date")}
                    </div>
                  </TableCell>
                  <TableCell
                    sx={HEADER_CELL_STYLES}
                    onClick={() => handleSort("deadline")}
                  >
                    <div style={{ display: "flex", alignItems: "center" }}>
                      Дедлайн
                      {renderSortIcon("deadline")}
                    </div>
                  </TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                {(sortedTasks || []).map((task) => (
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
        projectId={projectId}
        teamId={teamId}
        onSaved={() => {
          setFormOpen(false);
          loadAll();
        }}
      />
    </>
  );
};

export default TaskList;
