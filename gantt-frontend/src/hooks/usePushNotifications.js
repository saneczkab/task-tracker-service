import { useCallback, useEffect, useState } from "react";
import { subscribeToPushApi } from "../api/push.js";

const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || "";

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = atob(base64);
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)));
}

export function usePushNotifications() {
  const [permission, setPermission] = useState(
    "Notification" in window ? Notification.permission : "unsupported",
  );
  const [subscription, setSubscription] = useState(null);
  const [swReady, setSwReady] = useState(false);
  const [error, setError] = useState(null);

  const token = window.localStorage.getItem("auth_token") || "";

  useEffect(() => {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
      return;
    }

    navigator.serviceWorker
      .register("/sw.js")
      .then((reg) => {
        setSwReady(true);
        return reg.pushManager.getSubscription();
      })
      .then((sub) => {
        if (sub) setSubscription(sub);
      })
      .catch((err) => {
        console.error("Ошибка service worker:", err);
        setError("Непредвиденная ошибка!");
      });
  }, []);

  const requestPermissionAndSubscribe = useCallback(async () => {
    if (!("Notification" in window)) {
      setError("Браузер не поддерживает уведомления");
      return false;
    }

    if (!VAPID_PUBLIC_KEY) {
      console.error("Ошибка: VAPID ключ не найден");
      setError("Непредвиденная ошибка!");
      return false;
    }

    let perm = Notification.permission;
    if (perm === "default") {
      perm = await Notification.requestPermission();
      setPermission(perm);
    }

    if (perm !== "granted") {
      setError("Разрешение на уведомления не получено");
      return false;
    }

    try {
      const reg = await navigator.serviceWorker.ready;
      const existingSub = await reg.pushManager.getSubscription();
      if (existingSub) {
        setSubscription(existingSub);
        await subscribeToPushApi(existingSub, token);
        return true;
      }

      const newSub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });

      setSubscription(newSub);
      const result = await subscribeToPushApi(newSub, token);
      if (!result.ok) {
        setError("Не удалось сохранить подписку на сервере");
        return false;
      }
      return true;
    } catch (err) {
      console.error("Push subscribe error:", err);
      setError("Непредвиденная ошибка!");
      return false;
    }
  }, [token]);

  const isSupported =
    "Notification" in window &&
    "serviceWorker" in navigator &&
    "PushManager" in window;

  return {
    isSupported,
    permission,
    subscription,
    swReady,
    error,
    requestPermissionAndSubscribe,
  };
}
