import axios from "axios";

export async function fetchTeamTagsApi(teamId, token) {
  try {
    const response = await axios.get(`/api/team/${teamId}/tags`, {
      headers: { Authorization: token },
    });
    return { ok: true, tags: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function createTeamTagApi(teamId, name, color, token) {
  try {
    const response = await axios.post(
      `/api/team/${teamId}/tags/new`,
      { name, color },
      { headers: { Authorization: token } },
    );
    return { ok: true, tag: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function deleteTeamTagApi(teamId, tagId, token) {
  try {
    await axios.delete(`/api/team/${teamId}/tags/${tagId}`, {
      headers: { Authorization: token },
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}
