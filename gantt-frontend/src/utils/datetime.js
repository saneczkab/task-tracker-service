export const toInputDate = (value) => {
  if (!value) {
    return "";
  }

  const datetime = new Date(value);
  return `${datetime.getFullYear()}-${String(datetime.getMonth() + 1).padStart(2, "0")}-${String(datetime.getDate()).padStart(2, "0")}`;
};

export const toInputTime = (value) => {
  if (!value) {
    return "";
  }

  const datetime = new Date(value + "Z");
  return `${String(datetime.getHours()).padStart(2, "0")}:${String(datetime.getMinutes()).padStart(2, "0")}`;
};

export const toISOStringOrNull = (dateStr, timeStr) => {
  if (!dateStr) {
    return null;
  }

  const combined = `${dateStr}T${timeStr || "00:00"}`;
  const date = new Date(combined);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
};

export const toLocaleDateWithTimeHM = (value) => {
  if (!value) {
    return "";
  }

  const normalized = value.trim().replace(" ", "T");
  const hasTimezone = /Z$/.test(normalized) || /[+-]\d{2}:\d{2}$/.test(normalized);
  const date = new Date(hasTimezone ? normalized : normalized + "Z");

  const datePart = date.toLocaleDateString("ru-RU");
  const timePart = `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
  return `${datePart}, ${timePart}`;
};
