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

    return { ok: true, summary: response.data?.ai_summary ?? "" };
  } catch (e) {
    console.error("Error:", e);
    return { ok: false, status: e.response?.status, error: e.message };
  }
}
