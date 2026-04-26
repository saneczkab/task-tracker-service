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
}) => {
  const [streamName, setStreamName] = useState("");
  const [projId, setProjId] = useState(null);
  const [loading, setLoading] = useState(true);

  const token = useMemo(
    () => window.localStorage.getItem("auth_token") || "",
    [],
  );
  const processError = useProcessError();
  const location = useLocation();

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const response = await fetchStreamApi(streamId, token);
      if (!response.ok) {
        processError(response.status);
        setLoading(false);
        return;
      }
      const streamData = response.stream;
      setStreamName(streamData.name || "");
      setProjId(streamData.project_id);
      if (onProjIdLoaded && streamData.project_id) {
        onProjIdLoaded(streamData.project_id);
      }
      setLoading(false);
    };
    if (streamId) {
      load();
    }
  }, [streamId, token]);

  const basePath = `/team/${teamId}/stream/${streamId}`;
  const kanbanPath = `/team/${teamId}/stream/${streamId}/kanban`;
  const ganttPath = `/team/${teamId}/project/${projId}/stream/${streamId}/gantt`;

  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex w-full">
      <Sidebar teamId={teamId} projId={projId} streamId={streamId} />
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
