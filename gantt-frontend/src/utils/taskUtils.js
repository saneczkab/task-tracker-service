export const sortTasks = (
  tasks,
  sortField,
  sortOrder,
  statusMap,
  priorityMap,
) => {
  const sorted = [...tasks];

  sorted.sort((a, b) => {
    let aValue, bValue;

    switch (sortField) {
      case "name":
        aValue = (a.name || "").toLowerCase();
        bValue = (b.name || "").toLowerCase();
        break;
      case "assignee":
        aValue = (a.assignee_email || "").toLowerCase();
        bValue = (b.assignee_email || "").toLowerCase();
        break;
      case "status":
        aValue = a.status_id
          ? (statusMap[a.status_id] || "").toLowerCase()
          : "";
        bValue = b.status_id
          ? (statusMap[b.status_id] || "").toLowerCase()
          : "";
        break;
      case "priority":
        aValue = a.priority_id
          ? (priorityMap[a.priority_id] || "").toLowerCase()
          : "";
        bValue = b.priority_id
          ? (priorityMap[b.priority_id] || "").toLowerCase()
          : "";
        break;
      case "start_date":
        aValue = a.start_date ? new Date(a.start_date).getTime() : 0;
        bValue = b.start_date ? new Date(b.start_date).getTime() : 0;
        break;
      case "deadline":
        aValue = a.deadline ? new Date(a.deadline).getTime() : 0;
        bValue = b.deadline ? new Date(b.deadline).getTime() : 0;
        break;
      case "team":
        aValue = (a.team_name || "").toLowerCase();
        bValue = (b.team_name || "").toLowerCase();
        break;
      case "project":
        aValue = (a.project_name || "").toLowerCase();
        bValue = (b.project_name || "").toLowerCase();
        break;
      case "stream":
        aValue = (a.stream_name || "").toLowerCase();
        bValue = (b.stream_name || "").toLowerCase();
        break;
      default:
        return 0;
    }

    if (aValue < bValue) {
      return sortOrder === "asc" ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortOrder === "asc" ? 1 : -1;
    }

    if (sortField !== "name") {
      const na = (a.name || "").toLowerCase();
      const nb = (b.name || "").toLowerCase();
      if (na < nb) return sortOrder === "asc" ? -1 : 1;
      if (na > nb) return sortOrder === "asc" ? 1 : -1;
    }

    return 0;
  });

  return sorted;
};

export const filterTasksByTeamAndUser = (
  tasks,
  filterMode,
  teamFilter,
  userEmail,
  selectedTeamId,
) => {
  let filtered = tasks;

  if (teamFilter === "selected" && selectedTeamId) {
    filtered = filtered.filter(
      (task) => task.team_id === Number(selectedTeamId),
    );
  }

  if (filterMode === "my") {
    filtered = filtered.filter((task) => task.assignee_email === userEmail);
  }

  return filtered;
};
