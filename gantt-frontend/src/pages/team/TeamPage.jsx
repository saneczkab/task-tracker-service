import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Topbar from "../../components/ui/Topbar.jsx";
import Sidebar from "../../components/ui/Sidebar.jsx";

const TeamPage = () => {
    const { teamId } = useParams();
    const navigate = useNavigate();

    const [rawBody, setRawBody] = useState("");
    const [error, setError] = useState("");
    const [projects, setProjects] = useState([]);

    useEffect(() => {
        const fetchProjects = async () => {
            setError("");
            const token = window.localStorage.getItem("auth_token");

            try {
                const res = await fetch(`/api/team/${teamId}/projects`, {
                    method: "GET",
                    headers: {
                        "Accept": "application/json",
                        "Authorization": token
                    }
                });

                if (res.status === 404) {
                    navigate("/error/404");
                    return;
                }

                const text = await res.text();
                setRawBody(text);
                const parsed = JSON.parse(text);
                setProjects(parsed);
            } catch (e) {
                setError(e.message);
            }
        };

        fetchProjects();
    }, [teamId, navigate]);

    return (
        <div className="min-h-screen flex flex-col">
            <Topbar />

            <div className="flex flex-1">
                <Sidebar projects={projects} teamId={Number(teamId)} />

                <main className="flex-1 p-6">
                    <h1>{rawBody}</h1>
                    {error && <p style={{ color: "red" }}>Error: {error}</p>}
                </main>
            </div>
        </div>
    );
};

export default TeamPage;
