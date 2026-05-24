import "./api/http.js";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./styles/index.css";
import { ConfirmDeleteDialogProvider } from "./context/ConfirmDeleteDialogContext.jsx";
import { NotificationProvider } from "./context/NotificationContext.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <NotificationProvider>
      <ConfirmDeleteDialogProvider>
        <App />
      </ConfirmDeleteDialogProvider>
    </NotificationProvider>
  </StrictMode>,
);
