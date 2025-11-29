import React, { useState, useEffect, useMemo } from "react";
import {
  Tooltip,
  IconButton,
  TextField,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Button,
  CircularProgress,
  Box,
} from "@mui/material";
import {
  Close as CloseIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  ListAlt as ListAltIcon,
  ViewKanban as ViewKanbanIcon,
  Edit as EditIcon,
  ExpandMore,
  ExpandLess,
  Search as SearchIcon,
  Add as AddIcon,
} from "@mui/icons-material";
import TeamEdit from "./TeamEdit.jsx";

import {
  createProjectApi,
  fetchProjectsApi,
  updateProjectNameApi,
  deleteProjectApi,
} from "../../api/project.js";
import {
  createStreamApi,
  fetchStreamsApi,
  updateStreamNameApi,
  deleteStreamApi,
} from "../../api/stream.js";
import { fetchTeamNameApi } from "../../api/team.js";
import { useProcessError } from "../../hooks/useProcessError.js";

const Sidebar = ({ teamId }) => {
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
  const [user, setUser] = useState(null);

  const [uiProjects, setUiProjects] = useState([]);

  const getProjectColor = (id) => {
    const colors = [
      '#78F878',
      '#3A7AFE',
      '#FF6B35',
      '#9C27B0',
      '#E91E63',
      '#4CAF50',
      '#2196F3',
      '#FF9800',
    ];
    return colors[id % colors.length];
  };

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();

  useEffect(() => {
    fetchProjects();
  }, [teamId]);

  const fetchProjects = async () => {
    const response = await fetchProjectsApi(teamId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setUiProjects(response.projects);
  };

  const createProject = async () => {
    const name = newProjName.trim() || "Новый проект";
    setIsCreateProjLoading(true);

    const response = await createProjectApi(teamId, name, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    const created = await response.created;
    setUiProjects((prev) => [
      ...prev,
      { id: created.id, name: created.name, open: true, streams: [] },
    ]);

    setIsCreatingProject(false);
    setNewProjName("");
    setIsCreateProjLoading(false);
  };

  const toggleProject = (projId) => {
    const proj = uiProjects.find((p) => p.id === projId);
    const willOpen = !proj?.open;

    setUiProjects((prev) =>
      prev.map((p) => (p.id === projId ? { ...p, open: !p.open } : p)),
    );

    if (willOpen && proj && !proj.isStreamsLoaded) {
      fetchProjectStreams(projId);
    }
  };

  const createSidebarStream = async () => {
    const projId = newStreamFor;
    const name = newStreamName.trim() || "Новый стрим";
    setIsCreateStreamLoading(true);

    const response = await createStreamApi(projId, name, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    const created = await response.created;
    setUiProjects((prev) =>
      prev.map((p) =>
        p.id === projId
          ? {
            ...p,
            streams: [
              ...p.streams,
              { id: created.id, name: created.name, open: false },
            ],
          }
          : p,
      ),
    );

    setNewStreamName("");
    setNewStreamFor(null);
    setIsCreateStreamLoading(false);
  };

  const deleteStream = async (projectId, streamId) => {
    setDeletingStreamId(streamId);
    const response = await deleteStreamApi(streamId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setUiProjects((prev) =>
      prev.map((proj) =>
        proj.id === projectId
          ? { ...proj, streams: proj.streams.filter((s) => s.id !== streamId) }
          : proj,
      ),
    );
    setDeletingStreamId(null);
  };

  const toggleStream = (projectId, streamId) => {
    setUiProjects((prev) =>
      prev.map((proj) =>
        proj.id === projectId
          ? {
            ...proj,
            streams: (proj.streams || []).map((s) =>
              s.id === streamId ? { ...s, open: !s.open } : s,
            ),
          }
          : proj,
      ),
    );
  };

  const deleteProject = async (projId) => {
    setDeletingProjId(projId);
    const response = await deleteProjectApi(projId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    setUiProjects((prev) => prev.filter((proj) => proj.id !== projId));
    if (newStreamFor === projId) {
      setNewStreamFor(null);
      setNewStreamName("");
    }

    setDeletingProjId(null);
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
    const name = (editedProjName || "").trim() || `Проект ${projId}`;
    setSavingProjId(projId);

    const response = await updateProjectNameApi(projId, name, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    const updated = await response.updated;
    setUiProjects((prev) =>
      prev.map((p) => (p.id === projId ? { ...p, name: updated.name } : p)),
    );
    cancelEditProject();
    setSavingProjId(null);
  };

  const fetchProjectStreams = async (projId) => {
    setUiProjects((prev) =>
      prev.map((p) => (p.id === projId ? { ...p, isStreamsLoading: true } : p)),
    );

    const response = await fetchStreamsApi(projId, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    const data = await response.streams;
    setUiProjects((prev) =>
      prev.map((p) =>
        p.id === projId
          ? {
            ...p,
            streams: (data || []).map((s) => ({
              id: s.id,
              name: s.name,
              open: false,
            })),
            isStreamsLoaded: true,
            isStreamsLoading: false,
          }
          : p,
      ),
    );
  };

  const saveStreamName = async (projectId, streamId) => {
    const name = editedStreamName.trim() || `Стрим ${streamId}`;
    setSavingStreamId(streamId);

    const response = await updateStreamNameApi(streamId, name, token);

    if (!response.ok) {
      processError(response.status);
      return;
    }

    const updated = await response.updated;
    setUiProjects((prev) =>
      prev.map((p) =>
        p.id === projectId
          ? {
            ...p,
            streams: p.streams.map((s) =>
              s.id === streamId ? { ...s, name: updated.name } : s,
            ),
          }
          : p,
      ),
    );
    cancelEditStream();
    setSavingStreamId(null);
  };

  const startEditStream = (stream) => {
    setEditingStreamId(stream.id);
    setEditedStreamName(stream.name);
  };

  const cancelEditStream = () => {
    setEditingStreamId(null);
    setEditedStreamName("");
  };

  // TODO: перенести в профиль юзера
  useEffect(() => {
    const fetchTeamName = async () => {
      const response = await fetchTeamNameApi(teamId, token);
      if (!response.ok) {
        processError(response.status);
        return;
      }

      setTeamName(response.name);
    };

    fetchTeamName();
  }, [teamId]);

  return (
    <aside className="w-75 min-h-screen bg-[#F5F6F7] flex flex-col">
      <div className="flex items-center justify-between bg-[#F5F6F7] px-3 py-2">
        <div className="flex items-center gap-1.5">
          <div className="w-6 h-6 bg-gray-300 rounded flex items-center justify-center">
            <span className="text-sm font-semibold text-gray-600">
              {teamName ? teamName.charAt(0).toUpperCase() : 'T'}
            </span>
          </div>
          <span className="font-bold text-xl text-gray-800">{teamName}</span>
        </div>
        <div className="flex items-center gap-1">
          <Tooltip title="Поиск">
            <IconButton
              size="small"
              sx={{
                '&:hover': { backgroundColor: 'rgba(0,0,0,0.08)' }
              }}
            >
              <SearchIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Редактировать">
            <IconButton
              size="small"
              sx={{
                '&:hover': { backgroundColor: 'rgba(0,0,0,0.08)' }
              }}
              onClick={() => {
                setIsTeamEditOpen(true);
              }}
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </div>
      </div>

      <TeamEdit
        open={isTeamEditOpen}
        onClose={() => setIsTeamEditOpen(false)}
      />

      <div className="mt">
        <List disablePadding>
          <ListItem disablePadding sx={{ my: 0.2 }}>
            <Box
              sx={{
                px: 1,
                py: 1,
                borderRadius: '10px',
                mx: 1,
                border: '1px solid rgba(0, 0, 0, 0.2)',
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                width: 'calc(100% - 16px)',
                minHeight: '30px',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.05)'
                },
              }}
            >
              <SearchIcon
                sx={{
                  fontSize: 25,
                  marginLeft: '8px',
                  marginRight: '-4px',
                  color: 'rgba(0, 0, 0, 0.5)'
                }}
              />

              <Box
                sx={{
                  fontFamily: 'Montserrat, sans-serif',
                  fontWeight: 600,
                  fontSize: '1.1rem',
                  color: 'rgba(0, 0, 0, 0.45)',
                  flex: 1,
                  px: 0.1
                }}
              >
                Проект...
              </Box>
            </Box>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton
              sx={{
                px: 5.9,
                py: 0.5,
                borderRadius: '10px',
                mx: 1,
                '&:hover': {
                  backgroundColor: 'rgba(217, 217, 217, 0.8)',
                },
                '& .MuiListItemText-primary': {
                  fontFamily: 'Montserrat, sans-serif',
                  fontWeight: 400,
                  fontSize: '1.1rem'
                }
              }}
            >
              <ListItemText primary="Мои задачи" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton
              sx={{
                px: 5.9,
                py: 0.5,
                borderRadius: '10px',
                mx: 1,
                '&:hover': {
                  backgroundColor: 'rgba(217, 217, 217, 0.8)',
                },
                '& .MuiListItemText-primary': {
                  fontFamily: 'Montserrat, sans-serif',
                  fontWeight: 400,
                  fontSize: '1.1rem'
                }
              }}
            >
              <ListItemText primary="Все задачи" />
            </ListItemButton>
          </ListItem>
        </List>
      </div>

      <div className="flex items-center justify-between px-3 py-2">
        <span
          style={{
            fontFamily: 'Montserrat, sans-serif',
            fontWeight: 600,
            color: 'rgba(31, 31, 31, 0.5)',
            fontSize: '1rem'
          }}
        >
          Проекты
        </span>
        <Tooltip title="Создать проект">
          <IconButton
            size="small"
            sx={{
              '&:hover': { backgroundColor: 'rgba(0,0,0,0.04)' }
            }}
            onClick={() => {
              setNewProjName("");
              setIsCreatingProject(true);
            }}
          >
            <AddIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </div>

      {isCreatingProject && (
        <div className="px-3 py-2">
          <div className="flex items-center gap-2">
            <TextField
              size="small"
              placeholder="Название проекта"
              value={newProjName}
              sx={{ flex: 1 }}
              autoFocus
              onChange={(e) => setNewProjName(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  createProject();
                }
              }}
            />
            <IconButton
              size="small"
              onClick={async () => {
                await createProject();
              }}
            >
              {isCreateProjLoading ? (
                <CircularProgress size={20} />
              ) : (
                <SaveIcon fontSize="small" />
              )}
            </IconButton>
            <IconButton
              size="small"
              onClick={() => {
                setIsCreatingProject(false);
                setNewProjName("");
              }}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </div>
        </div>
      )}

      <List disablePadding>
        {uiProjects.map((proj) => (
          <div key={proj.id}>
            <ListItem
              disablePadding
              secondaryAction={
                <Box
                  sx={{
                    display: "flex",
                    gap: 0,
                    pr: 0,
                    alignItems: "center",
                  }}
                >
                  {editingProjId === proj.id ? (
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
                            deleteProject(proj.id);
                          }}
                        >
                          {deletingProjId === proj.id ? (
                            <CircularProgress size={20} />
                          ) : (
                            <DeleteIcon fontSize="small" />
                          )}
                        </IconButton>
                      </Tooltip>
                    </>
                  )}
                </Box>
              }
            >
              <ListItemButton
                onClick={() => toggleProject(proj.id)}
                selected={proj.open}
                sx={{
                  mx: 0,
                  my: 0,
                  borderRadius: '10px',
                  mx: 1,
                  '&:hover': {
                    backgroundColor: 'rgba(217, 217, 217, 0.8)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: '#D9D9D9',
                    '&:hover': {
                      backgroundColor: '#D9D9D9',
                    }
                  }
                }}
              >
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleProject(proj.id);
                  }}
                  sx={{
                    mr: 0,
                    ml: -2.5,
                  }}
                >
                  {proj.open ? <ExpandLess /> : <ExpandMore />}
                </IconButton>

                <ListItemIcon sx={{ minWidth: 32, mr: -0.5 }}>
                  <Box
                    sx={{
                      width: 24,
                      height: 24,
                      borderRadius: '6px',
                      backgroundColor: getProjectColor(proj.id),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      fontFamily: 'Montserrat, sans-serif',
                    }}
                  >
                    {proj.name ? proj.name.charAt(0).toUpperCase() : 'П'}
                  </Box>
                </ListItemIcon>

                {editingProjId === proj.id ? (
                  <TextField
                    size="small"
                    value={editedProjName}
                    onChange={(e) => setEditedProjName(e.target.value)}
                    autoFocus
                    inputProps={{
                      style: {
                        fontFamily: 'Montserrat, sans-serif',
                        fontWeight: 400,
                      }
                    }}
                  />
                ) : (
                  <ListItemText
                    primary={proj.name}
                    slotProps={{
                      primary: {
                        sx: {
                          fontFamily: 'Montserrat, sans-serif',
                          fontWeight: proj.open ? 700 : 400,
                          fontSize: "1.1rem"
                        }
                      },
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>

            <Collapse in={proj.open} unmountOnExit>
              <List component="div" disablePadding dense>
                <ListItem disablePadding sx={{ px: 3, py: 1, pl: 5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <span
                      style={{
                        fontFamily: 'Montserrat, sans-serif',
                        fontWeight: 600,
                        color: 'rgba(31, 31, 31, 0.5)',
                        fontSize: '0.9rem'
                      }}
                    >
                      Стримы
                    </span>
                    <Tooltip title="Добавить стрим">
                      <IconButton
                        size="small"
                        sx={{
                          '&:hover': { backgroundColor: 'rgba(0,0,0,0.04)' }
                        }}
                        onClick={() => {
                          setNewStreamName("");
                          setNewStreamFor(proj.id);
                        }}
                      >
                        <AddIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </ListItem>

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
                        <Box
                          sx={{
                            display: "flex",
                            gap: 0,
                            pr: 0,
                            alignItems: "center",
                          }}
                        >
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
                                  {savingStreamId === stream.id ? (
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
                                  {deletingStreamId === stream.id ? (
                                    <CircularProgress size={20} />
                                  ) : (
                                    <DeleteIcon fontSize="small" />
                                  )}
                                </IconButton>
                              </Tooltip>
                            </>
                          )}
                        </Box>
                      }
                      sx={{ pl: 0 }}
                    >
                      <ListItemButton
                        onClick={() => toggleStream(proj.id, stream.id)}
                        selected={stream.open}
                        sx={{
                          pr: 10,
                          mx: 2,
                          my: 0.5,
                          borderRadius: "8px",
                          "&.Mui-selected, &.Mui-selected:hover": {
                            backgroundColor: "#EDEDED",
                          },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <IconButton
                            size="small"
                            edge="start"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleStream(proj.id, stream.id);
                            }}
                          >
                            {stream.open ? <ExpandLess /> : <ExpandMore />}
                          </IconButton>
                        </ListItemIcon>

                        {editingStreamId === stream.id ? (
                          <TextField
                            size="small"
                            value={editedStreamName}
                            onChange={(e) =>
                              setEditedStreamName(e.target.value)
                            }
                            autoFocus
                            inputProps={{
                              style: {
                                fontFamily: 'Montserrat, sans-serif',
                                fontWeight: 400,
                              }
                            }}
                          />
                        ) : (
                          <ListItemText
                            primary={stream.name}
                            slotProps={{
                              primary: {
                                sx: {
                                  fontFamily: 'Montserrat, sans-serif',
                                  fontWeight: stream.open ? 700 : 400,
                                  fontSize: "1.06rem"
                                },
                              },
                            }}
                          />
                        )}
                      </ListItemButton>
                    </ListItem>

                    <Collapse in={stream.open} unmountOnExit>
                      <List component="div" disablePadding dense>
                        <ListItem disablePadding sx={{ pl: 2 }}>
                          <ListItemButton
                            component="a"
                            href={`/team/${teamId}/stream/${stream.id}`}
                            sx={{
                              borderRadius: "8px",
                              mx: 2,
                              my: 0.5,
                              '&:hover': {
                                backgroundColor: "rgba(217, 217, 217, 0.6)",
                              }
                            }}
                          >
                            <ListItemIcon sx={{ minWidth: 24 }}>
                              <ListAltIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText
                              primary="Список задач"
                              slotProps={{
                                primary: {
                                  sx: {
                                    fontFamily: 'Montserrat, sans-serif',
                                    fontWeight: 400,
                                  },
                                },
                              }}
                            />
                          </ListItemButton>
                        </ListItem>

                        <ListItem disablePadding sx={{ pl: 2 }}>
                          <ListItemButton
                            component="a"
                            href={`/team/${teamId}/stream/${stream.id}/kanban`}
                            sx={{
                              borderRadius: "8px",
                              mx: 2,
                              my: 0.5,
                              '&:hover': {
                                backgroundColor: "rgba(217, 217, 217, 0.6)",
                              }
                            }}
                          >
                            <ListItemIcon sx={{ minWidth: 24 }}>
                              <ViewKanbanIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText
                              primary="Канбан-доска"
                              slotProps={{
                                primary: {
                                  sx: {
                                    fontFamily: 'Montserrat, sans-serif',
                                    fontWeight: 400,
                                  },
                                },
                              }}
                            />
                          </ListItemButton>
                        </ListItem>
                      </List>
                    </Collapse>
                  </div>
                ))}

                {newStreamFor === proj.id && (
                  <ListItem sx={{ pl: 6 }}>
                    <div className="flex items-center w-full gap-2">
                      <TextField
                        size="small"
                        fullWidth
                        placeholder="Новый стрим"
                        value={newStreamName}
                        onChange={(e) => setNewStreamName(e.target.value)}
                        inputProps={{
                          style: {
                            fontFamily: 'Montserrat, sans-serif',
                            fontWeight: 400,
                          }
                        }}
                      />

                      <IconButton size="small" onClick={createSidebarStream}>
                        {isCreateStreamLoading ? (
                          <CircularProgress size={20} />
                        ) : (
                          <SaveIcon fontSize="small" />
                        )}
                      </IconButton>

                      <IconButton
                        size="small"
                        onClick={() => {
                          if (isCreateStreamLoading) {
                            return;
                          }
                          setNewStreamFor(null);
                          setNewStreamName("");
                        }}
                      >
                        <CloseIcon fontSize="small" />
                      </IconButton>
                    </div>
                  </ListItem>
                )}
              </List>
            </Collapse>
          </div>
        ))}
      </List>

      <div className="mt-auto p-2">
        <Button
          component="a"
          href={user ? "/profile" : "/login"}
          fullWidth
          sx={{
            justifyContent: 'flex-start',
            textTransform: 'none',
            padding: '8px 12px',
            borderRadius: '8px',
            '&:hover': {
              backgroundColor: 'rgba(217, 217, 217, 0.4)',
            }
          }}
        >
          <div className="flex items-center gap-3 w-full">
            <div
              className="w-8 h-8 bg-gray-300 flex items-center justify-center"
              style={{ borderRadius: '7px' }}
            >
              <span className="text-sm font-semibold text-gray-600">
                {user ? user.username.charAt(0).toUpperCase() : 'Л'}
              </span>
            </div>

            <div
              style={{
                fontFamily: 'Montserrat, sans-serif',
                fontWeight: 500,
                fontSize: '1rem',
                color: '#1F1F1F'
              }}
            >
              {user ? user.username : 'Личный кабинет'}
            </div>
          </div>
        </Button>
      </div>
    </aside >
  );
};

export default Sidebar;
