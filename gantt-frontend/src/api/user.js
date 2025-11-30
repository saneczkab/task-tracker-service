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
