import React, { useEffect, useMemo, useState } from "react";
import { Box, Button, Chip, CircularProgress, Typography } from "@mui/material";
import {
  ArrowBack as ArrowBackIcon,
  CheckCircleOutline as SavedIcon,
  CloudSyncOutlined as SavingIcon,
  DeleteOutline as DeleteIcon,
  ErrorOutline as ErrorIcon,
  Schedule as PendingIcon,
} from "@mui/icons-material";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import StreamLayout from "../../components/layout/StreamLayout.jsx";
import TaskForm from "../../components/tasks/TaskForm.jsx";
import { deleteTaskApi, fetchTaskApi } from "../../api/task.js";
import { fetchPrioritiesApi, fetchStatusesApi } from "../../api/meta.js";
import { useConfirmDelete } from "../../context/ConfirmDeleteDialogContext.jsx";
import { useProcessError } from "../../hooks/useProcessError.js";

const TaskPage = () => {
  const { teamId, taskId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const processError = useProcessError();
  const { confirm } = useConfirmDelete();
  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );

  const [task, setTask] = useState(null);
  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saveState, setSaveState] = useState("saved");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const loadData = async () => {
      setLoading(true);
      const [taskResponse, statusesResponse, prioritiesResponse] =
        await Promise.all([
          fetchTaskApi(taskId, token),
          fetchStatusesApi(),
          fetchPrioritiesApi(),
        ]);

      if (cancelled) return;

      if (!taskResponse.ok) {
        processError(taskResponse.status);
        setLoading(false);
        return;
      }

      setTask(taskResponse.task);
      setStatuses(statusesResponse.ok ? statusesResponse.statuses : []);
      setPriorities(prioritiesResponse.ok ? prioritiesResponse.priorities : []);
      setLoading(false);
    };

    loadData();
    return () => {
      cancelled = true;
    };
  }, [taskId, token]);

  const defaultReturnPath = task
    ? `/team/${task.team_id}/project/${task.project_id}/stream/${task.stream_id}`
    : `/team/${teamId}/tasks`;
  const returnPath = location.state?.from || defaultReturnPath;

  const handleDelete = async () => {
    if (!(await confirm(`задачу "${task.name}"`))) return;

    setDeleting(true);
    const response = await deleteTaskApi(task.id, token);
    if (!response.ok) {
      setDeleting(false);
      processError(response.status);
      return;
    }

    navigate(returnPath, { replace: true });
  };

  const saveStatus = {
    pending: {
      label: "Есть изменения",
      icon: <PendingIcon sx={{ fontSize: 16 }} />,
      color: "default",
    },
    saving: {
      label: "Сохраняем",
      icon: <SavingIcon sx={{ fontSize: 16 }} />,
      color: "primary",
    },
    saved: {
      label: "Сохранено",
      icon: <SavedIcon sx={{ fontSize: 16 }} />,
      color: "success",
    },
    error: {
      label: "Не сохранено",
      icon: <ErrorIcon sx={{ fontSize: 16 }} />,
      color: "error",
    },
  }[saveState];

  if (loading || !task) {
    return (
      <Box className="min-h-screen flex items-center justify-center bg-[#F5F6F7]">
        <CircularProgress size={32} />
      </Box>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F6F7]">
      <div className="flex flex-1">
        <StreamLayout teamId={task.team_id} streamId={task.stream_id}>
          <Box
            sx={{
              mx: { xs: -3, md: -3 },
              mt: { xs: -3, md: -3 },
              mb: 1,
              px: { xs: 2, md: 4 },
              py: 2,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 2,
              borderBottom: "1px solid #E5E7EC",
              background:
                "linear-gradient(90deg, rgba(58,122,254,0.08), rgba(255,255,255,0) 55%)",
            }}
          >
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1.5,
                minWidth: 0,
              }}
            >
              <Button
                startIcon={<ArrowBackIcon />}
                onClick={() => navigate(returnPath)}
                sx={{ color: "#4D5568", flexShrink: 0 }}
              >
                Назад
              </Button>
              <Box sx={{ minWidth: 0, display: { xs: "none", sm: "block" } }}>
                <Typography variant="caption" color="text.secondary" noWrap>
                  {task.project_name} / {task.stream_name}
                </Typography>
                <Typography variant="body2" fontWeight={700} color="#303646">
                  {task.name}
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Chip
                size="small"
                variant="outlined"
                color={saveStatus.color}
                icon={saveStatus.icon}
                label={saveStatus.label}
                sx={{ backgroundColor: "rgba(255,255,255,0.75)" }}
              />
              <Button
                color="error"
                startIcon={
                  deleting ? <CircularProgress size={16} /> : <DeleteIcon />
                }
                onClick={handleDelete}
                disabled={deleting}
              >
                Удалить
              </Button>
            </Box>
          </Box>
          <TaskForm
            key={task.id}
            open
            pageMode
            autoSave
            streamId={task.stream_id}
            task={task}
            statuses={statuses}
            priorities={priorities}
            projectId={task.project_id}
            teamId={task.team_id}
            onSaveStateChange={setSaveState}
            skipSaveOnUnmount={deleting}
            onSaved={(savedTask) => {
              setTask((current) => ({ ...current, ...savedTask }));
            }}
          />
        </StreamLayout>
      </div>
    </div>
  );
};

export default TaskPage;
