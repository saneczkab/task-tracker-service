import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./styles/index.css";
import { ConfirmDeleteDialogProvider } from "./context/ConfirmDeleteDialogContext.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ConfirmDeleteDialogProvider>
      <App />
    </ConfirmDeleteDialogProvider>
  </StrictMode>,
);
