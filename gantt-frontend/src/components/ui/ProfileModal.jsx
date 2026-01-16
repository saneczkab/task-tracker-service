import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  Popover,
  Box,
  Button,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Menu,
  MenuItem,
  IconButton,
  TextField,
} from "@mui/material";
import {
  Person as PersonIcon,
  Close as CloseIcon,
  MoreVert as MoreVertIcon,
  Add as AddIcon,
  Save as SaveIcon,
} from "@mui/icons-material";
import { fetchUserApi } from "../../api/user.js";
import { deleteTeamApi, createTeamApi } from "../../api/team.js";
import { useProcessError } from "../../hooks/useProcessError.js";
import SelectedTeamEdit from "./SelectedTeamEdit.jsx";

const ProfileModal = ({ open, onClose, anchorEl }) => {
  const [teams, setTeams] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [nickname, setNickname] = useState("");
  const [email, setEmail] = useState("");
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamEditOpen, setTeamEditOpen] = useState(false);
  const [createTeamOpen, setCreateTeamOpen] = useState(false);
  const [newTeamName, setNewTeamName] = useState("");
  const [creatingTeam, setCreatingTeam] = useState(false);

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();

  const loadUserData = useCallback(async () => {
    setIsLoading(true);
    const response = await fetchUserApi(token);
    if (response.ok) {
      const userData = response.email;
      setNickname(userData.nickname || "");
      setEmail(userData.email || "");
      setTeams(userData.teams || []);
    } else {
      processError(response.status);
    }
    setIsLoading(false);
  }, [token]);

  useEffect(() => {
    if (open) {
      loadUserData();
    }
  }, [open]);

  const handleMenuOpen = (event, team) => {
    event.stopPropagation();
    setMenuAnchorEl(event.currentTarget);
    setSelectedTeam(team);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleEditTeam = () => {
    handleMenuClose();
    setTeamEditOpen(true);
  };

  const handleDeleteTeam = async () => {
    if (selectedTeam) {
      const response = await deleteTeamApi(selectedTeam.id, token);
      if (response.ok) {
        await loadUserData();
      } else {
        processError(response.status);
      }
    }
    handleMenuClose();
  };

  const handleLogout = () => {
    window.localStorage.removeItem("auth_token");
    window.location.href = "/login";
  };

  const startCreateTeam = () => {
    setCreateTeamOpen(true);
    setNewTeamName("");
  };

  const cancelCreateTeam = () => {
    setCreateTeamOpen(false);
    setNewTeamName("");
  };

  const handleCreateTeam = async () => {
    const name = newTeamName.trim() || "Новая команда";
    setCreatingTeam(true);

    const response = await createTeamApi(name, token);

    if (response.ok) {
      await loadUserData();
      setCreateTeamOpen(false);
      setNewTeamName("");
    } else {
      processError(response.status);
    }

    setCreatingTeam(false);
  };

  return (
    <>
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={onClose}
        anchorOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
        slotProps={{
          paper: {
            sx: {
              borderRadius: "12px",
              padding: "24px",
              fontFamily: "Montserrat, sans-serif",
              minWidth: "320px",
              maxWidth: "400px",
              boxShadow: "0px 4px 20px rgba(0, 0, 0, 0.15)",
            },
          },
        }}
      >
        <IconButton
          onClick={onClose}
          sx={{
            position: "absolute",
            right: 8,
            top: 8,
          }}
        >
          <CloseIcon />
        </IconButton>

        {isLoading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : (
          <Box display="flex" flexDirection="column" alignItems="center">
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                backgroundColor: "#E0E0E0",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <PersonIcon sx={{ fontSize: 48, color: "#757575" }} />
            </Box>

            <Box
              sx={{
                fontFamily: "Montserrat, sans-serif",
                fontSize: "18px",
                fontWeight: 600,
              }}
            >
              {nickname}
            </Box>

            <Box
              sx={{
                fontFamily: "Montserrat, sans-serif",
                fontSize: "14px",
                color: "#757575",
              }}
            >
              {email}
            </Box>

            <Box width="100%" mt={2}>
              <Box
                sx={{
                  fontFamily: "Montserrat, sans-serif",
                  fontSize: "16px",
                  fontWeight: 600,
                  mb: 1,
                }}
              >
                Мои команды
              </Box>
              <List sx={{ padding: 0 }}>
                {teams.map((team) => (
                  <ListItem
                    key={team.id}
                    button
                    onClick={() => {
                      if (onClose) onClose();
                      window.location.href = `/team/${team.id}/tasks`;
                    }}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        onClick={(e) => handleMenuOpen(e, team)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    }
                    sx={{
                      border: "1px solid #E0E0E0",
                      borderRadius: "8px",
                      mb: 1,
                      cursor: "pointer",
                    }}
                  >
                    <ListItemText
                      primary={team.name}
                      slotProps={{
                        primary: {
                          sx: {
                            fontFamily: "Montserrat, sans-serif",
                            fontSize: "14px",
                          },
                        },
                      }}
                    />
                  </ListItem>
                ))}
              </List>

              <Box
                sx={{
                  mt: 2,
                  display: "flex",
                  gap: 1,
                  alignItems: "center",
                  justifyContent: "flex-start",
                }}
              >
                {createTeamOpen ? (
                  <>
                    <TextField
                      size="small"
                      placeholder="Название команды"
                      value={newTeamName}
                      onChange={(e) => setNewTeamName(e.target.value)}
                      autoFocus
                      sx={{
                        flex: 1,
                        "& .MuiInputBase-input": {
                          fontFamily: "Montserrat, sans-serif",
                          fontSize: "14px",
                        },
                      }}
                    />
                    <IconButton
                      size="small"
                      onClick={cancelCreateTeam}
                      disabled={creatingTeam}
                    >
                      <CloseIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={handleCreateTeam}
                      disabled={creatingTeam}
                    >
                      {creatingTeam ? (
                        <CircularProgress size={20} />
                      ) : (
                        <SaveIcon fontSize="small" />
                      )}
                    </IconButton>
                  </>
                ) : (
                  <Button
                    startIcon={<AddIcon />}
                    onClick={startCreateTeam}
                    sx={{
                      color: "#757575",
                      fontFamily: "Montserrat, sans-serif",
                      textTransform: "none",
                      fontSize: "14px",
                    }}
                  >
                    Новая команда
                  </Button>
                )}
              </Box>
            </Box>

            <Button
              fullWidth
              onClick={handleLogout}
              sx={{
                backgroundColor: "#EEF3FF",
                border: "1px solid #91B2F4",
                color: "#000",
                fontFamily: "Montserrat, sans-serif",
                textTransform: "none",
                borderRadius: "8px",
                padding: "10px",
                "&:hover": {
                  backgroundColor: "#DDE7FF",
                },
              }}
            >
              Выйти
            </Button>
          </Box>
        )}
      </Popover>

      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEditTeam}>Редактировать</MenuItem>
        <MenuItem onClick={handleDeleteTeam}>Удалить</MenuItem>
      </Menu>

      {selectedTeam && (
        <SelectedTeamEdit
          open={teamEditOpen}
          onClose={() => {
            setTeamEditOpen(false);
            setSelectedTeam(null);
          }}
          teamId={selectedTeam.id}
          onTeamUpdated={loadUserData}
        />
      )}
    </>
  );
};

export default ProfileModal;
