import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { CircularProgress, Table, TableHead, TableRow, TableCell, TableBody, TableContainer, Paper, IconButton,
Button, Menu, MenuItem } from "@mui/material";
import { MoreVert as MoreVertIcon }
    from '@mui/icons-material';
import GoalForm from "./GoalForm.jsx";

const GoalList = ({ streamId }) => {
    const navigate = useNavigate();
    const token = useMemo(() => window.localStorage.getItem("auth_token") || "", []);

    const [goals, setGoals] = useState([]);
    const [loading, setLoading] = useState(true);

    const [menuAnchorEl, setMenuAnchorEl] = useState(null);
    const [menuGoalId, setMenuGoalId] = useState(null);

    const [deletingGoalId, setDeletingGoalId] = useState(null);

    const [formOpen, setFormOpen] = useState(false);
    const [selectedGoal, setSelectedGoal] = useState(null);

    const fetchGoals = async () => {
        setLoading(true);

        try {
            const response = await fetch(`/api/stream/${streamId}/goals`, {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (response.status === 404) {
                navigate("/error/404");
                return;
            }

            if (!response.ok) {
                // TODO
                return;
            }

            const data = await response.json();
            setGoals(data);
        } catch {
            // TODO
        } finally {
            setLoading(false);
        }
    }

    const handleSaved = (saved) => {
        setFormOpen(false);
        setSelectedGoal(null);
        setGoals(prev => {
            const idx = prev.findIndex(g => g.id === saved.id);
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

        try {
            const response = await fetch(`/api/goal/${goalId}`, {
                method: "DELETE",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (!response.ok) {
                // TODO
                return;
            }

            setGoals((prev) => prev.filter((g) => g.id !== goalId));
        } catch {
            // TODO
        } finally {
            setDeletingGoalId(null);
        }
    };

    const handleCreate = () => {
        setSelectedGoal(null);
        setFormOpen(true);
    };

    const handleEdit = () => {
        const goal = goals.find(x => x.id === menuGoalId) || null;
        setSelectedGoal(goal);
        setFormOpen(true);
        closeMenu();
    };

    if (loading) {
        return <CircularProgress size={32} />
    }

    return (
        <>
            {
                goals.length > 0 ? (
                    <div>
                        <TableContainer
                            component={ Paper }
                            sx={{
                                borderRadius: 2,
                                overflow: 'hidden',
                                mt: 1,
                                border: "1px solid black"
                        }}>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell
                                            sx={{
                                                backgroundColor: '#EDEDED',
                                                fontWeight: 'bold',
                                                // borderRight: '1px solid rgba(0,0,0,0.12)'
                                            }}
                                        >Название
                                        </TableCell>

                                        <TableCell
                                            sx={{
                                                backgroundColor: '#EDEDED',
                                                fontWeight: 'bold',
                                                // borderRight: '1px solid rgba(0,0,0,0.12)'
                                            }}
                                        >Дедлайн
                                        </TableCell>
                                    </TableRow>
                                </TableHead>

                                <TableBody>
                                    {
                                        goals.map(goal => (
                                            <TableRow
                                                key={goal.id}
                                                sx={{
                                                    "&:hover": { backgroundColor: "#fafafa" },
                                                    "& .goal-actions": { opacity: 0, transition: "opacity 0.2s" },
                                                    "&:hover .goal-actions": { opacity: 1 },
                                                }}
                                            >
                                                <TableCell
                                                    // sx={{ borderRight: '1px solid rgba(0,0,0,0.12)' }}
                                                >
                                                    {goal.name}
                                                </TableCell>

                                                <TableCell sx={{
                                                    // borderRight: "1px solid rgba(0,0,0,0.12)",
                                                    position: "relative",
                                                    pr: 5
                                                }}>
                                                    {goal.deadline ? new Date(goal.deadline).toLocaleString() : "-"}

                                                    <IconButton
                                                        size="small"
                                                        onClick={e => openMenu(e, goal.id)}
                                                        className="goal-actions"
                                                        sx={{
                                                            position: "absolute",
                                                            right: 8,
                                                            top: "50%",
                                                            transform: "translateY(-50%)"
                                                        }}>
                                                        <MoreVertIcon fontSize="small" />
                                                    </IconButton>
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    }
                                </TableBody>
                            </Table>
                        </TableContainer>

                        <Menu
                            anchorEl={menuAnchorEl}
                            open={Boolean(menuAnchorEl)}
                            onClose={closeMenu}
                            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                        >
                            <MenuItem onClick={handleEdit}>Редактировать</MenuItem>

                            <MenuItem onClick={() => deleteGoal(menuGoalId)}>
                                {deletingGoalId === menuGoalId ? <CircularProgress size={16} /> : "Удалить"}
                            </MenuItem>
                        </Menu>

                        <div style={{ marginTop: 8, display: "flex" }}>
                            <Button variant="text" size="small" onClick={handleCreate}>
                                Добавить цель
                            </Button>
                        </div>

                    </div>
                ) : (
                    <div>Цели не заданы. Создайте цель!
                        <div style={{ marginTop: 8, display: "flex" }}>
                            <Button variant="text" size="small" onClick={handleCreate}>
                                Добавить цель
                            </Button>
                        </div>

                    </div>
                )
            }

            <GoalForm
                open={formOpen}
                onClose={() => setFormOpen(false)}
                streamId={streamId}
                goal={selectedGoal}
                onSaved={handleSaved}
            />
        </>
    )
}

export default GoalList;