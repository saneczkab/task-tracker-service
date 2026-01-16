import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/dashboard/Dashboard.jsx";
import Register from "./pages/auth/Register.jsx";
import Login from "./pages/auth/Login.jsx";
import Profile from "./pages/auth/Profile.jsx";
import TeamPage from "./pages/team/TeamPage.jsx";
import StreamPage from "./pages/stream/StreamPage.jsx";
import KanbanBoard from "./components/tasks/KanbanBoard.jsx";
import GanttChartPage from "./pages/stream/GanttChartPage.jsx";
import AllTasks from "./pages/tasks/AllTasks.jsx";
import ImmediateTasks from "./pages/tasks/ImmediateTasks.jsx";
import ErrorLayout from "./pages/error/ErrorLayout.jsx";
import React from "react";

function App() {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/team/:teamId" element={<TeamPage />} />
          <Route
            path="/team/:teamId/stream/:streamId"
            element={<StreamPage />}
          />
          <Route
            path="/team/:teamId/stream/:streamId/kanban"
            element={<KanbanBoard />}
          />
          <Route
            path="/team/:teamId/project/:projId/stream/:streamId/gantt"
            element={<GanttChartPage />}
          />
          <Route path="/team/:teamId/tasks" element={<AllTasks />} />
          <Route
            path="/team/:teamId/immediateTasks"
            element={<ImmediateTasks />}
          />

          <Route
            path="/error/403"
            element={<ErrorLayout code={403} message="Доступ запрещён" />}
          />
          <Route
            path="/error/404"
            element={<ErrorLayout code={404} message="Страница не найдена" />}
          />
          <Route
            path="/error/500"
            element={
              <ErrorLayout code={500} message="Внутренняя ошибка сервера" />
            }
          />
        </Routes>
      </Router>
    </>
  );
}

export default App;
