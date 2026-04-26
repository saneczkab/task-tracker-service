import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import GanttChart from "../../components/gantt/GanttChart.jsx";
import StreamLayout from "../../components/layout/StreamLayout.jsx";

const GanttChartPage = () => {
  const { teamId, projId, streamId } = useParams();
  const [showChart, setShowChart] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setShowChart(true), 100);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F6F7]">
      <div className="flex-1 gap-4">
        <div className="">
          <StreamLayout teamId={teamId} streamId={streamId}>
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
                <GanttChart projId={projId} teamId={teamId} />
              ) : null}
            </main>
          </StreamLayout>
        </div>
      </div>
    </div>
  );
};

export default GanttChartPage;
