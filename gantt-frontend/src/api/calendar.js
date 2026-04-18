import axios from "axios";

export async function exportCalendarApi(scope, payload, token) {
  try {
    const finalPayload = { scope, ...payload };

    const response = await axios.post("/api/calendar/export", finalPayload, {
      headers: { Authorization: token },
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "calendar.ics");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response?.status };
  }
}
