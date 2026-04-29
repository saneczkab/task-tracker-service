import React, { useEffect, useMemo, useRef, useState } from "react";
import { Search as SearchIcon, Close as CloseIcon } from "@mui/icons-material";

const EMPTY_FILTERS = {
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
};

const AdvancedFiltersPanel = ({
  tasks,
  onFiltersChange,
  statuses,
  priorities,
  currentUserEmail = "",
  showTeamProjectStreamFilters = false,
  initialFilters = null,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState(EMPTY_FILTERS);
  const [openDropdowns, setOpenDropdowns] = useState({});
  const [searchInputs, setSearchInputs] = useState({
    assignee: "",
    priority: "",
    status: "",
    tags: "",
    team: "",
    project: "",
    stream: "",
  });

  const dropdownRefs = useRef({});
  const didInitRef = useRef(false);

  const uniqueAssignees = useMemo(() => {
    const assignees = new Set();
    tasks.forEach((task) => {
      if (task.assignee_email) {
        assignees.add(task.assignee_email);
      }
    });
    return Array.from(assignees).sort();
  }, [tasks]);

  const uniqueTeams = useMemo(() => {
    const teams = new Set();
    tasks.forEach((task) => {
      if (task.team_name) {
        teams.add(task.team_name);
      }
    });
    return Array.from(teams).sort();
  }, [tasks]);

  const uniqueProjects = useMemo(() => {
    const projects = new Set();
    tasks.forEach((task) => {
      if (task.project_name) {
        projects.add(task.project_name);
      }
    });
    return Array.from(projects).sort();
  }, [tasks]);

  const uniqueStreams = useMemo(() => {
    const streams = new Set();
    tasks.forEach((task) => {
      if (task.stream_name) {
        streams.add(task.stream_name);
      }
    });
    return Array.from(streams).sort();
  }, [tasks]);

  const uniqueTags = useMemo(() => {
    const tags = {};
    tasks.forEach((task) => {
      if (Array.isArray(task.tag_list)) {
        task.tag_list.forEach((tag) => {
          if (!tags[tag.id]) {
            tags[tag.id] = { id: tag.id, name: tag.name, color: tag.color };
          }
        });
      }
    });
    return Object.values(tags).sort((a, b) => a.name.localeCompare(b.name));
  }, [tasks]);

  const filteredAssignees = useMemo(
    () =>
      uniqueAssignees.filter((x) =>
        x.toLowerCase().includes(searchInputs.assignee.toLowerCase()),
      ),
    [uniqueAssignees, searchInputs.assignee],
  );
  const filteredTeams = useMemo(
    () =>
      uniqueTeams.filter((x) =>
        x.toLowerCase().includes(searchInputs.team.toLowerCase()),
      ),
    [uniqueTeams, searchInputs.team],
  );
  const filteredProjects = useMemo(
    () =>
      uniqueProjects.filter((x) =>
        x.toLowerCase().includes(searchInputs.project.toLowerCase()),
      ),
    [uniqueProjects, searchInputs.project],
  );
  const filteredStreams = useMemo(
    () =>
      uniqueStreams.filter((x) =>
        x.toLowerCase().includes(searchInputs.stream.toLowerCase()),
      ),
    [uniqueStreams, searchInputs.stream],
  );
  const filteredPriorities = useMemo(
    () =>
      priorities.filter((x) =>
        x.name.toLowerCase().includes(searchInputs.priority.toLowerCase()),
      ),
    [priorities, searchInputs.priority],
  );
  const filteredStatuses = useMemo(
    () =>
      statuses.filter((x) =>
        x.name.toLowerCase().includes(searchInputs.status.toLowerCase()),
      ),
    [statuses, searchInputs.status],
  );
  const filteredTags = useMemo(
    () =>
      uniqueTags.filter((x) =>
        x.name.toLowerCase().includes(searchInputs.tags.toLowerCase()),
      ),
    [uniqueTags, searchInputs.tags],
  );

  useEffect(() => {
    const handleClickOutside = (event) => {
      Object.keys(dropdownRefs.current).forEach((key) => {
        if (
          dropdownRefs.current[key] &&
          !dropdownRefs.current[key].contains(event.target)
        ) {
          setOpenDropdowns((prev) => ({ ...prev, [key]: false }));
        }
      });
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (didInitRef.current) return;
    if (!initialFilters) return;
    didInitRef.current = true;
    setSelectedFilters(initialFilters);
    onFiltersChange(initialFilters);
  }, [initialFilters, onFiltersChange]);

  const pushFilters = (next) => {
    setSelectedFilters(next);
    onFiltersChange(next);
  };

  const handleFilterChange = (name, value) => {
    pushFilters({ ...selectedFilters, [name]: value });
  };

  const handleMultiSelectChange = (name, value) => {
    const current = selectedFilters[name] || [];
    const updated = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    handleFilterChange(name, updated);
  };

  const resetSpecificFilter = (name) => {
    const next = { ...selectedFilters };
    if (
      [
        "priority",
        "status",
        "tags",
        "assignee",
        "team",
        "project",
        "stream",
      ].includes(name)
    ) {
      next[name] = [];
    } else if (name === "startDate") {
      next.startDate = "";
      next.startDateEnd = "";
    } else if (name === "deadline") {
      next.deadline = "";
      next.deadlineEnd = "";
    } else {
      next[name] = "";
    }
    pushFilters(next);
  };

  const toggleDropdown = (name) => {
    setOpenDropdowns((prev) => ({ ...prev, [name]: !prev[name] }));
  };

  const closeAllDropdowns = () => setOpenDropdowns({});

  const clearAllFilters = () => {
    pushFilters(EMPTY_FILTERS);
    setSearchInputs({
      assignee: "",
      priority: "",
      status: "",
      tags: "",
      team: "",
      project: "",
      stream: "",
    });
  };

  const hasActiveFilters = Object.values(selectedFilters).some(
    (value) =>
      (Array.isArray(value) && value.length > 0) ||
      (typeof value === "string" && value),
  );

  const getSelectedCount = (name) => {
    if (name === "startDateRange") {
      return [selectedFilters.startDate, selectedFilters.startDateEnd].filter(
        Boolean,
      ).length;
    }
    if (name === "deadlineRange") {
      return [selectedFilters.deadline, selectedFilters.deadlineEnd].filter(
        Boolean,
      ).length;
    }
    const value = selectedFilters[name];
    if (Array.isArray(value)) {
      return value.length;
    }
    return value ? 1 : 0;
  };

  const getLabel = (title, name) => `${title} (${getSelectedCount(name)})`;

  return (
    <div className="mb-4">
      <button
        type="button"
        onClick={() => {
          setIsOpen((prev) => !prev);
          if (isOpen) {
            closeAllDropdowns();
          }
        }}
        className="mb-2 bg-transparent border-none text-blue-600 hover:text-blue-700 font-medium"
      >
        Фильтры
      </button>

      {isOpen && (
        <div className="space-y-1">
          <div className="relative w-1/4 mb-2">
            <SearchIcon
              sx={{
                position: "absolute",
                left: 10,
                top: "50%",
                transform: "translateY(-50%)",
                fontSize: 18,
                color: "text.secondary",
              }}
            />
            <input
              type="text"
              placeholder="Поиск..."
              value={selectedFilters.searchText}
              onChange={(e) => handleFilterChange("searchText", e.target.value)}
              className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          <div className="relative" style={{ overflow: "visible" }}>
            <div className="flex items-center gap-2 flex-wrap">
              <div
                className="relative whitespace-nowrap"
                ref={(el) => (dropdownRefs.current.assignee = el)}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown("assignee")}
                  className="px-3 py-1 bg-gray-200 border-none rounded-md text-sm font-bold text-gray-700 hover:bg-gray-300 text-left"
                >
                  {getLabel("Исполнитель", "assignee")}
                </button>
                {openDropdowns.assignee && (
                  <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-72">
                    <div className="flex items-center border-b border-gray-200 px-2 py-1">
                      <input
                        type="text"
                        placeholder="Поиск исполнителя..."
                        value={searchInputs.assignee}
                        onChange={(e) =>
                          setSearchInputs((prev) => ({
                            ...prev,
                            assignee: e.target.value,
                          }))
                        }
                        className="w-full text-sm focus:outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => resetSpecificFilter("assignee")}
                        className="text-gray-500 hover:text-gray-700"
                        title="Сбросить фильтр"
                      >
                        <CloseIcon sx={{ fontSize: 16 }} />
                      </button>
                    </div>
                    <div className="max-h-52 overflow-y-auto">
                      {currentUserEmail && (
                        <label className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100">
                          <input
                            type="checkbox"
                            checked={selectedFilters.assignee.includes(
                              "__my__",
                            )}
                            onChange={() =>
                              handleMultiSelectChange("assignee", "__my__")
                            }
                          />
                          <span>Назначенные мне</span>
                        </label>
                      )}
                      {filteredAssignees.map((assignee) => (
                        <label
                          key={assignee}
                          className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100"
                        >
                          <input
                            type="checkbox"
                            checked={selectedFilters.assignee.includes(
                              assignee,
                            )}
                            onChange={() =>
                              handleMultiSelectChange("assignee", assignee)
                            }
                          />
                          <span>{assignee}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {showTeamProjectStreamFilters && (
                <div
                  className="relative whitespace-nowrap"
                  ref={(el) => (dropdownRefs.current.team = el)}
                >
                  <button
                    type="button"
                    onClick={() => toggleDropdown("team")}
                    className="px-3 py-1 bg-gray-200 border-none rounded-md text-sm font-bold text-gray-700 hover:bg-gray-300 text-left"
                  >
                    {getLabel("Команда", "team")}
                  </button>
                  {openDropdowns.team && (
                    <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-60">
                      <div className="flex items-center border-b border-gray-200 px-2 py-1">
                        <input
                          type="text"
                          placeholder="Поиск команды..."
                          value={searchInputs.team}
                          onChange={(e) =>
                            setSearchInputs((prev) => ({
                              ...prev,
                              team: e.target.value,
                            }))
                          }
                          className="w-full text-sm focus:outline-none"
                        />
                        <button
                          type="button"
                          onClick={() => resetSpecificFilter("team")}
                          className="text-gray-500 hover:text-gray-700"
                          title="Сбросить фильтр"
                        >
                          <CloseIcon sx={{ fontSize: 16 }} />
                        </button>
                      </div>
                      <div className="max-h-52 overflow-y-auto">
                        {filteredTeams.map((team) => (
                          <label
                            key={team}
                            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100"
                          >
                            <input
                              type="checkbox"
                              checked={selectedFilters.team.includes(team)}
                              onChange={() =>
                                handleMultiSelectChange("team", team)
                              }
                            />
                            <span>{team}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {showTeamProjectStreamFilters && (
                <div
                  className="relative whitespace-nowrap"
                  ref={(el) => (dropdownRefs.current.project = el)}
                >
                  <button
                    type="button"
                    onClick={() => toggleDropdown("project")}
                    className="px-3 py-1 bg-gray-200 border-none rounded-md text-sm font-bold text-gray-700 hover:bg-gray-300 text-left"
                  >
                    {getLabel("Проект", "project")}
                  </button>
                  {openDropdowns.project && (
                    <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-60">
                      <div className="flex items-center border-b border-gray-200 px-2 py-1">
                        <input
                          type="text"
                          placeholder="Поиск проекта..."
                          value={searchInputs.project}
                          onChange={(e) =>
                            setSearchInputs((prev) => ({
                              ...prev,
                              project: e.target.value,
                            }))
                          }
                          className="w-full text-sm focus:outline-none"
                        />
                        <button
                          type="button"
                          onClick={() => resetSpecificFilter("project")}
                          className="text-gray-500 hover:text-gray-700"
                          title="Сбросить фильтр"
                        >
                          <CloseIcon sx={{ fontSize: 16 }} />
                        </button>
                      </div>
                      <div className="max-h-52 overflow-y-auto">
                        {filteredProjects.map((project) => (
                          <label
                            key={project}
                            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100"
                          >
                            <input
                              type="checkbox"
                              checked={selectedFilters.project.includes(
                                project,
                              )}
                              onChange={() =>
                                handleMultiSelectChange("project", project)
                              }
                            />
                            <span>{project}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {showTeamProjectStreamFilters && (
                <div
                  className="relative whitespace-nowrap"
                  ref={(el) => (dropdownRefs.current.stream = el)}
                >
                  <button
                    type="button"
                    onClick={() => toggleDropdown("stream")}
                    className="px-3 py-1 bg-gray-200 border-none rounded-md text-sm font-bold text-gray-700 hover:bg-gray-300 text-left"
                  >
                    {getLabel("Стрим", "stream")}
                  </button>
                  {openDropdowns.stream && (
                    <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-60">
                      <div className="flex items-center border-b border-gray-200 px-2 py-1">
                        <input
                          type="text"
                          placeholder="Поиск стрима..."
                          value={searchInputs.stream}
                          onChange={(e) =>
                            setSearchInputs((prev) => ({
                              ...prev,
                              stream: e.target.value,
                            }))
                          }
                          className="w-full text-sm focus:outline-none"
                        />
                        <button
                          type="button"
                          onClick={() => resetSpecificFilter("stream")}
                          className="text-gray-500 hover:text-gray-700"
                          title="Сбросить фильтр"
                        >
                          <CloseIcon sx={{ fontSize: 16 }} />
                        </button>
                      </div>
                      <div className="max-h-52 overflow-y-auto">
                        {filteredStreams.map((stream) => (
                          <label
                            key={stream}
                            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100"
                          >
                            <input
                              type="checkbox"
                              checked={selectedFilters.stream.includes(stream)}
                              onChange={() =>
                                handleMultiSelectChange("stream", stream)
                              }
                            />
                            <span>{stream}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div
                className="relative whitespace-nowrap"
                ref={(el) => (dropdownRefs.current.priority = el)}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown("priority")}
                  className="px-3 py-1 bg-gray-200 border-none rounded-md text-sm font-bold text-gray-700 hover:bg-gray-300 text-left"
                >
                  {getLabel("Приоритет", "priority")}
                </button>
                {openDropdowns.priority && (
                  <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-60">
                    <div className="flex items-center border-b border-gray-200 px-2 py-1">
                      <input
                        type="text"
                        placeholder="Поиск приоритета..."
                        value={searchInputs.priority}
                        onChange={(e) =>
                          setSearchInputs((prev) => ({
                            ...prev,
                            priority: e.target.value,
                          }))
                        }
                        className="w-full text-sm focus:outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => resetSpecificFilter("priority")}
                        className="text-gray-500 hover:text-gray-700"
                        title="Сбросить фильтр"
                      >
                        <CloseIcon sx={{ fontSize: 16 }} />
                      </button>
                    </div>
                    <div className="max-h-52 overflow-y-auto">
                      {filteredPriorities.map((priority) => (
                        <label
                          key={priority.id}
                          className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100"
                        >
                          <input
                            type="checkbox"
                            checked={selectedFilters.priority.includes(
                              priority.id,
                            )}
                            onChange={() =>
                              handleMultiSelectChange("priority", priority.id)
                            }
                          />
                          <span>{priority.name}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div
                className="relative whitespace-nowrap"
                ref={(el) => (dropdownRefs.current.status = el)}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown("status")}
                  className="px-3 py-1 bg-gray-200 border-none rounded-md text-sm font-bold text-gray-700 hover:bg-gray-300 text-left"
                >
                  {getLabel("Статус", "status")}
                </button>
                {openDropdowns.status && (
                  <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-60">
                    <div className="flex items-center border-b border-gray-200 px-2 py-1">
                      <input
                        type="text"
                        placeholder="Поиск статуса..."
                        value={searchInputs.status}
                        onChange={(e) =>
                          setSearchInputs((prev) => ({
                            ...prev,
                            status: e.target.value,
                          }))
                        }
                        className="w-full text-sm focus:outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => resetSpecificFilter("status")}
                        className="text-gray-500 hover:text-gray-700"
                        title="Сбросить фильтр"
                      >
                        <CloseIcon sx={{ fontSize: 16 }} />
                      </button>
                    </div>
                    <div className="max-h-52 overflow-y-auto">
                      {filteredStatuses.map((s) => (
                        <label
                          key={s.id}
                          className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100"
                        >
                          <input
                            type="checkbox"
                            checked={selectedFilters.status.includes(s.id)}
                            onChange={() =>
                              handleMultiSelectChange("status", s.id)
                            }
                          />
                          <span>{s.name}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div
                className="relative whitespace-nowrap"
                ref={(el) => (dropdownRefs.current.tags = el)}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown("tags")}
                  className="px-3 py-1 bg-gray-200 border-none rounded-md text-sm font-bold text-gray-700 hover:bg-gray-300 text-left"
                >
                  {getLabel("Теги", "tags")}
                </button>
                {openDropdowns.tags && (
                  <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-60">
                    <div className="flex items-center border-b border-gray-200 px-2 py-1">
                      <input
                        type="text"
                        placeholder="Поиск тега..."
                        value={searchInputs.tags}
                        onChange={(e) =>
                          setSearchInputs((prev) => ({
                            ...prev,
                            tags: e.target.value,
                          }))
                        }
                        className="w-full text-sm focus:outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => resetSpecificFilter("tags")}
                        className="text-gray-500 hover:text-gray-700"
                        title="Сбросить фильтр"
                      >
                        <CloseIcon sx={{ fontSize: 16 }} />
                      </button>
                    </div>
                    <div className="max-h-52 overflow-y-auto">
                      {filteredTags.map((tag) => (
                        <label
                          key={tag.id}
                          className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100"
                        >
                          <input
                            type="checkbox"
                            checked={selectedFilters.tags.includes(tag.id)}
                            onChange={() =>
                              handleMultiSelectChange("tags", tag.id)
                            }
                          />
                          <span
                            className="px-2 py-0.5 rounded text-white text-xs"
                            style={{ backgroundColor: tag.color }}
                          >
                            {tag.name}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div
                className="relative whitespace-nowrap"
                ref={(el) => (dropdownRefs.current.startDate = el)}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown("startDate")}
                  className="px-3 py-1 bg-gray-200 border-none rounded-md text-sm font-bold text-gray-700 hover:bg-gray-300 text-left"
                >
                  {getLabel("Дата начала", "startDateRange")}
                </button>
                {openDropdowns.startDate && (
                  <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-64 p-2 space-y-2">
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-gray-600 font-medium">
                        От:
                      </label>
                      <input
                        type="date"
                        value={selectedFilters.startDate}
                        onChange={(e) =>
                          handleFilterChange("startDate", e.target.value)
                        }
                        className="flex-1 px-2 py-2 border border-gray-300 rounded-md text-sm"
                      />
                      {selectedFilters.startDate && (
                        <button
                          type="button"
                          onClick={() => handleFilterChange("startDate", "")}
                          className="text-gray-500 hover:text-gray-700"
                          title="Сбросить"
                        >
                          <CloseIcon sx={{ fontSize: 16 }} />
                        </button>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-gray-600 font-medium">
                        До:
                      </label>
                      <input
                        type="date"
                        value={selectedFilters.startDateEnd}
                        onChange={(e) =>
                          handleFilterChange("startDateEnd", e.target.value)
                        }
                        className="flex-1 px-2 py-2 border border-gray-300 rounded-md text-sm"
                      />
                      {selectedFilters.startDateEnd && (
                        <button
                          type="button"
                          onClick={() => handleFilterChange("startDateEnd", "")}
                          className="text-gray-500 hover:text-gray-700"
                          title="Сбросить"
                        >
                          <CloseIcon sx={{ fontSize: 16 }} />
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div
                className="relative whitespace-nowrap"
                ref={(el) => (dropdownRefs.current.deadline = el)}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown("deadline")}
                  className="px-3 py-1 bg-gray-200 border-none rounded-md text-sm font-bold text-gray-700 hover:bg-gray-300 text-left"
                >
                  {getLabel("Дедлайн", "deadlineRange")}
                </button>
                {openDropdowns.deadline && (
                  <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-64 p-2 space-y-2">
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-gray-600 font-medium">
                        От:
                      </label>
                      <input
                        type="date"
                        value={selectedFilters.deadline}
                        onChange={(e) =>
                          handleFilterChange("deadline", e.target.value)
                        }
                        className="flex-1 px-2 py-2 border border-gray-300 rounded-md text-sm"
                      />
                      {selectedFilters.deadline && (
                        <button
                          type="button"
                          onClick={() => handleFilterChange("deadline", "")}
                          className="text-gray-500 hover:text-gray-700"
                          title="Сбросить"
                        >
                          <CloseIcon sx={{ fontSize: 16 }} />
                        </button>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-gray-600 font-medium">
                        До:
                      </label>
                      <input
                        type="date"
                        value={selectedFilters.deadlineEnd}
                        onChange={(e) =>
                          handleFilterChange("deadlineEnd", e.target.value)
                        }
                        className="flex-1 px-2 py-2 border border-gray-300 rounded-md text-sm"
                      />
                      {selectedFilters.deadlineEnd && (
                        <button
                          type="button"
                          onClick={() => handleFilterChange("deadlineEnd", "")}
                          className="text-gray-500 hover:text-gray-700"
                          title="Сбросить"
                        >
                          <CloseIcon sx={{ fontSize: 16 }} />
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={clearAllFilters}
                  className="ml-auto px-2 py-2 text-gray-600 hover:text-gray-800"
                  title="Сбросить все фильтры"
                >
                  <CloseIcon sx={{ fontSize: 18 }} />
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedFiltersPanel;
