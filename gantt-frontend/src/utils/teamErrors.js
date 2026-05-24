export function getAddTeamMemberErrorMessage(status, details) {
  if (status === 422) {
    return "Введите корректный email";
  }

  if (status === 404) {
    return "Пользователь не найден";
  }

  if (typeof details?.detail === "string") {
    return details.detail;
  }

  return "Не удалось добавить пользователя";
}
