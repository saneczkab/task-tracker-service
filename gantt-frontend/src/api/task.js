import axios from "axios";

export async function createTaskApi(task, streamId, token) {
  try {
    const response = await axios.post(
      `/api/stream/${streamId}/task/new`,
      task,
      {
        headers: { Authorization: token },
      },
    );
    return { ok: true, task: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchTasksApi(streamId, token) {
  try {
    const response = await axios.get(`/api/stream/${streamId}/tasks`, {
      headers: { Authorization: token },
    });
    return { ok: true, tasks: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function updateTaskApi(taskId, task, token) {
  try {
    const response = await axios.patch(`/api/task/${taskId}`, task, {
      headers: { Authorization: token },
    });
    return { ok: true, task: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function deleteTaskApi(taskId, token) {
  try {
    await axios.delete(`/api/task/${taskId}`, {
      headers: { Authorization: token },
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}
