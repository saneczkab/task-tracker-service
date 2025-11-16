import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Topbar from "../../components/ui/Topbar.jsx";
import Sidebar from "../../components/ui/Sidebar.jsx";
import GoalList from "../../components/tasks/GoalList.jsx";
import TaskList from "../../components/tasks/TaskList.jsx";

const StreamPage = () => {
    const { streamId } = useParams();
    const { teamId } = useParams();

    const navigate = useNavigate();

    const [streamName, setStreamName] = useState("");

    useEffect(() => {
        fetchStreamName(teamId);
    }, [streamId, navigate]);

    const fetchStreamName = async () => {
        const token = window.localStorage.getItem("auth_token");

        try {
            const res = await fetch(`/api/stream/${streamId}`, {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                    "Authorization": token
                }
            });

            if (!res.ok) {
                // TODO
                return;
            }

            const data = await res.json();
            setStreamName(data.name);
        } catch {
            // TODO
        }
    };

    return (
        <div className="min-h-screen flex flex-col bg-white">
            <Topbar />
            <div className="flex flex-1">
                <Sidebar teamId={teamId} />
                <main className="flex-1 p-6">
                    <h1 className="font-bold text-xl mb-4">Цели стрима {streamName}</h1>
                    <GoalList streamId={Number(streamId)} />

                    <h1 className="font-bold text-xl mb-4 mt-8">Задачи стрима {streamName}</h1>
                    <TaskList streamId={Number(streamId)} />
                </main>
            </div>
        </div>
    )
}


export default StreamPage;