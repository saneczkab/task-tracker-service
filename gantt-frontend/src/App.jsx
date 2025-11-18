import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/dashboard/Dashboard.jsx'
import Register from './pages/auth/Register.jsx'
import Login from './pages/auth/Login.jsx'
import Profile from './pages/auth/Profile.jsx'
import TeamPage from "./pages/team/TeamPage.jsx";

import Error404 from "./pages/error/Error404.jsx";
import StreamPage from "./pages/stream/StreamPage.jsx";
import KanbanBoard from "./components/tasks/KanbanBoard.jsx";

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
                <Route path="/team/:teamId/stream/:streamId" element={<StreamPage />} />
                <Route path="/team/:teamId/stream/:streamId/kanban" element={<KanbanBoard />} />

                <Route path="/error/404" element={<Error404 />} />
            </Routes>
        </Router>
    </>
  )
}

export default App
