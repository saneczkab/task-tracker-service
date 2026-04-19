import React, { useEffect, useState, useMemo } from "react";
import { useLocation, Link } from "react-router-dom";
import { CircularProgress } from "@mui/material";
import { fetchStreamApi } from "../../api/stream.js";
import { useProcessError } from "../../hooks/useProcessError.js";
import Sidebar from "../ui/Sidebar.jsx";

const StreamLayout = ({
  teamId,
  streamId,
  children,
  showHeader = true,
  onProjIdLoaded,
  onStreamsReorder,
  onGanttStreamsReorder,
  sidebarStreams,
}) => {
  const location = useLocation();
  const processError = useProcessError();
  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );

  const [projId, setProjId] = useState(null);
  const [streamName, setStreamName] = useState("Стрим");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const loadStream = async () => {
      if (!streamId || !token) return;
      const response = await fetchStreamApi(streamId, token);
      if (!mounted) return;
      if (response.ok) {
        setStreamName(response.stream.name || "Стрим");
        setProjId(response.stream.project_id);
        if (onProjIdLoaded) {
          onProjIdLoaded(response.stream.project_id);
        }
      } else {
        processError(response.status);
      }
      setLoading(false);
    };

    loadStream();
    return () => {
      mounted = false;
    };
  }, [streamId, token]);

  const basePath = `/team/${teamId}/project/${projId}/stream/${streamId}`;
  const ganttPath = `${basePath}/gantt`;
  const kanbanPath = `${basePath}/kanban`;

  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex w-full">
      <Sidebar
        teamId={teamId}
        projId={projId}
        streamId={streamId}
        onStreamsReorder={onStreamsReorder}
        onGanttStreamsReorder={onGanttStreamsReorder}
        sidebarStreams={sidebarStreams}
      />
      <div className="p-4 flex flex-col overflow-hidden flex-1">
        <div className="border border-gray-300 rounded-lg bg-white flex flex-col overflow-hidden flex-1">
          {showHeader && (
            <>
              <div className="bg-[#EDEDED60] px-4 h-14 flex items-center relative">
                <div
                  className="font-semibold text-sm sm:text-base mr-4 truncate max-w-[35%]"
                  title={streamName}
                >
                  {loading ? (
                    <CircularProgress size={16} sx={{ color: "#fff" }} />
                  ) : (
                    streamName
                  )}
                </div>
                <nav className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex gap-4">
                  <NavButton to={basePath} active={isActive(basePath)}>
                    Задачи
                  </NavButton>
                  <NavButton to={ganttPath} active={isActive(ganttPath)}>
                    Диаграмма Ганта
                  </NavButton>
                  <NavButton to={kanbanPath} active={isActive(kanbanPath)}>
                    Канбан
                  </NavButton>
                </nav>
              </div>
              <div className="border-t border-gray-300" />
            </>
          )}
          <div className="p-6 flex-1 flex flex-col">{children}</div>
        </div>
      </div>
    </div>
  );
};

const NavButton = ({ to, active, children }) => {
  return (
    <Link
      to={to}
      className={`px-3 py-1 rounded-md text-sm sm:text-base transition-colors whitespace-nowrap ${active ? "bg-white text-[#3A7AFE]" : "bg-transparent hover:bg-white/20"}`}
    >
      {children}
    </Link>
  );
};

export default StreamLayout;
