import axios from "axios";

export async function createProjectApi(teamId, name, token) {
  try {
    const response = await axios.post(
      `/api/team/${teamId}/project/new`,
      { name },
      { headers: { Authorization: token } },
    );

    return { ok: true, created: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchProjectsApi(teamId, token) {
  try {
    const response = await axios.get(`/api/team/${teamId}/projects`, {
      headers: { Authorization: token },
    });
    return { ok: true, projects: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function updateProjectNameApi(projectId, newName, token) {
  try {
    const response = await axios.patch(
      `/api/project/${projectId}`,
      { name: newName },
      { headers: { Authorization: token } },
    );
    return { ok: true, updated: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function deleteProjectApi(projectId, token) {
  try {
    await axios.delete(`/api/project/${projectId}`, {
      headers: { Authorization: token },
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}
