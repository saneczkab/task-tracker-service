import { useNavigate } from "react-router-dom";

export const useProcessError = (onUnknown = null) => {
  const navigate = useNavigate();

  // TODO: другие типы ошибок
  const handlers = {
    401: () => navigate("/login"),
    403: () => navigate("/error/403"),
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
