import axios from "axios";

export async function subscribeToPushApi(subscription, token) {
  try {
    const keys = subscription.getKey
      ? {
          p256dh: btoa(
            String.fromCharCode(
              ...new Uint8Array(subscription.getKey("p256dh")),
            ),
          ),
          auth: btoa(
            String.fromCharCode(...new Uint8Array(subscription.getKey("auth"))),
          ),
        }
      : subscription.keys;

    const response = await axios.post(
      "/api/push/subscribe",
      {
        endpoint: subscription.endpoint,
        p256dh: keys.p256dh,
        auth: keys.auth,
      },
      { headers: { Authorization: token } },
    );
    return { ok: true, subscription: response.data };
  } catch (e) {
    return { ok: false, status: e.response?.status };
  }
}

export async function getPushSubscriptionsApi(token) {
  try {
    const response = await axios.get("/api/push/subscriptions", {
      headers: { Authorization: token },
    });
    return { ok: true, subscriptions: response.data };
  } catch (e) {
    return { ok: false, status: e.response?.status };
  }
}

export async function deletePushSubscriptionApi(subscriptionId, token) {
  try {
    await axios.delete(`/api/push/subscriptions/${subscriptionId}`, {
      headers: { Authorization: token },
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response?.status };
  }
}
