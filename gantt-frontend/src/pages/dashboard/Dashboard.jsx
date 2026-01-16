import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import { fetchUserApi } from "../../api/user.js";
import { createTeamApi } from "../../api/team.js";
import { useProcessError } from "../../hooks/useProcessError.js";

const Dashboard = () => {
  const navigate = useNavigate();
  const processError = useProcessError();
  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );

  const [loading, setLoading] = useState(true);
  const [userTeams, setUserTeams] = useState([]);
  const [newTeamName, setNewTeamName] = useState("");
  const [creatingTeam, setCreatingTeam] = useState(false);

  useEffect(() => {
    const checkAuthAndRedirect = async () => {
      if (!token) {
        navigate("/login");
        return;
      }

      const result = await fetchUserApi(token);
      if (!result.ok) {
        processError(result.status);
        navigate("/login");
        return;
      }

      const teams = result.email.teams || [];
      setUserTeams(teams);
      setLoading(false);

      if (teams.length > 0) {
        navigate(`/team/${teams[0].id}/tasks`);
      }
    };

    checkAuthAndRedirect();
  }, [token, navigate, processError]);

  const handleCreateTeam = async () => {
    if (!newTeamName.trim()) return;

    setCreatingTeam(true);
    const result = await createTeamApi(newTeamName, token);

    if (result.ok) {
      const userResult = await fetchUserApi(token);
      if (userResult.ok) {
        const teams = userResult.email.teams || [];
        const createdTeam = teams.find((t) => t.name === newTeamName);
        if (createdTeam) {
          navigate(`/team/${createdTeam.id}/tasks`);
        }
      }
    } else {
      processError(result.status);
      setCreatingTeam(false);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (userTeams.length === 0) {
    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
          gap: 3,
          fontFamily: "Montserrat, sans-serif",
        }}
      >
        <Typography
          sx={{
            fontFamily: "Montserrat, sans-serif",
            fontSize: "24px",
            fontWeight: 600,
          }}
        >
          Создайте свою первую команду
        </Typography>
        <TextField
          placeholder="Введите название"
          value={newTeamName}
          onChange={(e) => setNewTeamName(e.target.value)}
          sx={{
            width: "400px",
            "& .MuiInputBase-input": {
              fontFamily: "Montserrat, sans-serif",
            },
          }}
          disabled={creatingTeam}
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateTeam}
          disabled={creatingTeam || !newTeamName.trim()}
          sx={{
            fontFamily: "Montserrat, sans-serif",
            textTransform: "none",
            backgroundColor: "#1976d2",
            "&:hover": {
              backgroundColor: "#1565c0",
            },
          }}
        >
          {creatingTeam ? "Создание..." : "Создать команду"}
        </Button>
      </Box>
    );
  }

  return null;
};

export default Dashboard;
