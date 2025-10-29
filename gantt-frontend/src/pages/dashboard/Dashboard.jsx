import {useEffect, useState} from "react";
import { Button } from "@mui/material";

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
        <div>
            <h1>Главная страница</h1>
            <p>Токен: {authToken ? authToken : 'Пользователь не авторизован'}</p>

            {authToken && (
                <Button
                    variant="contained"
                    onClick={handleLogout}>
                    Выйти</Button>
            )}
        </div>
    )
}

export default Dashboard
