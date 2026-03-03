import axios from "axios";

export async function getTaskRemindersApi(taskId, token) {
  try {
    const response = await axios.get(`/api/tasks/${taskId}/reminders`, {
      headers: { Authorization: token },
    });
    return { ok: true, reminders: response.data };
  } catch (e) {
    return { ok: false, status: e.response?.status };
  }
}

export async function createReminderApi(taskId, remindAt, token) {
  try {
    const remindAtNaive = remindAt ? remindAt.replace("Z", "") : remindAt;
    const response = await axios.post(
      `/api/tasks/${taskId}/reminders`,
      { remind_at: remindAtNaive },
      { headers: { Authorization: token } },
    );
    return { ok: true, reminder: response.data };
  } catch (e) {
    return { ok: false, status: e.response?.status };
  }
}

export async function updateReminderApi(reminderId, remindAt, token) {
  try {
    const remindAtNaive = remindAt ? remindAt.replace("Z", "") : remindAt;
    const response = await axios.patch(
      `/api/tasks/reminders/${reminderId}`,
      { remind_at: remindAtNaive },
      { headers: { Authorization: token } },
    );
    return { ok: true, reminder: response.data };
  } catch (e) {
    return { ok: false, status: e.response?.status };
  }
}

export async function deleteReminderApi(reminderId, token) {
  try {
    await axios.delete(`/api/tasks/reminders/${reminderId}`, {
      headers: { Authorization: token },
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response?.status };
  }
}
