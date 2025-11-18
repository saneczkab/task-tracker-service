import { useNavigate } from "react-router-dom";

export const useProcessError = (onUnknown = null) => {
  const navigate = useNavigate();

  // TODO: другие типы ошибок
  const handlers = {
    404: () => navigate("/error/404"),
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
