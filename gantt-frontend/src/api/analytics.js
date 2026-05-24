import axios from "axios";

export async function getTeamAnalyticsApi(teamId, filters, token) {
  try {
    const response = await axios.get(`/api/team/${teamId}/analytics`, {
      params: filters,
      headers: { Authorization: token },
    });

    return {
      ok: true,
      analytics: response.data,
      statistics: response.data?.analytics ?? null,
      aiSummary: response.data?.ai_summary ?? "",
      requestLimit: response.data?.request_limit ?? null,
    };
  } catch (e) {
    console.error("Error:", e);
    return { ok: false, status: e.response?.status, error: e.message };
  }
}

export async function getAISummaryApi(teamId, filters, token) {
  try {
    const summaryFilters = {
      ...(filters || {}),
      is_ai_needed: true,
    };

    const response = await axios.get(`/api/team/${teamId}/analytics`, {
      params: summaryFilters,
      headers: { Authorization: token },
    });

    return {
      ok: true,
      summary: response.data?.ai_summary ?? "",
      requestLimit: response.data?.request_limit ?? null,
    };
  } catch (e) {
    console.error("Error:", e);
    const detail = e.response?.data?.detail;
    if (e.response?.status === 429 && detail?.request_limit) {
      return {
        ok: false,
        status: 429,
        requestLimit: detail.request_limit,
        message: detail.message,
      };
    }
    return { ok: false, status: e.response?.status, error: e.message };
  }
}
