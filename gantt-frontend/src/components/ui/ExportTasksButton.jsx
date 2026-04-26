import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  Button,
  Menu,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  CircularProgress,
  Checkbox,
  ListItemText,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import { fetchTeamsApi } from "../../api/team.js";
import { fetchProjectsApi } from "../../api/project.js";
import { fetchStreamsApi } from "../../api/stream.js";
import { exportCalendarApi } from "../../api/calendar.js";

const ExportTasksButton = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const [scope, setScope] = useState("my");
  const [selectedTeams, setSelectedTeams] = useState([]);
  const [selectedProjects, setSelectedProjects] = useState([]);
  const [selectedStreams, setSelectedStreams] = useState([]);

  const [teams, setTeams] = useState([]);
  const [projects, setProjects] = useState([]);
  const [streams, setStreams] = useState([]);

  const [loadingTeams, setLoadingTeams] = useState(false);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [loadingStreams, setLoadingStreams] = useState(false);
  const [exporting, setExporting] = useState(false);

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const loadTeams = useCallback(async () => {
    setLoadingTeams(true);
    const res = await fetchTeamsApi(token);
    if (res.ok) {
      setTeams(res.teams);
    }
    setLoadingTeams(false);
  }, [token]);

  useEffect(() => {
    if (open && teams.length === 0) {
      loadTeams();
    }
  }, [open, teams.length, loadTeams]);

  useEffect(() => {
    if (selectedTeams.length > 0) {
      setLoadingProjects(true);
      Promise.all(
        selectedTeams.map((tId) => fetchProjectsApi(tId, token)),
      ).then((results) => {
        let allProjects = [];
        results.forEach((res) => {
          if (res.ok) allProjects = [...allProjects, ...res.projects];
        });
        setProjects(allProjects);
        setLoadingProjects(false);
      });
      setSelectedProjects([]);
      setSelectedStreams([]);
      setStreams([]);
    } else {
      setProjects([]);
      setSelectedProjects([]);
      setSelectedStreams([]);
      setStreams([]);
    }
  }, [selectedTeams, token]);

  useEffect(() => {
    if (selectedProjects.length > 0) {
      setLoadingStreams(true);
      Promise.all(
        selectedProjects.map((pId) => fetchStreamsApi(pId, token)),
      ).then((results) => {
        let allStreams = [];
        results.forEach((res) => {
          if (res.ok) allStreams = [...allStreams, ...res.streams];
        });
        setStreams(allStreams);
        setLoadingStreams(false);
      });
      setSelectedStreams([]);
    } else {
      setStreams([]);
      setSelectedStreams([]);
    }
  }, [selectedProjects, token]);

  const handleExport = async () => {
    setExporting(true);
    let payload = {};
    if (selectedStreams.length > 0) {
      payload = { target: "streams", target_ids: selectedStreams };
    } else if (selectedProjects.length > 0) {
      payload = { target: "projects", target_ids: selectedProjects };
    } else if (selectedTeams.length > 0) {
      payload = { target: "teams", target_ids: selectedTeams };
    } else {
      payload = { target: "all" };
    }

    await exportCalendarApi(scope, payload, token);
    setExporting(false);
    handleClose();
  };

  return (
    <>
      <Button
        variant="text"
        sx={{
          textTransform: "none",
          borderRadius: "8px",
          color: "#1976d2",
          fontWeight: 500,
          "&:hover": {
            backgroundColor: "transparent",
            textDecoration: "underline",
          },
        }}
        startIcon={<DownloadIcon />}
        onClick={handleClick}
      >
        Экспорт задач
      </Button>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "export-button",
        }}
        PaperProps={{
          style: {
            width: "300px",
            padding: "16px",
          },
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <FormControl component="fieldset">
            <RadioGroup
              row
              value={scope}
              onChange={(e) => setScope(e.target.value)}
            >
              <FormControlLabel
                value="my"
                control={<Radio />}
                label="Назначенные мне"
              />
              <FormControlLabel
                value="all"
                control={<Radio />}
                label="Все задачи"
              />
            </RadioGroup>
          </FormControl>

          <FormControl fullWidth size="small">
            <InputLabel>Выбрать команды</InputLabel>
            <Select
              multiple
              variant="outlined"
              value={selectedTeams}
              label="Выбрать команды"
              onChange={(e) => setSelectedTeams(e.target.value)}
              renderValue={(selected) =>
                selected
                  .map((id) => teams.find((t) => t.id === id)?.name)
                  .join(", ")
              }
            >
              {loadingTeams ? (
                <MenuItem disabled>
                  <CircularProgress size={20} />
                </MenuItem>
              ) : (
                teams.map((t) => (
                  <MenuItem key={t.id} value={t.id}>
                    <Checkbox checked={selectedTeams.indexOf(t.id) > -1} />
                    <ListItemText primary={t.name} />
                  </MenuItem>
                ))
              )}
            </Select>
          </FormControl>

          {selectedTeams.length > 0 && (
            <FormControl fullWidth size="small">
              <InputLabel>Выбрать проекты</InputLabel>
              <Select
                multiple
                variant="outlined"
                value={selectedProjects}
                label="Выбрать проекты"
                onChange={(e) => setSelectedProjects(e.target.value)}
                renderValue={(selected) =>
                  selected
                    .map((id) => projects.find((p) => p.id === id)?.name)
                    .join(", ")
                }
              >
                {loadingProjects ? (
                  <MenuItem disabled>
                    <CircularProgress size={20} />
                  </MenuItem>
                ) : (
                  projects.map((p) => (
                    <MenuItem key={p.id} value={p.id}>
                      <Checkbox checked={selectedProjects.indexOf(p.id) > -1} />
                      <ListItemText primary={p.name} />
                    </MenuItem>
                  ))
                )}
              </Select>
            </FormControl>
          )}

          {selectedProjects.length > 0 && (
            <FormControl fullWidth size="small">
              <InputLabel>Выбрать стримы</InputLabel>
              <Select
                multiple
                variant="outlined"
                value={selectedStreams}
                label="Выбрать стримы"
                onChange={(e) => setSelectedStreams(e.target.value)}
                renderValue={(selected) =>
                  selected
                    .map((id) => streams.find((s) => s.id === id)?.name)
                    .join(", ")
                }
              >
                {loadingStreams ? (
                  <MenuItem disabled>
                    <CircularProgress size={20} />
                  </MenuItem>
                ) : (
                  streams.map((s) => (
                    <MenuItem key={s.id} value={s.id}>
                      <Checkbox checked={selectedStreams.indexOf(s.id) > -1} />
                      <ListItemText primary={s.name} />
                    </MenuItem>
                  ))
                )}
              </Select>
            </FormControl>
          )}

          <Button
            variant="text"
            sx={{
              textTransform: "none",
              borderRadius: "8px",
              color: "#1976d2",
              fontWeight: 500,
              "&:hover": {
                backgroundColor: "transparent",
                textDecoration: "underline",
              },
            }}
            fullWidth
            onClick={handleExport}
            disabled={exporting}
          >
            {exporting ? <CircularProgress size={24} /> : "Скачать"}
          </Button>
        </div>
      </Menu>
    </>
  );
};

export default ExportTasksButton;
