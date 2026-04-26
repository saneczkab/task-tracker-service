import React, { useEffect, useState, useMemo, useCallback } from "react";
import { useParams } from "react-router-dom";
import { CircularProgress } from "@mui/material";
import StreamLayout from "../../components/layout/StreamLayout.jsx";
import TaskFilters from "../../components/ui/TaskFilters.jsx";
import AllTasksTable from "../../components/tasks/AllTasksTable.jsx";
import { useProcessError } from "../../hooks/useProcessError.js";
import { fetchAllUserTasksApi } from "../../api/task.js";
import { fetchUserEmailApi } from "../../api/user.js";
import { fetchTeamNameApi } from "../../api/team.js";
import { fetchStatusesApi, fetchPrioritiesApi } from "../../api/meta.js";
import { sortTasks, filterTasksByTeamAndUser } from "../../utils/taskUtils.js";

const AllTasks = () => {
  const { teamId } = useParams();
  const [tasks, setTasks] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState("");
  const [teamName, setTeamName] = useState("");

  const [filterMode, setFilterMode] = useState("all");
  const [teamFilter, setTeamFilter] = useState("selected");
  const [sortField, setSortField] = useState("deadline");
  const [sortOrder, setSortOrder] = useState("asc");

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();

  const statusMap = useMemo(() => {
    const map = {};
    statuses.forEach((s) => (map[s.id] = s.name));
    return map;
  }, [statuses]);

  const priorityMap = useMemo(() => {
    const map = {};
    priorities.forEach((p) => (map[p.id] = p.name));
    return map;
  }, [priorities]);

  const loadData = useCallback(async () => {
    setLoading(true);

    const tasksResponse = await fetchAllUserTasksApi(token);
    const emailResponse = await fetchUserEmailApi(token);
    const teamNameResponse = await fetchTeamNameApi(teamId, token);
    const statusesResponse = await fetchStatusesApi();
    const prioritiesResponse = await fetchPrioritiesApi();

    if (!tasksResponse.ok) {
      processError(tasksResponse.status);
    }

    if (!emailResponse.ok) {
      processError(emailResponse.status);
    }

    if (!teamNameResponse.ok) {
      processError(teamNameResponse.status);
    }

    if (!statusesResponse.ok) {
      processError(statusesResponse.status);
    }

    if (!prioritiesResponse.ok) {
      processError(prioritiesResponse.status);
    }

    setTasks(tasksResponse.ok ? tasksResponse.tasks : []);
    setUserEmail(emailResponse.ok ? emailResponse.email : "");
    setTeamName(teamNameResponse.ok ? teamNameResponse.name : "Команда");
    setStatuses(statusesResponse.ok ? statusesResponse.statuses : []);
    setPriorities(prioritiesResponse.ok ? prioritiesResponse.priorities : []);

    setLoading(false);
  }, [token, teamId]);

  useEffect(() => {
    loadData();
  }, []);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  const filteredTasks = useMemo(() => {
    return filterTasksByTeamAndUser(
      tasks,
      filterMode,
      teamFilter,
      userEmail,
      teamId,
    );
  }, [tasks, filterMode, teamFilter, userEmail, teamId]);

  const sortedTasks = useMemo(() => {
    return sortTasks(
      filteredTasks,
      sortField,
      sortOrder,
      statusMap,
      priorityMap,
    );
  }, [filteredTasks, sortField, sortOrder, statusMap, priorityMap]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-[#F5F6F7]">
        <div className="flex flex-1 gap-4">
          <div className="flex flex-1 p-4 items-center justify-center">
            <CircularProgress size={32} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F6F7]">
      <div className="flex flex-1 gap-4">
        <div className="flex flex-1">
          <StreamLayout teamId={teamId} showHeader={false}>
            <h2 className="font-bold text-lg mb-4">Все задачи</h2>

            <TaskFilters
              filterMode={filterMode}
              setFilterMode={setFilterMode}
              teamFilter={teamFilter}
              setTeamFilter={setTeamFilter}
              teamName={teamName}
            />

            {sortedTasks.length > 0 ? (
              <AllTasksTable
                tasks={sortedTasks}
                sortField={sortField}
                sortOrder={sortOrder}
                handleSort={handleSort}
              />
            ) : (
              <div>Нет задач</div>
            )}
          </StreamLayout>
        </div>
      </div>
    </div>
  );
};

export default AllTasks;
