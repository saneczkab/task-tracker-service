import {useEffect, useState} from "react";
import { Button } from "@mui/material";
import Sidebar from "../../components/ui/Sidebar.jsx";
import Topbar from "../../components/ui/Topbar.jsx";

const Dashboard = () => {
    const [authToken, setAuthToken] = useState("");

    useEffect(() => {
        const token = window.localStorage.getItem('auth_token');
        setAuthToken(token);
    }, []);

    const handleLogout = () => {
        window.localStorage.removeItem('auth_token');
        setAuthToken("");
    }

    return (
        <div className="min-h-screen flex flex-col">
            <Topbar/>

            <div className="flex flex-1">
                <Sidebar />

                <main className="flex-1 p-6">
                    <h1>Главная страница</h1>
                    <p>Токен: {authToken ? authToken : 'Пользователь не авторизован'}</p>

                    {authToken && (
                        <Button
                            variant="contained"
                            onClick={handleLogout}>
                            Выйти</Button>
                    )}
                </main>
            </div>
        </div>

    )
}

export default Dashboard
