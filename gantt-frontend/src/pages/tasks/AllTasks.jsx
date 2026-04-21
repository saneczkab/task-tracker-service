import React, { useEffect, useState, useMemo, useCallback } from "react";
import { useParams } from "react-router-dom";
import { CircularProgress } from "@mui/material";
import StreamLayout from "../../components/layout/StreamLayout.jsx";
import AllTasksTable from "../../components/tasks/AllTasksTable.jsx";
import AdvancedFiltersPanel from "../../components/tasks/AdvancedFiltersPanel.jsx";
import ExportTasksButton from "../../components/ui/ExportTasksButton.jsx";
import TasksStatisticsChart from "../../components/tasks/TasksStatisticsChart.jsx";
import AISummaryButton from "../../components/tasks/AISummaryButton.jsx";
import { getTeamAnalyticsApi } from "../../api/analytics.js";
import { fetchAllUserTasksApi } from "../../api/task.js";
import { fetchUserEmailApi } from "../../api/user.js";
import { fetchStatusesApi, fetchPrioritiesApi } from "../../api/meta.js";
import { sortTasks, applyAdvancedFilters } from "../../utils/taskUtils.js";

const AllTasks = () => {
  const { teamId } = useParams();
  const [tasks, setTasks] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState("");
  const [statistics, setStatistics] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState("");

  const [sortField, setSortField] = useState("deadline");
  const [sortOrder, setSortOrder] = useState("asc");
  const [advancedFilters, setAdvancedFilters] = useState({
    searchText: "",
    assignee: [],
    team: [],
    project: [],
    stream: [],
    priority: [],
    status: [],
    tags: [],
    startDate: "",
    startDateEnd: "",
    deadline: "",
    deadlineEnd: "",
  });

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const tasksResponse = await fetchAllUserTasksApi(token);
      const emailResponse = await fetchUserEmailApi(token);
      const statusesResponse = await fetchStatusesApi();
      const prioritiesResponse = await fetchPrioritiesApi();

      setTasks(tasksResponse.ok ? tasksResponse.tasks : []);
      setUserEmail(emailResponse.ok ? emailResponse.email : "");
      setStatuses(statusesResponse.ok ? statusesResponse.statuses : []);
      setPriorities(prioritiesResponse.ok ? prioritiesResponse.priorities : []);
    } catch (error) {
      console.error("Error loading data:", error);
    }

    setLoading(false);
  }, [token]);

  useEffect(() => {
    loadData();
  }, [loadData]);

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

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  const filteredTasks = useMemo(() => {
    return applyAdvancedFilters(
      tasks,
      advancedFilters,
      statusMap,
      priorityMap,
      userEmail,
    );
  }, [tasks, advancedFilters, statusMap, priorityMap, userEmail]);

  const sortedTasks = useMemo(() => {
    return sortTasks(
      filteredTasks,
      sortField,
      sortOrder,
      statusMap,
      priorityMap,
    );
  }, [filteredTasks, sortField, sortOrder, statusMap, priorityMap]);

  const analyticsFilters = useMemo(() => {
    const params = {};

    if (advancedFilters.deadline) {
      params.start_date = advancedFilters.deadline;
    } else if (advancedFilters.startDate) {
      params.start_date = advancedFilters.startDate;
    }

    if (advancedFilters.deadlineEnd) {
      params.end_date = advancedFilters.deadlineEnd;
    } else if (advancedFilters.startDateEnd) {
      params.end_date = advancedFilters.startDateEnd;
    }

    if (advancedFilters.project.length === 1) {
      const selectedProjectName = advancedFilters.project[0];
      const matchedTask = tasks.find(
        (t) => t.project_name === selectedProjectName,
      );
      if (matchedTask?.project_id) {
        params.project_id = matchedTask.project_id;
      }
    }

    if (advancedFilters.stream.length === 1) {
      const selectedStreamName = advancedFilters.stream[0];
      const matchedTask = tasks.find(
        (t) => t.stream_name === selectedStreamName,
      );
      if (matchedTask?.stream_id) {
        params.stream_id = matchedTask.stream_id;
      }
    }

    return params;
  }, [advancedFilters, tasks]);

  useEffect(() => {
    if (!teamId || !token) {
      setStatistics(null);
      return;
    }

    let isCancelled = false;

    const loadAnalytics = async () => {
      setAnalyticsLoading(true);
      setAnalyticsError("");

      const response = await getTeamAnalyticsApi(
        teamId,
        analyticsFilters,
        token,
      );

      if (isCancelled) {
        return;
      }

      if (response.ok) {
        setStatistics(response.statistics);
      } else {
        setStatistics(null);
        setAnalyticsError("Не удалось загрузить статистику");
      }

      setAnalyticsLoading(false);
    };

    loadAnalytics();

    return () => {
      isCancelled = true;
    };
  }, [teamId, token, analyticsFilters]);

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
    <div
      className="min-h-screen flex flex-col bg-[#F5F6F7]"
      style={{ fontFamily: "Montserrat, sans-serif" }}
    >
      <div className="flex flex-1 gap-4">
        <div className="flex flex-1">
          <StreamLayout teamId={teamId} showHeader={false}>
            <h2 className="font-bold text-lg mb-4">Все задачи</h2>

            <div className="mb-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <TasksStatisticsChart
                    statistics={statistics}
                    loading={loading || analyticsLoading}
                    error={analyticsError}
                  />
                </div>
                <div className="shrink-0 flex items-start">
                  <ExportTasksButton />
                </div>
              </div>
              <div className="mt-3 flex justify-end">
                <AISummaryButton
                  tasks={sortedTasks}
                  teamId={teamId}
                  analyticsFilters={analyticsFilters}
                  token={token}
                />
              </div>
            </div>

            <AdvancedFiltersPanel
              tasks={tasks}
              onFiltersChange={setAdvancedFilters}
              statuses={statuses}
              priorities={priorities}
              currentUserEmail={userEmail}
              showTeamProjectStreamFilters={true}
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
