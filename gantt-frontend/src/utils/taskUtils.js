export function getContrastColor(hexColor) {
  const hex = hexColor.replace("#", "");
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? "#000000" : "#ffffff";
}

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

export const applyAdvancedFilters = (
  tasks,
  filters,
  statusMap = {},
  priorityMap = {},
  userEmail = "",
) => {
  if (!filters) return tasks;

  return tasks.filter((task) => {
    const searchText = (filters.searchText || "").toLowerCase();

    if (searchText) {
      const searchableText = [
        task.name || "",
        task.assignee_email || "",
        task.team_name || "",
        task.project_name || "",
        task.stream_name || "",
        statusMap[task.status_id] || "",
        priorityMap[task.priority_id] || "",
        (task.tag_list || []).map((task) => task.name).join(" ") || "",
      ]
        .join(" ")
        .toLowerCase();

      if (!searchableText.includes(searchText)) {
        return false;
      }
    }

    if (filters.assignee && filters.assignee.length > 0) {
      const isMyTask =
        filters.assignee.includes("__my__") &&
        task.assignee_email === userEmail;
      const isOtherAssignee = filters.assignee.some(
        (a) => a !== "__my__" && task.assignee_email === a,
      );
      if (!isMyTask && !isOtherAssignee) {
        return false;
      }
    }

    if (
      filters.team &&
      filters.team.length > 0 &&
      !filters.team.includes(task.team_name)
    ) {
      return false;
    }

    if (
      filters.project &&
      filters.project.length > 0 &&
      !filters.project.includes(task.project_name)
    ) {
      return false;
    }

    if (
      filters.stream &&
      filters.stream.length > 0 &&
      !filters.stream.includes(task.stream_name)
    ) {
      return false;
    }

    if (
      filters.priority &&
      filters.priority.length > 0 &&
      !filters.priority.includes(task.priority_id)
    ) {
      return false;
    }

    if (
      filters.status &&
      filters.status.length > 0 &&
      !filters.status.includes(task.status_id)
    ) {
      return false;
    }

    if (filters.tags && filters.tags.length > 0) {
      const taskTagIds = (task.tag_list || []).map((tag) => tag.id);
      const hasAllTags = filters.tags.some((tagId) =>
        taskTagIds.includes(tagId),
      );
      if (!hasAllTags) {
        return false;
      }
    }

    if (filters.startDate) {
      const filterDate = new Date(filters.startDate);
      const taskDate = task.start_date ? new Date(task.start_date) : null;
      if (taskDate === null || taskDate < filterDate) {
        return false;
      }
    }

    if (filters.startDateEnd) {
      const filterDate = new Date(filters.startDateEnd);
      const taskDate = task.start_date ? new Date(task.start_date) : null;
      if (taskDate === null || taskDate > filterDate) {
        return false;
      }
    }

    if (filters.deadline) {
      const filterDate = new Date(filters.deadline);
      const taskDate = task.deadline ? new Date(task.deadline) : null;
      if (taskDate === null || taskDate < filterDate) {
        return false;
      }
    }

    if (filters.deadlineEnd) {
      const filterDate = new Date(filters.deadlineEnd);
      const taskDate = task.deadline ? new Date(task.deadline) : null;
      if (taskDate === null || taskDate > filterDate) {
        return false;
      }
    }

    return true;
  });
};
