import React, { Fragment, useEffect, useState, useRef } from "react";
import { Dialog, DialogTitle, DialogContent, Box, Button, CircularProgress, List, ListItem, ListItemText, Alert,
    Divider, TextField, IconButton, Collapse  } from "@mui/material";
import { Delete as DeleteIcon, ArrowForward as ArrowForwardIcon, Edit as EditIcon, Save as SaveIcon,
    People as PeopleIcon, Close as CloseIcon } from "@mui/icons-material";
import { useLocation } from "react-router-dom";

const TeamEdit = ({ open, onClose }) => {
    const location = useLocation();
    const prevPathRef = useRef(location.pathname);

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const [teams, setTeams] = useState([]);
    const [newTeamName, setNewTeamName] = useState("");
    const [deletingId, setDeletingId] = useState(null);
    const [editingId, setEditingId] = useState(null);
    const [savingId, setSavingId] = useState(null);
    const [editedName, setEditedName] = useState("");
    const [expandedTeamIds, setExpandedTeamIds] = useState(new Set());
    const [membersByTeamId, setMembersByTeamId] = useState({});
    const [removingUserByTeam, setRemovingUserByTeam] = useState({});
    const [addUserByTeam, setAddUserByTeam] = useState({});
    const [addTeam, setAddTeam] = useState({ open: false, loading: false });

    const fetchTeams = async () => {
        setIsLoading(true);
        setError("");

        try {
            const token = window.localStorage.getItem("auth_token");
            if (!token) {
                setError("Войдите в аккаунт!");
                setTeams([]);
                return;
            }

            const response = await fetch("/api/user_by_token", {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (!response.ok) {
                setError(`Ошибка ${response.status}`);
                setTeams([]);
                return;
            }

            const data = await response.json();
            setTeams(data.teams);
        } catch (e) {
            setError(`Ошибка: ${e.message}`);
            setTeams([]);
        } finally {
            setIsLoading(false);
        }
    };

    const createTeam = async () => {
        const token = window.localStorage.getItem("auth_token");
        setError("");

        let name = newTeamName;
        if (!newTeamName.trim()) {
            name = "Новая команда";
        }

        setAddTeam(prev => ({ ...prev, loading: true }));
        try{
            const response = await fetch("/api/team/new",{
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": token
                },
                body: JSON.stringify({ name })
            });

            if (!response.ok) {
                setError(`Ошибка ${response.status}`);
                return;
            }

            setNewTeamName("");
            await fetchTeams();
            setAddTeam(prev => ({ ...prev, open: false }));
        } catch (e) {
            setError(`Ошибка: ${e.message}`);
        } finally {
            setAddTeam(prev => ({ ...prev, loading: false }));
        }
    };

    const deleteTeam = async (teamId) => {
        const token = window.localStorage.getItem("auth_token");
        if (!token) {
            setError("Войдите в аккаунт!");
            setTeams([]);
            return;
        }
        setDeletingId(teamId);
        setError("");

        try {
            const response = await fetch(`/api/team/${teamId}`,{
                method: "DELETE",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (!response.ok) {
                setError(`Ошибка ${response.status}`);
                return;
            }

            await fetchTeams();
        } catch (e) {
            setError(`Ошибка: ${e.message}`);
        } finally {
            setDeletingId(null);
        }
    }

    useEffect(() => {
        if (open && prevPathRef.current !== location.pathname) {
            onClose?.();
        }
        prevPathRef.current = location.pathname;
    }, [location.pathname, open, onClose]);

    useEffect(() => {
        if (open) {
            fetchTeams();
        }
    }, [open]);

    const saveTeam = async (teamId) => {
        const token = window.localStorage.getItem("auth_token");
        let name = editedName.trim();
        if (!name) {
            name = `Команда ${teamId}`;
        }
        setSavingId(teamId);
        setError("");

        try {
            const response = await fetch(`/api/team/${teamId}`, {
                method: "PATCH",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": token
                },
                body: JSON.stringify({ name })
            });

            if (!response.ok) {
                const data = await response.json();
                setError(`Ошибка ${data?.detail}`);
                return;
            }

            setEditingId(null);
            setEditedName("");
            await fetchTeams();
        } catch (e) {
            setError(`Ошибка: ${e.message}`);
        } finally {
            setSavingId(null);
        }
    };

    const startEditing = (team) => {
        setError("");
        setEditingId(team.id);
        setEditedName(team.name);
    };

    const fetchTeamMembers = async (teamId) => {
        const token = window.localStorage.getItem("auth_token");
        setMembersByTeamId(prev => ({
            ...prev,
            [teamId]: { ...(prev[teamId] || {}), loading: true }
        }));

        try {
            const response = await fetch(`/api/team/${teamId}/users`, {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (!response.ok) {
                setError(`Ошибка ${response.status}`);
                setMembersByTeamId(prev => ({
                    ...prev,
                    [teamId]: { ...(prev[teamId] || {}), loading: false, list: [] }
                }));
                return;
            }

            const data = await response.json();
            setMembersByTeamId(prev => ({
                ...prev,
                [teamId]: { loading: false, list: data }
            }));
        } catch (e) {
            setError(`Ошибка: ${e.message}`);
            setMembersByTeamId(prev => ({
                ...prev,
                [teamId]: { ...(prev[teamId] || {}), loading: false, list: [] }
            }));
        }
    };

    const toggleMembers = (teamId) => {
        setError("");

        setExpandedTeamIds((prev) => {
            const next = new Set(prev);
            if (!next.has(teamId) && !membersByTeamId[teamId]) {
                fetchTeamMembers(teamId);
            }

            if (next.has(teamId)) {
                next.delete(teamId);
            } else {
                next.add(teamId);
            }
            return next;
        });
    };

    const removeUserFromTeam = async (teamId, userEmail) => {
        const token = window.localStorage.getItem("auth_token");
        setError("");
        setRemovingUserByTeam(prev => ({
            ...prev,
            [teamId]: userEmail
        }));

        try {
            const response = await fetch(`/api/team/${teamId}`, {
                method: "PATCH",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": token
                },
                body: JSON.stringify({ deleteUsers: [userEmail] })
            });

            if (!response.ok) {
                setError(`Ошибка ${response.status}`);
                return;
            }

            await fetchTeamMembers(teamId);
        } catch (e) {
            setError(`Ошибка: ${e.message}`);
        } finally {
            setRemovingUserByTeam(prev => ({
                ...prev,
                [teamId]: null
            }));
        }
    };

    const startAddUser = (teamId) => {
        setError("");
        setAddUserByTeam(prev => ({
            ...prev,
            [teamId]: { open: true, email: "", loading: false }
        }));
    };

    const cancelAddUser = (teamId) => {
        setAddUserByTeam(prev => ({
            ...prev,
            [teamId]: { open: false, email: "", loading: false }
        }));
    };

    const addUserToTeam = async (teamId) => {
        const token = window.localStorage.getItem("auth_token");
        const email = addUserByTeam[teamId]?.email?.trim();
        setError("");
        setAddUserByTeam(prev => ({
            ...prev,
            [teamId]: { ...(prev[teamId] || {}), loading: true }
        }));

        try {
            const response = await fetch(`/api/team/${teamId}`, {
                method: "PATCH",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": token
                },
                body: JSON.stringify({ newUsers: [email] })
            });

            if (!response.ok) {
                const data = await response.json();
                setError(`Ошибка ${data?.detail}`);
                return;
            }

            await fetchTeamMembers(teamId);
            cancelAddUser(teamId);
        } catch (e) {
            setError(`Ошибка: ${e.message}`);
        } finally {
            setAddUserByTeam(prev => ({
                ...prev,
                [teamId]: { ...(prev[teamId] || {}), loading: false }
            }));
        }
    };

    const cancelCreateTeam = () => {
        setError("");
        setAddTeam({ open: false, loading: false })
    };

    const startCreateTeam = () => {
        setNewTeamName("");
        setAddTeam({ open: true, loading: false })
    };

    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="sm"
            slotProps={{ backdrop: { sx: { backdropFilter: "blur(2px)" } } }}
        >
            <DialogTitle>Команды</DialogTitle>
            <DialogContent>
                <Box sx={{ minHeight: 120, mt: 1 }}>
                    {isLoading && (
                        <Box sx={{ display: "flex", justifyContent: "center", mt: 2}}>
                            <CircularProgress size={24} />
                        </Box>
                    )}

                    {!isLoading && error && (
                        <Alert
                            severity="error"
                            action={
                                <Button
                                    color="inherit"
                                    size="small"
                                    onClick={() => {
                                        setError("");
                                        fetchTeams();
                                    }}
                                >Продолжить
                                </Button>
                            }
                        >{error}
                        </Alert>
                    )}

                    {!isLoading && !error && (
                        <>
                        {
                            teams.length > 0 ? (
                                <List dense>
                                    {
                                        teams.map((team, idx) => (
                                            <Fragment key={team.id}>
                                                <ListItem
                                                    secondaryAction={
                                                        <Box sx={{ display: "flex", gap: 1 }}>
                                                            <IconButton
                                                                edge="end"
                                                                onClick={() => toggleMembers(team.id)}
                                                            >
                                                                <PeopleIcon fontSize="small" />
                                                            </IconButton>

                                                            <IconButton
                                                                edge="end"
                                                                component="a"
                                                                href={`/team/${team.id}`}
                                                                onClick={() => { onClose?.(); }}
                                                            >
                                                                <ArrowForwardIcon fontSize="small" />
                                                            </IconButton>

                                                            {editingId === team.id ? (
                                                                <IconButton
                                                                edge="end"
                                                                onClick={() => saveTeam(team.id)}
                                                                >
                                                                    {
                                                                        savingId === team.id
                                                                        ? <CircularProgress size={20} />
                                                                        : <SaveIcon />
                                                                    }
                                                                </IconButton>
                                                            ) : (
                                                                <IconButton
                                                                edge="end"
                                                                onClick={() => startEditing(team)}
                                                                >
                                                                    <EditIcon fontSize="small" />
                                                                </IconButton>
                                                            )}

                                                            <IconButton
                                                                edge="end"
                                                                onClick={() => deleteTeam(team.id)}
                                                                disabled={deletingId === team.id}
                                                            >
                                                                {deletingId === team.id
                                                                    ? (
                                                                        <CircularProgress size={20} />
                                                                    ) : (
                                                                        <DeleteIcon />
                                                                    )}
                                                            </IconButton>
                                                        </Box>
                                                    }>
                                                    {editingId === team.id ? (
                                                        <TextField
                                                        size="small"
                                                        value={editedName}
                                                        onChange={(e) => setEditedName(e.target.value)}
                                                        autoFocus
                                                        />
                                                        ) : (
                                                        <ListItemText primary={team.name} />
                                                    )}
                                                </ListItem>

                                                <Collapse
                                                in={expandedTeamIds.has(team.id)}
                                                unmountOnExit>
                                                    <Box
                                                    sx={{ bgcolor: "#EDEDED", px: 2, py: 1, borderRadius: 1, ml: 6, mr: 1, my: 1}}>
                                                        {membersByTeamId[team.id]?.loading && (
                                                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                                                <CircularProgress size={20} />
                                                            </Box>
                                                        )}

                                                        {membersByTeamId[team.id] && !membersByTeamId[team.id]?.loading && (
                                                            <List dense sx={{ bgcolor: "transparent", p: 0 }}>
                                                                {
                                                                    membersByTeamId[team.id].list.map((user) => (
                                                                        <ListItem
                                                                            key={user.id}
                                                                            sx={{ py: 0 }}
                                                                            secondaryAction={
                                                                                <IconButton
                                                                                    edge="end"
                                                                                    size="small"
                                                                                    onClick={() => removeUserFromTeam(team.id, user.email)}
                                                                                    >
                                                                                    {
                                                                                        removingUserByTeam[team.id] === user.id
                                                                                            ? <CircularProgress size={16} />
                                                                                            : <DeleteIcon fontSize="small" />
                                                                                    }
                                                                                </IconButton>
                                                                            }
                                                                        >
                                                                            <ListItemText
                                                                                primary={user.nickname}
                                                                                secondary={user.email}
                                                                                />
                                                                        </ListItem>
                                                                    ))
                                                                }
                                                            </List>
                                                        )}
                                                    </Box>

                                                    <Box sx={{ mt: 1, ml: 6, mr: 1, mb: 1, display: "flex", gap: 1, alignItems: "center", justifyContent: "flex-end" }}>
                                                        {addUserByTeam[team.id]?.open ? (
                                                            <>
                                                                <TextField
                                                                size="small"
                                                                lable="Email пользователя"
                                                                value={addUserByTeam[team.id].email || ""}
                                                                sx={{ flex: 1 }}
                                                                onChange={(e) =>
                                                                setAddUserByTeam(prev => ({
                                                                    ...prev,
                                                                    [team.id]: {
                                                                        ...(prev[team.id] || {}),
                                                                        email: e.target.value
                                                                    }
                                                                }))}/>

                                                                <IconButton
                                                                size="small"
                                                                edge="end"
                                                                onClick={() => cancelAddUser(team.id)}>
                                                                    <CloseIcon fontSize="small" />
                                                                </IconButton>

                                                                <IconButton
                                                                size="small"
                                                                edge="end"
                                                                onClick={() => addUserToTeam(team.id)}>
                                                                    {
                                                                        addUserByTeam[team.id]?.loading
                                                                            ? <CircularProgress size={20} />
                                                                            : <SaveIcon />
                                                                    }
                                                                </IconButton>
                                                            </>
                                                        ) : (
                                                            <Button
                                                            variant="text"
                                                            size="small"
                                                            onClick={() => startAddUser(team.id)}
                                                            >Добавить участника
                                                            </Button>
                                                        )}
                                                    </Box>

                                                </Collapse>

                                                {idx < teams.length - 1 && <Divider component="li"/>}
                                            </Fragment>
                                        ))
                                    }
                                </List>

                            ) : (
                                <Box>Нет команд. Создайте новую!</Box>
                            )
                        }

                            <Box sx={{ mt: 2, display: "flex", gap: 1, alignItems: "center", justifyContent: "flex-end" }}>
                                {
                                    addTeam.open ? (
                                    <>
                                        <TextField
                                        size="small"
                                        label="Название команды"
                                        value={newTeamName}
                                        sx={{ flex: 1 }}
                                        autoFocus
                                        onChange={(e) => setNewTeamName(e.target.value)}/>

                                        <IconButton
                                        size="small"
                                        edge="end"
                                        onClick={cancelCreateTeam}>
                                            <CloseIcon fontSize="small" />
                                        </IconButton>

                                        <IconButton
                                        size="small"
                                        edge="end"
                                        onClick={createTeam}>
                                            {
                                                addTeam.loading
                                                    ? <CircularProgress size={20} />
                                                    : <SaveIcon fontSize="small" />
                                            }
                                        </IconButton>
                                    </>
                                ) : (
                                    <Button
                                    variant="text"
                                    size="small"
                                    onClick={startCreateTeam}
                                    >Добавить команду
                                    </Button>
                                )}
                            </Box>
                        </>
                    )}
                </Box>
            </DialogContent>
        </Dialog>
    )
}

export default TeamEdit;