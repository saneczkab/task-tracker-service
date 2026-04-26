import axios from "axios";

export async function createStreamApi(projectId, name, token) {
  try {
    const response = await axios.post(
      `/api/project/${projectId}/stream/new`,
      { name },
      { headers: { Authorization: token } },
    );

    return { ok: true, created: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchStreamApi(streamId, token) {
  try {
    const response = await axios.get(`/api/stream/${streamId}`, {
      headers: { Authorization: token },
    });

    return { ok: true, stream: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchStreamsApi(projectId, token) {
  try {
    const response = await axios.get(`/api/project/${projectId}/streams`, {
      headers: { Authorization: token },
    });

    return { ok: true, streams: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function updateStreamNameApi(streamId, newName, token) {
  try {
    const response = await axios.patch(
      `/api/stream/${streamId}`,
      { name: newName },
      { headers: { Authorization: token } },
    );

    return { ok: true, updated: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function deleteStreamApi(streamId, token) {
  try {
    await axios.delete(`/api/stream/${streamId}`, {
      headers: { Authorization: token },
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}
