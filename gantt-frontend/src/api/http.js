import axios from "axios";

axios.interceptors.request.use((config) => {
  const auth = window.localStorage.getItem("auth_token");
  const refresh = window.localStorage.getItem("refresh_token");
  if (auth) {
    config.headers.Authorization = auth;
  }
  if (refresh) {
    config.headers["X-Refresh-Token"] = refresh;
  }
  return config;
});

axios.interceptors.response.use(
  (response) => {
    const next = response.headers["x-new-access-token"];
    if (next) {
      window.localStorage.setItem("auth_token", `Bearer ${next}`);
    }
    return response;
  },
  (error) => {
    const next = error.response?.headers?.["x-new-access-token"];
    if (next) {
      window.localStorage.setItem("auth_token", `Bearer ${next}`);
    }
    const status = error.response?.status;
    if (status === 401) {
      window.localStorage.removeItem("auth_token");
      window.localStorage.removeItem("refresh_token");
      if (window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
    }
    return Promise.reject(error);
  },
);
