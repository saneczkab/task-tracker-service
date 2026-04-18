const parseDateTime = (value) => {
  const normalized = String(value).trim().replace(" ", "T");
  const hasTimezone =
    /Z$/.test(normalized) || /[+-]\d{2}:\d{2}$/.test(normalized);
  return new Date(hasTimezone ? normalized : normalized + "Z");
};

export const toInputDate = (value) => {
  if (!value) {
    return "";
  }

  const datetime = parseDateTime(value);
  if (Number.isNaN(datetime.getTime())) {
    return "";
  }

  return `${datetime.getFullYear()}-${String(datetime.getMonth() + 1).padStart(2, "0")}-${String(datetime.getDate()).padStart(2, "0")}`;
};

export const toInputDateValue = (value) => {
  if (!value) {
    return "";
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return value;
  }

  return toInputDate(value);
};

export const toInputDateTimeValue = (value) => {
  if (!value) {
    return "";
  }

  const dateStr = toInputDate(value);
  const timeStr = toInputTime(value);

  if (!dateStr || !timeStr) {
    return "";
  }

  return `${dateStr}T${timeStr}`;
};

export const toInputTime = (value) => {
  if (!value) {
    return "";
  }

  const datetime = parseDateTime(value);
  if (Number.isNaN(datetime.getTime())) {
    return "";
  }

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
  const hasTimezone =
    /Z$/.test(normalized) || /[+-]\d{2}:\d{2}$/.test(normalized);
  const date = new Date(hasTimezone ? normalized : normalized + "Z");

  const datePart = date.toLocaleDateString("ru-RU");
  const timePart = `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
  return `${datePart}, ${timePart}`;
};
