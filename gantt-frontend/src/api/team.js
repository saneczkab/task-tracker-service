import axios from "axios";

export async function createTeamApi(name, token) {
  try {
    await axios.post(
      `/api/team/new`,
      { name },
      { headers: { Authorization: token } },
    );
    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function addUserToTeamApi(teamId, userEmail, token) {
  try {
    await axios.patch(
      `/api/team/${teamId}`,
      { newUsers: [userEmail] },
      { headers: { Authorization: token } },
    );

    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchTeamsApi(token) {
  try {
    const response = await axios.get(`/api/user_by_token`, {
      headers: { Authorization: token },
    });
    return { ok: true, teams: response.data.teams };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchTeamNameApi(teamId, token) {
  try {
    const user = await axios.get(`/api/user_by_token`, {
      headers: { Authorization: token },
    });

    const teams = user.data.teams;
    const team = teams.find((t) => t.id === Number(teamId));
    if (team) {
      return { ok: true, name: team.name };
    } else {
      // TODO: возвращать ошибку 404
      return { ok: true, name: "Команда" };
    }
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchTeamMembersApi(teamId, token) {
  try {
    const response = await axios.get(`/api/team/${teamId}/users`, {
      headers: { Authorization: token },
    });

    return { ok: true, users: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function updateTeamNameApi(teamId, newName, token) {
  try {
    await axios.patch(
      `/api/team/${teamId}`,
      { name: newName },
      { headers: { Authorization: token } },
    );

    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function deleteTeamApi(teamId, token) {
  try {
    await axios.delete(`/api/team/${teamId}`, {
      headers: { Authorization: token },
    });

    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function deleteUserFromTeamApi(teamId, userEmail, token) {
  try {
    await axios.patch(
      `/api/team/${teamId}`,
      { deleteUsers: [userEmail] },
      { headers: { Authorization: token } },
    );

    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}
