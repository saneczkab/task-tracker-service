import React, { useEffect, useState, useMemo } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Alert,
  TextField,
  IconButton,
  Menu,
  MenuItem,
} from "@mui/material";
import {
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Add as AddIcon,
  Save as SaveIcon,
  Close as CloseIcon,
} from "@mui/icons-material";

import {
  addUserToTeamApi,
  fetchTeamMembersApi,
  updateTeamNameApi,
  deleteUserFromTeamApi,
} from "../../api/team.js";

const SelectedTeamEdit = ({ open, onClose, teamId, onTeamUpdated }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [teamName, setTeamName] = useState("");
  const [editingName, setEditingName] = useState(false);
  const [editedName, setEditedName] = useState("");
  const [savingName, setSavingName] = useState(false);
  const [members, setMembers] = useState([]);
  const [removingUserId, setRemovingUserId] = useState(null);
  const [addUserOpen, setAddUserOpen] = useState(false);
  const [newUserEmail, setNewUserEmail] = useState("");
  const [addingUser, setAddingUser] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );

  useEffect(() => {
    if (open && teamId) {
      loadTeamMembers();
    }
  }, [open, teamId]);

  const loadTeamMembers = async () => {
    setIsLoading(true);
    setError("");

    const response = await fetchTeamMembersApi(teamId, token);

    if (!response.ok) {
      const errorMsg = response.details
        ? `Ошибка ${response.status}: ${JSON.stringify(response.details)}`
        : `Ошибка ${response.status}`;
      setError(errorMsg);
      setIsLoading(false);
      return;
    }

    setMembers(response.users);
    if (response.users.length > 0) {
      setTeamName(response.users[0].teamName || "Команда");
    }
    setIsLoading(false);
  };

  const saveTeamName = async () => {
    const name = editedName.trim() || teamName;
    setSavingName(true);
    setError("");

    const response = await updateTeamNameApi(teamId, name, token);

    if (!response.ok) {
      const errorMsg = response.details
        ? `Ошибка ${response.status}: ${JSON.stringify(response.details)}`
        : `Ошибка ${response.status}`;
      setError(errorMsg);
      setSavingName(false);
      return;
    }

    setTeamName(name);
    setEditingName(false);
    setSavingName(false);
    onTeamUpdated?.();
  };

  const startEditingName = () => {
    setError("");
    setEditingName(true);
    setEditedName(teamName);
  };

  const removeUserFromTeam = async (userEmail) => {
    setError("");
    setRemovingUserId(selectedUser.id);
    handleMenuClose();

    const response = await deleteUserFromTeamApi(teamId, userEmail, token);

    if (!response.ok) {
      const errorMsg = response.details
        ? `Ошибка ${response.status}: ${JSON.stringify(response.details)}`
        : `Ошибка ${response.status}`;
      setError(errorMsg);
      setRemovingUserId(null);
      return;
    }

    await loadTeamMembers();
    setRemovingUserId(null);
  };

  const addUserToTeam = async () => {
    const email = newUserEmail.trim();
    if (!email) return;

    setError("");
    setAddingUser(true);

    const response = await addUserToTeamApi(teamId, email, token);

    if (!response.ok) {
      const errorMsg = response.details
        ? `Ошибка ${response.status}: ${JSON.stringify(response.details)}`
        : `Ошибка ${response.status}`;
      setError(errorMsg);
      setAddingUser(false);
      return;
    }

    await loadTeamMembers();
    setNewUserEmail("");
    setAddUserOpen(false);
    setAddingUser(false);
  };

  const handleMenuOpen = (event, user) => {
    setAnchorEl(event.currentTarget);
    setSelectedUser(user);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleDeleteUser = () => {
    if (selectedUser) {
      removeUserFromTeam(selectedUser.email);
    }
  };

  return (
    <>
      <Dialog
        open={open}
        onClose={onClose}
        fullWidth
        maxWidth="sm"
        slotProps={{
          paper: {
            sx: {
              borderRadius: "12px",
              fontFamily: "Montserrat, sans-serif",
            },
          },
        }}
      >
        <DialogTitle sx={{ fontFamily: "Montserrat, sans-serif" }}>
          {editingName ? (
            <Box display="flex" alignItems="center" gap={1}>
              <TextField
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                size="small"
                autoFocus
                fullWidth
                sx={{ fontFamily: "Montserrat, sans-serif" }}
              />
              <IconButton onClick={saveTeamName} disabled={savingName}>
                {savingName ? <CircularProgress size={20} /> : <SaveIcon />}
              </IconButton>
              <IconButton onClick={() => setEditingName(false)}>
                <CloseIcon />
              </IconButton>
            </Box>
          ) : (
            <Box
              display="flex"
              alignItems="center"
              gap={1}
              sx={{
                fontFamily: "Montserrat, sans-serif",
                fontWeight: 600,
              }}
            >
              {teamName}
              <IconButton onClick={startEditingName} size="small">
                <EditIcon />
              </IconButton>
            </Box>
          )}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ minHeight: 120, mt: 1 }}>
            {isLoading && (
              <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
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
                      loadTeamMembers();
                    }}
                  >
                    Продолжить
                  </Button>
                }
              >
                {error}
              </Alert>
            )}

            {!isLoading && !error && (
              <>
                <Box
                  sx={{
                    fontFamily: "Montserrat, sans-serif",
                    fontSize: "16px",
                    mb: 2,
                  }}
                >
                  Участники команды
                </Box>

                <List>
                  {members.map((user) => (
                    <ListItem
                      key={user.id}
                      sx={{
                        border: "1px solid #E0E0E0",
                        borderRadius: "8px",
                        mb: 1,
                      }}
                      secondaryAction={
                        <IconButton
                          edge="end"
                          onClick={(e) => handleMenuOpen(e, user)}
                          disabled={removingUserId === user.id}
                        >
                          {removingUserId === user.id ? (
                            <CircularProgress size={20} />
                          ) : (
                            <MoreVertIcon />
                          )}
                        </IconButton>
                      }
                    >
                      <ListItemText
                        primary={user.nickname}
                        secondary={user.email}
                        slotProps={{
                          primary: {
                            sx: {
                              fontFamily: "Montserrat, sans-serif",
                              fontSize: "14px",
                            },
                          },
                          secondary: {
                            sx: {
                              fontFamily: "Montserrat, sans-serif",
                              fontSize: "12px",
                            },
                          },
                        }}
                      />
                    </ListItem>
                  ))}
                </List>

                <Box sx={{ mt: 2 }}>
                  {addUserOpen ? (
                    <Box display="flex" gap={1} alignItems="center">
                      <TextField
                        size="small"
                        placeholder="Email пользователя"
                        value={newUserEmail}
                        onChange={(e) => setNewUserEmail(e.target.value)}
                        fullWidth
                        sx={{ fontFamily: "Montserrat, sans-serif" }}
                      />
                      <IconButton
                        onClick={() => {
                          setAddUserOpen(false);
                          setNewUserEmail("");
                        }}
                      >
                        <CloseIcon />
                      </IconButton>
                      <IconButton onClick={addUserToTeam} disabled={addingUser}>
                        {addingUser ? (
                          <CircularProgress size={20} />
                        ) : (
                          <SaveIcon />
                        )}
                      </IconButton>
                    </Box>
                  ) : (
                    <Button
                      fullWidth
                      startIcon={<AddIcon />}
                      onClick={() => setAddUserOpen(true)}
                      sx={{
                        backgroundColor: "#E0E0E0",
                        color: "#000",
                        fontFamily: "Montserrat, sans-serif",
                        textTransform: "none",
                        "&:hover": {
                          backgroundColor: "#D0D0D0",
                        },
                      }}
                    >
                      Добавить участника
                    </Button>
                  )}
                </Box>
              </>
            )}
          </Box>
        </DialogContent>
      </Dialog>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleDeleteUser}>Удалить</MenuItem>
      </Menu>
    </>
  );
};

export default SelectedTeamEdit;
