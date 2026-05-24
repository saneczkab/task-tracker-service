import { useNavigate } from "react-router-dom";
import { useNotification } from "../context/NotificationContext.jsx";

export const useProcessError = (onUnknown = null) => {
  const navigate = useNavigate();
  const { showNotification } = useNotification();

  // TODO: другие типы ошибок
  const handlers = {
    401: () => navigate("/login"),
    403: () => showNotification("Нет прав на это действие"),
    404: () => navigate("/error/404"),
    500: () => navigate("/error/500"),
  };

  return (status) => {
    const handler = handlers[status];
    if (handler) {
      handler();
      return;
    }

    if (onUnknown) {
      onUnknown(status);
      return;
    }

    console.error("Error: ", status);
  };
};
