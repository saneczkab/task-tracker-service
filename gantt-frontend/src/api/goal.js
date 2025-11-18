import axios from "axios";

export async function createGoalApi(goal, streamId, token) {
  try {
    const response = await axios.post(
      `/api/stream/${streamId}/goal/new`,
      goal,
      {
        headers: { Authorization: token },
      },
    );

    return { ok: true, goal: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function fetchGoalsApi(streamId, token) {
  try {
    const response = await axios.get(`/api/stream/${streamId}/goals`, {
      headers: {
        Authorization: token,
      },
    });

    return { ok: true, goals: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function updateGoalApi(goalId, goal, token) {
  try {
    const response = await axios.patch(`/api/goal/${goalId}`, goal, {
      headers: {
        Authorization: token,
      },
    });

    return { ok: true, goal: response.data };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}

export async function deleteGoalApi(goalId, token) {
  try {
    await axios.delete(`/api/goal/${goalId}`, {
      headers: {
        Authorization: token,
      },
    });

    return { ok: true };
  } catch (e) {
    return { ok: false, status: e.response.status };
  }
}
