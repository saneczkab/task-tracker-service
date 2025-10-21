import React from "react";
import { TextField, Button } from "@mui/material";

const Login = () => {
    return (
        <div className="min-h-screen flex items-center justify-center px-4">
            <div className="w-full max-w-xl bg-white p-8 rounded-[12px] shadow text-center">
                <div className="text-4xl font-bold">Вход в Gantt</div>
                <div className="text-lg mt-2">Введите почту, чтобы войти или зарегистрироваться</div>

                <form className="mt-6 text-left">
                    <TextField
                        id="email"
                        label="Электронная почта"
                        variant="filled"
                        fullWidth
                        slotProps={{
                            input: { disableUnderline: true },
                        }}
                        sx={{
                            "& .MuiFilledInput-root": {
                                backgroundColor: "#EDEDED",
                                borderRadius: "12px",
                                height: (theme) => theme.spacing(7)
                            },
                        }}
                    />

                    <Button
                        variant="contained"
                        fullWidth
                        color="inherit"
                        sx={{
                            mt: 2,
                            borderRadius: "12px",
                            backgroundColor: "#FFDD2D",
                            height: (theme) => theme.spacing(7),
                            fontFamily: "inherit"
                        }}
                    >Продолжить</Button>
                </form>
            </div>
        </div>
    )
}

export default Login
