import React from "react";
import { useParams } from "react-router-dom";
import Topbar from "../../components/ui/Topbar.jsx";
import Sidebar from "../../components/ui/Sidebar.jsx";

const TeamPage = () => {
  const { teamId } = useParams();

  return (
    <div className="min-h-screen flex flex-col">
      <Topbar />

      <div className="flex flex-1">
        <Sidebar teamId={teamId} />

        <main className="flex-1 p-6">
          <h1>Страница команда</h1>
        </main>
      </div>
    </div>
  );
};

export default TeamPage;
