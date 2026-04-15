import React, { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import GanttChart from "../../components/gantt/GanttChart.jsx";
import StreamLayout from "../../components/layout/StreamLayout.jsx";

const GanttChartPage = () => {
  const { teamId, projId, streamId } = useParams();
  const [showChart, setShowChart] = useState(false);
  const [sidebarStreams, setSidebarStreams] = useState(null);

  useEffect(() => {
    const t = setTimeout(() => setShowChart(true), 100);
    return () => clearTimeout(t);
  }, []);

  const handleStreamsReorder = useCallback((streams) => {
    if (Array.isArray(streams)) {
      setSidebarStreams(streams);
    }
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F6F7]">
      <div className="flex-1 gap-4">
        <div className="">
          <StreamLayout
            teamId={teamId}
            streamId={streamId}
            onStreamsReorder={handleStreamsReorder}
            onGanttStreamsReorder={setSidebarStreams}
            sidebarStreams={sidebarStreams}
          >
            <main
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                overflowY: "auto",
                overflowX: "hidden",
              }}
            >
              {showChart ? (
                <GanttChart
                  projId={projId}
                  teamId={teamId}
                  sidebarStreams={sidebarStreams}
                  onSidebarStreamsUpdate={handleStreamsReorder}
                />
              ) : null}
            </main>
          </StreamLayout>
        </div>
      </div>
    </div>
  );
};

export default GanttChartPage;
