import React, { useState } from "react";
import { useParams } from "react-router-dom";
import GoalList from "../../components/tasks/GoalList.jsx";
import TaskList from "../../components/tasks/TaskList.jsx";
import StreamLayout from "../../components/layout/StreamLayout.jsx";

const StreamPage = () => {
  const { streamId, teamId } = useParams();
  const [projId, setProjId] = useState(null);

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F6F7]">
      <div className="flex flex-1 gap-4">
        <div className="flex flex-1">
          <StreamLayout
            teamId={teamId}
            streamId={streamId}
            onProjIdLoaded={setProjId}
          >
            <h2 className="font-bold text-lg mb-4">Цели стрима</h2>
            <GoalList streamId={Number(streamId)} />

            <h2 className="font-bold text-lg mb-4 mt-8">Задачи стрима</h2>
            <TaskList
              streamId={Number(streamId)}
              projectId={projId}
              teamId={teamId}
            />
          </StreamLayout>
        </div>
      </div>
    </div>
  );
};

export default StreamPage;
