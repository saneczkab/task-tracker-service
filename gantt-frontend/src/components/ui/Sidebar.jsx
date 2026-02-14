import React, { useState, useEffect } from "react";
import { Tooltip, IconButton, TextField,  List, ListItem, ListItemButton, ListItemIcon, ListItemText, Collapse,
    Button, CircularProgress, Box }
    from "@mui/material";
import {
    Close as CloseIcon, Save as SaveIcon, Delete as DeleteIcon, ListAlt as ListAltIcon,
    ViewKanban as ViewKanbanIcon, Edit as EditIcon, ExpandMore, ExpandLess
} from "@mui/icons-material";
import TeamEdit from "./TeamEdit.jsx";
import { useNavigate } from "react-router-dom";

const Sidebar = ({ teamId }) => {
    const navigate = useNavigate();

    const [isTeamEditOpen, setIsTeamEditOpen] = useState(false);
    const [teamName, setTeamName] = useState("Команда");

    const [isCreatingProject, setIsCreatingProject] = useState(false);
    const [newProjName, setNewProjName] = useState("");
    const [deletingProjId, setDeletingProjId] = useState(null);
    const [editingProjId, setEditingProjId] = useState(null);
    const [editedProjName, setEditedProjName] = useState("");
    const [savingProjId, setSavingProjId] = useState(null);
    const [isCreateProjLoading, setIsCreateProjLoading] = useState(false);

    const [newStreamName, setNewStreamName] = useState("");
    const [newStreamFor, setNewStreamFor] = useState(null);
    const [isCreateStreamLoading, setIsCreateStreamLoading] = useState(false);
    const [deletingStreamId, setDeletingStreamId] = useState(null);
    const [editingStreamId, setEditingStreamId] = useState(null);
    const [editedStreamName, setEditedStreamName] = useState("");
    const [savingStreamId, setSavingStreamId] = useState(null);

    const [uiProjects, setUiProjects] = useState([]);

    useEffect(() => {
        if (!teamId) return;
        fetchProjects();
    }, [teamId]);

    const fetchProjects = async () => {
        const token = window.localStorage.getItem("auth_token");

        try {
            const res = await fetch(`/api/team/${teamId}/projects`, {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (res.status === 404) {
                navigate("/error/404");
                return;
            }

            const text = await res.text();
            const parsed = JSON.parse(text);
            setUiProjects(parsed);
        } catch {
            // TODO
        }
    };

    const addNewProject = async () => {
        let name = newProjName.trim() || "Новый проект";
        const token = window.localStorage.getItem("auth_token");
        setIsCreateProjLoading(true);

        try {
            const response = await fetch(`/api/team/${teamId}/project/new`, {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": token
                },
                body: JSON.stringify({ name })
            });

            if (!response.ok) {
                // TODO
            }

            const created = await response.json();
            setUiProjects((prev) => [
                ...prev,
                { id: created.id, name: created.name, open: true, streams: [] }
            ]);

            setIsCreatingProject(false);
            setNewProjName("");
        } catch {
            // TODO
        } finally {
            setIsCreateProjLoading(false);
        }
    }

    const toggleProject = (projId) => {
        const proj = uiProjects.find((p) => p.id === projId);
        const willOpen = !proj?.open;

        setUiProjects((prev) =>
            prev.map((p) => (p.id === projId ? { ...p, open: !p.open } : p))
        );

        if (willOpen && proj && !proj.isStreamsLoaded) {
            fetchProjectStreams(projId);
        }
    }

    const createStream = async () => {
        const projId = newStreamFor;
        const token = window.localStorage.getItem("auth_token");
        const name = (newStreamName).trim() || "Новый стрим";
        setIsCreateStreamLoading(true);

        try {
            const response = await fetch(`/api/project/${projId}/stream/new`, {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": token
                },
                body: JSON.stringify({ name })
            });

            if (!response.ok) {
                // TODO
            }

            const created = await response.json();
            setUiProjects((prev) =>
                prev.map((p) =>
                    p.id === projId
                        ? { ...p, streams: [...p.streams, { id: created.id, name: created.name, open: false }] }
                        : p
                )
            );
            setNewStreamName("");
            setNewStreamFor(null);
        } catch {
            // TODO
        } finally {
            setIsCreateStreamLoading(false);
        }
    }

    const deleteStream = async (projectId, streamId) => {
        const token = window.localStorage.getItem("auth_token");
        setDeletingStreamId(streamId);

        try {
            const res = await fetch(`/api/stream/${streamId}`, {
                method: "DELETE",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (!res.ok) {
                // TODO
            }

            setUiProjects((prev) =>
                prev.map((proj) =>
                    proj.id === projectId
                        ? { ...proj, streams: proj.streams.filter((s) => s.id !== streamId) }
                        : proj
                )
            );
        } catch {
            // TODO
        } finally {
            setDeletingStreamId(null);
        }
    }

    const toggleStream = (projectId, streamId) => {
        setUiProjects((prev) =>
            prev.map((proj) =>
                proj.id === projectId
                    ? {
                        ...proj,
                        streams: (proj.streams || []).map((s) =>
                            s.id === streamId ? { ...s, open: !s.open } : s
                        )
                    }
                    : proj
            )
        );
    };

    const deleteProject = async (projId) => {
        const token = window.localStorage.getItem("auth_token");
        setDeletingProjId(projId);

        try {
            const response = await fetch(`/api/project/${projId}`, {
                method: "DELETE",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (!response.ok) {
                // TODO
            }

            setUiProjects((prev) => prev.filter((proj) => proj.id !== projId));
            if (newStreamFor === projId) {
                setNewStreamFor(null);
                setNewStreamName("");
            }
        } catch {
            // TODO
        } finally {
            setDeletingProjId(null);
        }
    };

    const startEditProject = (proj) => {
        setEditingProjId(proj.id);
        setEditedProjName(proj.name || "");
    };

    const cancelEditProject = () => {
        setEditingProjId(null);
        setEditedProjName("");
    };

    const saveProjectName = async (projId) => {
        const token = window.localStorage.getItem("auth_token") || "";
        const name = (editedProjName || "").trim() || `Проект ${projId}`;
        setSavingProjId(projId);

        try {
            const res = await fetch(`/api/project/${projId}`, {
                method: "PATCH",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": token
                },
                body: JSON.stringify({ name })
            });

            if (!res.ok) {
                // TODO
            }

            const updated = await res.json();
            setUiProjects((prev) =>
                prev.map((p) => (p.id === projId ? { ...p, name: updated.name } : p))
            );
            cancelEditProject();
        } catch {
            // TODO
        } finally {
            setSavingProjId(null);
        }
    };

    const fetchProjectStreams = async (projId) => {
        const token = window.localStorage.getItem("auth_token");
        setUiProjects((prev) =>
            prev.map((p) => (p.id === projId ? { ...p, isStreamsLoading: true } : p))
        );

        try {
            const res = await fetch(`/api/project/${projId}/streams`, {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (!res.ok) {
                // TODO
            }

            const data = await res.json();
            setUiProjects((prev) =>
                prev.map((p) =>
                    p.id === projId
                        ? {
                            ...p,
                            streams: (data || []).map((s) => ({
                                id: s.id,
                                name: s.name,
                                open: false
                            })),
                            isStreamsLoaded: true
                        }
                        : p
                )
            );
        } catch {
            // TODO
        } finally {
            setUiProjects((prev) =>
                prev.map((p) => (p.id === projId ? { ...p, isStreamsLoading: false } : p))
            );
        }
    };

    const saveStreamName = async (projectId, streamId) => {
        const token = window.localStorage.getItem("auth_token");
        const name = (editedStreamName).trim() || `Стрим ${streamId}`;
        setSavingStreamId(streamId);

        try {
            const res = await fetch(`/api/stream/${streamId}`, {
                method: "PATCH",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": token
                },
                body: JSON.stringify({ name })
            });

            if (!res.ok) {
                // TODO
            }

            const updated = await res.json();
            setUiProjects((prev) =>
                prev.map((p) =>
                    p.id === projectId
                        ? {
                            ...p,
                            streams: p.streams.map((s) =>
                                s.id === streamId ? { ...s, name: updated.name } : s
                            )
                        }
                        : p
                )
            );
            cancelEditStream();
        } catch {
            // TODO
        } finally {
            setSavingStreamId(null);
        }
    };

    const startEditStream = (stream) => {
        setEditingStreamId(stream.id);
        setEditedStreamName(stream.name);
    };

    const cancelEditStream = () => {
        setEditingStreamId(null);
        setEditedStreamName("");
    };

    useEffect(() => {
        if (!teamId) {
            setTeamName("Команда");
            return;
        }
        const token = window.localStorage.getItem("auth_token");
        if (!token) return;

        let mounted = true;
        fetch("/api/user_by_token", {
            method: "GET",
            headers: {
                "Accept": "application/json",
                "Authorization": token
            }
        })
            .then((res) => {
                if (!res.ok) throw new Error(`Ошибка ${res.status}`);
                return res.json();
            })
            .then((data) => {
                if (!mounted) return;
                const team = (data.teams || []).find(t => Number(t.id) === Number(teamId));
                setTeamName(team ? team.name : "Команда");
            })
            .catch(() => {
                if (mounted) setTeamName("Команда");
            });

        return () => { mounted = false; };
    }, [teamId]);

    return (
        <aside className="w-88 min-h-screen bg-white border-r border-gray-200">

            <div className="px-3 py-3">
                <div className="flex items-center justify-between bg-[#EDEDED] rounded-lg px-3 py-2">
                    <span className="font-bold text-xl">{teamName}</span>
                    <Tooltip title="Редактировать">
                        <IconButton
                            size="small"
                            onClick={() => { setIsTeamEditOpen(true) }}>
                            <EditIcon fontSize="small" />
                        </IconButton>
                    </Tooltip>
                </div>
            </div>

            <TeamEdit
                open={isTeamEditOpen}
                onClose={() => setIsTeamEditOpen(false)}
            />

            <div className="flex items-center justify-between px-3 py-2">
                <span className="font-bold text-lg">Проекты</span>
            </div>

            <List disablePadding>
                {uiProjects.map((proj) => (
                    <div key={proj.id}>
                        <ListItem disablePadding
                        secondaryAction={
                            <Box sx={{ display: "flex", gap: 1, pr: 1, alignItems: "center" }}>
                                {
                                    editingProjId === proj.id ? (
                                        <>
                                            <Tooltip title="Сохранить">
                                                <IconButton
                                                    edge="end"
                                                    size="small"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        saveProjectName(proj.id);
                                                    }}
                                                >
                                                    {savingProjId === proj.id ? (
                                                        <CircularProgress size={20} />
                                                    ) : (
                                                        <SaveIcon fontSize="small" />
                                                    )}
                                                </IconButton>
                                            </Tooltip>

                                            <Tooltip title="Отменить">
                                                <IconButton
                                                    edge="end"
                                                    size="small"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        cancelEditProject();
                                                    }}
                                                >
                                                    <CloseIcon fontSize="small" />
                                                </IconButton>
                                            </Tooltip>
                                        </>
                                    ) : (
                                        <>
                                            <Tooltip title="Переименовать проект">
                                                <IconButton
                                                    edge="end"
                                                    size="small"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        startEditProject(proj);
                                                    }}
                                                >
                                                    <EditIcon fontSize="small" />
                                                </IconButton>
                                            </Tooltip>

                                            <Tooltip title="Удалить проект">
                                                <IconButton
                                                    edge="end"
                                                    size="small"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        deleteProject(proj.id)
                                                    }}
                                                >
                                                    {deletingProjId === proj.id ? (
                                                        <CircularProgress size={20} />
                                                    ) : (
                                                        <DeleteIcon fontSize="small"/>
                                                    )}
                                                </IconButton>
                                            </Tooltip>
                                        </>
                                    )
                                }
                            </Box>
                        }>
                            <ListItemButton
                                onClick={() => toggleProject(proj.id)}
                                selected={proj.open}
                                sx={{
                                    mx: 1,
                                    my: 0.5,
                                    borderRadius: "8px",
                                    '&.Mui-selected, &.Mui-selected:hover': { backgroundColor: "#EDEDED" }
                                }}>

                                <ListItemIcon sx={{ minWidth: 32 }}>
                                    <IconButton
                                        size="small"
                                        edge="start"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            toggleProject(proj.id);
                                        }}
                                    >
                                        {proj.open ? <ExpandLess /> : <ExpandMore />}
                                    </IconButton>
                                </ListItemIcon>

                                {editingProjId === proj.id ? (
                                    <TextField
                                        size="small"
                                        value={editedProjName}
                                        onChange={(e) => setEditedProjName(e.target.value)}
                                        autoFocus
                                    />
                                ) : (
                                    <ListItemText
                                        primary={proj.name}
                                        slotProps={{ primary: { sx: { fontWeight: 700, fontSize: "1rem" } } }}/>
                                )}
                            </ListItemButton>
                        </ListItem>

                        <Collapse in={proj.open} unmountOnExit>
                            <List component="div" disablePadding dense>
                                {proj.isStreamsLoading && (
                                    <ListItem sx={{ pl: 6 }}>
                                        <CircularProgress size={20} />
                                    </ListItem>
                                )}

                                {(proj.streams || []).map((stream) => (
                                    <div key={stream.id}>
                                        <ListItem
                                            disablePadding
                                            secondaryAction={
                                                <Box sx={{ display: "flex", gap: 1, pr: 1, alignItems: "center" }}>
                                                    {editingStreamId === stream.id ? (
                                                        <>
                                                            <Tooltip title="Сохранить">
                                                                <IconButton
                                                                    edge="end"
                                                                    size="small"
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        saveStreamName(proj.id, stream.id);
                                                                    }}
                                                                >
                                                                    {
                                                                        savingStreamId === stream.id ? (
                                                                            <CircularProgress size={20} />
                                                                        ) : (
                                                                            <SaveIcon fontSize="small" />
                                                                        )
                                                                    }
                                                                </IconButton>
                                                            </Tooltip>
                                                            <Tooltip title="Отменить">
                                                                <IconButton
                                                                    edge="end"
                                                                    size="small"
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        cancelEditStream();
                                                                    }}
                                                                >
                                                                    <CloseIcon fontSize="small" />
                                                                </IconButton>
                                                            </Tooltip>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <Tooltip title="Переименовать стрим">
                                                                <IconButton
                                                                    edge="end"
                                                                    size="small"
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        startEditStream(stream);
                                                                    }}
                                                                >
                                                                    <EditIcon fontSize="small" />
                                                                </IconButton>
                                                            </Tooltip>
                                                            <Tooltip title="Удалить стрим">
                                                                <IconButton
                                                                    edge="end"
                                                                    size="small"
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        deleteStream(proj.id, stream.id);
                                                                    }}
                                                                >
                                                                    {
                                                                        deletingStreamId === stream.id ? (
                                                                            <CircularProgress size={20} />
                                                                        ) : (
                                                                            <DeleteIcon fontSize="small" />
                                                                        )
                                                                    }
                                                                </IconButton>
                                                            </Tooltip>
                                                        </>
                                                    )}
                                                </Box>
                                            }
                                            sx={{ pl: 2 }}
                                        >
                                            <ListItemButton
                                                onClick={() => toggleStream(proj.id, stream.id)}
                                                selected={stream.open}
                                                sx={{
                                                    pr: 10,
                                                    mx: 2,
                                                    my: 0.5,
                                                    borderRadius: "8px",
                                                    '&.Mui-selected, &.Mui-selected:hover': { backgroundColor: "#EDEDED" }
                                                }}
                                            >
                                                <ListItemIcon sx={{ minWidth: 32 }}>
                                                    <IconButton
                                                        size="small"
                                                        edge="start"
                                                        onClick={(e) => { e.stopPropagation(); toggleStream(proj.id, stream.id); }}
                                                    >
                                                        {stream.open ? <ExpandLess /> : <ExpandMore />}
                                                    </IconButton>
                                                </ListItemIcon>

                                                {editingStreamId === stream.id ? (
                                                    <TextField
                                                        size="small"
                                                        value={editedStreamName}
                                                        onChange={(e) => setEditedStreamName(e.target.value)}
                                                        autoFocus
                                                    />
                                                ) : (
                                                    <ListItemText
                                                        primary={stream.name}
                                                        slotProps={{ primary: { sx: { fontWeight: 700, fontSize: "1rem" } } }}
                                                    />
                                                )}
                                            </ListItemButton>
                                        </ListItem>

                                        <Collapse in={stream.open} unmountOnExit>
                                            <List component="div" disablePadding dense>
                                                <ListItem disablePadding sx={{ pl: 4 }}>
                                                    <ListItemButton component="a" href={`/team/${teamId}/stream/${stream.id}`}>
                                                        <ListItemIcon>
                                                            <ListAltIcon fontSize="small" />
                                                        </ListItemIcon>
                                                        <ListItemText primary="Список задач" />
                                                    </ListItemButton>
                                                </ListItem>

                                                <ListItem disablePadding sx={{ pl: 4 }}>
                                                    <ListItemButton component="a" href={`/team/${teamId}/stream/${stream.id}/kanban`}>
                                                        <ListItemIcon>
                                                            <ViewKanbanIcon fontSize="small" />
                                                        </ListItemIcon>
                                                        <ListItemText primary="Канбан-доска" />
                                                    </ListItemButton>
                                                </ListItem>
                                            </List>

                                        </Collapse>
                                    </div>
                                ))}

                                {
                                    newStreamFor === proj.id ? (
                                        <ListItem sx = {{ pl: 6 }}>
                                            <div className="flex items-center w-full gap-2">
                                                <TextField
                                                    size="small"
                                                    fullWidth
                                                    placeholder="Новый стрим"
                                                    value={newStreamName}
                                                    onChange={(e) => setNewStreamName(e.target.value)}
                                                />

                                                <IconButton
                                                    size="small"
                                                    onClick={createStream}>
                                                    {
                                                        isCreateStreamLoading ? (
                                                            <CircularProgress size={20} />
                                                        ) : (
                                                            <SaveIcon fontSize="small"/>
                                                        )
                                                    }
                                                </IconButton>

                                                <IconButton
                                                    size="small"
                                                    onClick={() => {
                                                        if (isCreateStreamLoading) {
                                                            return;
                                                        }
                                                        setNewStreamFor(null);
                                                        setNewStreamName("");
                                                    }}>
                                                    <CloseIcon fontSize="small"/>
                                                </IconButton>
                                            </div>
                                        </ListItem>
                                    ) : (
                                        <ListItem sx={{ pl: 6 }}>
                                            <Button
                                                variant="text"
                                                size="small"
                                                onClick={() => {
                                                    setNewStreamName("");
                                                    setNewStreamFor(proj.id);
                                                }}
                                                sx={{ ml: "auto" }}
                                            >
                                                Добавить стрим
                                            </Button>
                                        </ListItem>
                                    )
                                }
                            </List>
                        </Collapse>

                    </div>
                ))}

            </List>

            <div className="px-3 py-2 flex items-center justify-end gap-2">
                {
                    isCreatingProject ? (
                        <>
                            <TextField
                                size="small"
                                label="Название проекта"
                                value={newProjName}
                                sx={{ flex: 1 }}
                                autoFocus
                                onChange={(e) => setNewProjName(e.target.value)}
                            />

                            <IconButton
                                size="small"
                                edge="end"
                                onClick={async () => { await addNewProject(); }}
                            >
                                {
                                    isCreateProjLoading ? (
                                        <CircularProgress size={20} />
                                    ) : (
                                        <SaveIcon fontSize="small" />
                                    )
                                }
                            </IconButton>

                            <IconButton
                                size="small"
                                edge="end"
                                onClick={() => {
                                    setIsCreatingProject(false);
                                    setNewProjName("");
                                }}
                            >
                                <CloseIcon fontSize="small" />
                            </IconButton>
                        </>
                    ) : (
                        <Button
                            variant="text"
                            size="small"
                            onClick={() => {
                                setNewProjName("");
                                setIsCreatingProject(true);
                            }}
                        >Создать проект
                        </Button>
                    )
                }

            </div>

        </aside>
    )
}

export default Sidebar;