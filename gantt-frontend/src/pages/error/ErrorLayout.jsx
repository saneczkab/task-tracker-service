import React from "react";
import { useNavigate } from "react-router-dom";

const ErrorLayout = ({ code, message }) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <main className="flex-grow flex items-center justify-center w-full">
        <div className="max-w-md w-full p-8 text-neutral-800 flex flex-col items-center gap-6">
          <div className="text-8xl font-bold">{code}</div>
          <h2 className="text-2xl font-semibold">{message}</h2>
          <button
            onClick={() => navigate("/")}
            aria-label="На главную"
            className="mt-2 px-6 py-2 bg-neutral-800 text-white rounded hover:opacity-90 transition"
          >
            На главную
          </button>
        </div>
      </main>

      <footer className="w-full text-center py-6 text-sm text-neutral-500">
        Что-то пошло не так? Сообщите нам в Telegram:{" "}
        <a
          href="https://t.me/saneczkab"
          className="text-neutral-500 hover:underline"
        >
          @saneczkab
        </a>
      </footer>
    </div>
  );
};

export default ErrorLayout;
