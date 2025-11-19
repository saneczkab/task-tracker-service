import React, { useState, useEffect } from "react";
import { TextField, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const navigate = useNavigate();

  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [isSigningIn, setIsSigningIn] = useState(false);
  const [isEmailCorrect, setIsEmailCorrect] = useState(false);
  const [isConfirmPasswordCorrect, setIsConfirmPasswordCorrect] =
    useState(false);

  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPasswordText, setConfirmPasswordText] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const buttonText = isLoggingIn
    ? "Войти"
    : isSigningIn
      ? "Зарегистрироваться"
      : "Продолжить";
  const titleText = isSigningIn ? "Регистрация в Gantt" : "Вход в Gantt";
  const descriptionText = isLoggingIn
    ? "Введите пароль для входа в аккаунт"
    : isSigningIn
      ? "Создайте аккаунт для использования сервиса"
      : "Введите почту, чтобы войти или зарегистрироваться";
  const isButtonEnabled =
    isEmailCorrect &&
    ((!isLoggingIn && !isSigningIn) ||
      (isLoggingIn && password.trim() !== "") ||
      (isSigningIn &&
        username.trim() !== "" &&
        password.trim() !== "" &&
        isConfirmPasswordCorrect));

  // TODO: валидация токена
  useEffect(() => {
    const token = window.localStorage.getItem("auth_token");
    if (token) {
      navigate("/");
    }
  }, []);

  const getErrorMessage = async (response) => {
    const data = await response.json();
    return (
      data?.message ||
      data?.detail ||
      data?.error ||
      `Ошибка ${response.status}`
    );
  };

  const checkEmailFormat = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isCorrect = emailRegex.test(email);
    setIsEmailCorrect(isCorrect);
    setErrorMessage(isCorrect ? "" : "Некорректный формат электронной почты");
  };

  const confirmPassword = (
    passwordStr = password,
    confirmPassStr = confirmPasswordText,
  ) => {
    const isCorrect = passwordStr === confirmPassStr;
    setIsConfirmPasswordCorrect(isCorrect);

    if (confirmPassStr) {
      setErrorMessage(isCorrect ? "" : "Пароли не совпадают");
    }
  };

  const processToken = (data) => {
    const tokenType = data?.token_type;
    const accessToken = data?.access_token;
    if (!tokenType || !accessToken) {
      setErrorMessage("Ошибка аутентификации");
      return;
    }

    const auth = `${tokenType} ${accessToken}`;
    localStorage.setItem("auth_token", auth);
    navigate("/");
  };

  const handleSubmit = async () => {
    setErrorMessage("");

    if (isLoggingIn) {
      await handleLogin();
    } else if (isSigningIn) {
      await handleRegistration();
    } else {
      await handleEmailSubmit();
    }
  };

  const handleLogin = async () => {
    try {
      // TODO: move request details to body
      const response = await fetch(
        "/api/login?email=" +
          encodeURIComponent(email) +
          "&password=" +
          encodeURIComponent(password),
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          // body: JSON.stringify({
          //     email: email.toLowerCase(),
          //     password: password
          // })
        },
      );

      if (!response.ok) {
        setErrorMessage("Ошибка входа: " + (await getErrorMessage(response)));
        return;
      }

      const data = await response.json();
      processToken(data);
    } catch (error) {
      setErrorMessage("Ошибка входа: " + error.message);
    }
  };

  const handleRegistration = async () => {
    try {
      // TODO: move request details to body
      const response = await fetch(
        "/api/register?email=" +
          encodeURIComponent(email) +
          "&nickname=" +
          encodeURIComponent(username) +
          "&password=" +
          encodeURIComponent(password),
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          // body: JSON.stringify({
          //     email: email.toLowerCase(),
          //     username: username,
          //     password: password
          // })
        },
      );

      if (!response.ok) {
        setErrorMessage("Ошибка входа: " + (await getErrorMessage(response)));
        return;
      }

      const data = await response.json();
      processToken(data);
    } catch (error) {
      setErrorMessage("Ошибка регистрации: " + error.message);
    }
  };

  const handleEmailSubmit = async () => {
    try {
      // TODO: move request details to body
      const response = await fetch(
        "/api/check-email?email=" + encodeURIComponent(email),
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          // body: JSON.stringify({ email: email.toLowerCase() })
        },
      );

      if (!response.ok) {
        setErrorMessage("Ошибка входа: " + (await getErrorMessage(response)));
        return;
      }

      const data = await response.json();
      setIsLoggingIn(data.exists);
      setIsSigningIn(!data.exists);
    } catch (error) {
      setErrorMessage("Ошибка проверки почты: " + error.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-xl bg-white p-8 rounded-[12px] shadow text-center">
        <div className="text-4xl font-bold">{titleText}</div>
        <div className="text-lg mt-2">{descriptionText}</div>

        <form className="mt-6 text-left">
          <TextField
            id="email"
            label="Электронная почта"
            variant="filled"
            fullWidth
            disabled={isSigningIn || isLoggingIn}
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              checkEmailFormat(e.target.value);
            }}
            slotProps={{
              input: { disableUnderline: true },
            }}
            sx={{
              "& .MuiFilledInput-root": {
                backgroundColor: "#EDEDED",
                borderRadius: "12px",
                height: (theme) => theme.spacing(7),
              },
            }}
          />

          {isSigningIn && (
            <TextField
              id="nickname"
              label="Никнейм"
              variant="filled"
              fullWidth
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              slotProps={{
                input: { disableUnderline: true },
              }}
              sx={{
                mt: 2,
                "& .MuiFilledInput-root": {
                  backgroundColor: "#EDEDED",
                  borderRadius: "12px",
                  height: (theme) => theme.spacing(7),
                },
              }}
            />
          )}

          {(isLoggingIn || isSigningIn) && (
            <TextField
              id="password"
              label="Пароль"
              type="password"
              variant="filled"
              fullWidth
              onChange={(e) => {
                setPassword(e.target.value);
                confirmPassword(e.target.value, undefined);
              }}
              slotProps={{
                input: { disableUnderline: true },
              }}
              sx={{
                mt: 2,
                "& .MuiFilledInput-root": {
                  backgroundColor: "#EDEDED",
                  borderRadius: "12px",
                  height: (theme) => theme.spacing(7),
                },
              }}
            />
          )}

          {isSigningIn && (
            <TextField
              id="confirm-password"
              label="Подтвердите пароль"
              type="password"
              variant="filled"
              fullWidth
              onChange={(e) => {
                setConfirmPasswordText(e.target.value);
                confirmPassword(undefined, e.target.value);
              }}
              slotProps={{
                input: { disableUnderline: true },
              }}
              sx={{
                mt: 2,
                "& .MuiFilledInput-root": {
                  backgroundColor: "#EDEDED",
                  borderRadius: "12px",
                  height: (theme) => theme.spacing(7),
                },
              }}
            />
          )}

          {errorMessage && (
            <div className="text-[#FF0000] mt-4">{errorMessage}</div>
          )}

          <Button
            variant="contained"
            fullWidth
            color="inherit"
            onClick={handleSubmit}
            disabled={!isButtonEnabled}
            sx={{
              mt: 2,
              borderRadius: "12px",
              backgroundColor: "#FFDD2D",
              height: (theme) => theme.spacing(7),
              fontFamily: "inherit",
            }}
          >
            {buttonText}
          </Button>
        </form>
      </div>
    </div>
  );
};

export default Login;
