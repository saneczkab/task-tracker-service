import axios from "axios";

export async function fetchUserEmailApi(token) {
  try {
    const response = await axios.get(`/api/user_by_token`, {
      headers: { Authorization: token },
    });
    return { ok: true, email: response.data.email };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchUserApi(token) {
  try {
    const response = await axios.get(`/api/user_by_token`, {
      headers: { Authorization: token },
    });
    return { ok: true, email: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function updateUserNicknameApi(nickname, token) {
  try {
    const response = await axios.put(
      `/api/user/nickname`,
      { nickname },
      {
        headers: { Authorization: token },
      },
    );
    return { ok: true, data: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function updateUserEmailApi(email, token) {
  try {
    const response = await axios.put(
      `/api/user/email`,
      { email },
      {
        headers: { Authorization: token },
      },
    );
    return { ok: true, data: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}
