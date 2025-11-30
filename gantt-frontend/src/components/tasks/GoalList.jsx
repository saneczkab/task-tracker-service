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
import { MoreVert as MoreVertIcon, Add as AddIcon } from "@mui/icons-material";
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
                  <TableCell sx={HEADER_CELL_STYLES}>Название</TableCell>
                  <TableCell sx={HEADER_CELL_STYLES}>Дедлайн</TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                {goals.map((goal) => (
                  <TableRow key={goal.id} sx={GOALS_TABLE_BODY_STYLES}>
                    <TableCell sx={CELL_STYLES}>{goal.name}</TableCell>

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
