import axios from "axios";

export async function fetchStatusesApi() {
  try {
    const response = await axios.get(`/api/taskStatuses`);
    return { ok: true, statuses: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchPrioritiesApi() {
  try {
    const response = await axios.get(`/api/priorities`);
    return { ok: true, priorities: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}
