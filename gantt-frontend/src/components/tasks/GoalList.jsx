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
} from "@mui/material";
import {
  MoreVert as MoreVertIcon,
  Add as AddIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
} from "@mui/icons-material";
import GoalForm from "./GoalForm.jsx";

import { useProcessError } from "../../hooks/useProcessError.js";
import { fetchGoalsApi, deleteGoalApi } from "../../api/goal.js";
import {
  CELL_STYLES,
  HEADER_CELL_STYLES,
  LAST_CELL_STYLES,
  TABLE_CONTAINER_STYLES,
  GOALS_TABLE_BODY_STYLES,
  CREATE_BUTTON_STYLES,
} from "./tableStyles.js";
import { toLocaleDateWithTimeHM } from "../../utils/datetime.js";

const GoalList = ({ streamId }) => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);

  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [menuGoalId, setMenuGoalId] = useState(null);

  const [deletingGoalId, setDeletingGoalId] = useState(null);

  const [formOpen, setFormOpen] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState(null);

  const [sortField, setSortField] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();

  const fetchGoals = async () => {
    setLoading(true);

    const response = await fetchGoalsApi(streamId, token);

    if (!response.ok) {
      processError(response.status);
      setLoading(false);
      return;
    }

    setGoals(response.goals);
    setLoading(false);
  };

  const handleSaved = (saved) => {
    setFormOpen(false);
    setSelectedGoal(null);
    setGoals((prev) => {
      const idx = prev.findIndex((g) => g.id === saved.id);
      if (idx === -1) {
        return [...prev, saved];
      }
      const copy = [...prev];
      copy[idx] = saved;
      return copy;
    });
  };

  useEffect(() => {
    fetchGoals();
  }, [streamId]);

  const openMenu = (event, goalId) => {
    setMenuAnchorEl(event.currentTarget);
    setMenuGoalId(goalId);
  };

  const closeMenu = () => {
    setMenuAnchorEl(null);
    setMenuGoalId(null);
  };

  const deleteGoal = async (goalId) => {
    setDeletingGoalId(goalId);
    setMenuAnchorEl(null);

    const response = await deleteGoalApi(goalId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setGoals((prev) => prev.filter((g) => g.id !== goalId));
    setDeletingGoalId(null);
  };

  const handleCreate = () => {
    setSelectedGoal(null);
    setFormOpen(true);
  };

  const handleEdit = () => {
    const goal = goals.find((x) => x.id === menuGoalId) || null;
    setSelectedGoal(goal);
    setFormOpen(true);
    closeMenu();
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
    if (sortField !== field) return null;
    return sortOrder === "asc" ? (
      <ArrowUpwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    ) : (
      <ArrowDownwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    );
  };

  const sortedGoals = useMemo(() => {
    const sorted = [...goals];

    sorted.sort((a, b) => {
      let aValue, bValue;

      switch (sortField) {
        case "name":
          aValue = (a.name || "").toLowerCase();
          bValue = (b.name || "").toLowerCase();
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
  }, [goals, sortField, sortOrder]);

  if (loading) {
    return <CircularProgress size={32} />;
  }

  return (
    <>
      {goals.length > 0 ? (
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
                {sortedGoals.map((goal) => (
                  <TableRow key={goal.id} sx={GOALS_TABLE_BODY_STYLES}>
                    <TableCell sx={CELL_STYLES}>{goal.name}</TableCell>

                    <TableCell sx={CELL_STYLES}>
                      {goal.start_date
                        ? toLocaleDateWithTimeHM(goal.start_date)
                        : "-"}
                    </TableCell>

                    <TableCell sx={LAST_CELL_STYLES}>
                      {goal.deadline
                        ? toLocaleDateWithTimeHM(goal.deadline)
                        : "-"}

                      <IconButton
                        size="small"
                        onClick={(e) => openMenu(e, goal.id)}
                        className="goal-actions"
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
              </TableBody>
            </Table>
          </TableContainer>

          <Button
            variant="text"
            onClick={handleCreate}
            startIcon={<AddIcon />}
            sx={CREATE_BUTTON_STYLES}
          >
            Создать
          </Button>

          <Menu
            anchorEl={menuAnchorEl}
            open={Boolean(menuAnchorEl)}
            onClose={closeMenu}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "right" }}
          >
            <MenuItem onClick={handleEdit}>Редактировать</MenuItem>

            <MenuItem onClick={() => deleteGoal(menuGoalId)}>
              {deletingGoalId === menuGoalId ? (
                <CircularProgress size={16} />
              ) : (
                "Удалить"
              )}
            </MenuItem>
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

      <GoalForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        streamId={streamId}
        goal={selectedGoal}
        onSaved={handleSaved}
      />
    </>
  );
};

export default GoalList;
