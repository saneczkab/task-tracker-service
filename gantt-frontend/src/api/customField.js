import axios from "axios";

export async function fetchTeamCustomFieldsApi(teamId, token) {
  try {
    const response = await axios.get(`/api/teams/${teamId}/custom_fields/`, {
      headers: { Authorization: token },
    });
    return { ok: true, fields: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function createTeamCustomFieldApi(teamId, field, token) {
  try {
    const response = await axios.post(
      `/api/teams/${teamId}/custom_fields/`,
      field,
      {
        headers: { Authorization: token },
      },
    );
    return { ok: true, field: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function deleteTeamCustomFieldApi(fieldId, token) {
  try {
    await axios.delete(`/api/custom_fields/${fieldId}/`, {
      headers: { Authorization: token },
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function deleteTaskCustomFieldValueApi(
  taskId,
  customFieldId,
  token,
) {
  try {
    await axios.delete(`/api/task/${taskId}/custom_fields/${customFieldId}`, {
      headers: { Authorization: token },
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}
