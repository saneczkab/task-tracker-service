export const toInputDate = (value) => {
  if (!value) {
    return "";
  }

  const datetime = new Date(value + "Z");
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

  const dateString = value + "Z";
  const date = new Date(dateString);
  const datePart = date.toLocaleDateString();
  const timePart = `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
  return `${datePart}, ${timePart}`;
};

export const formatDatetime = (value) => {
  if (!value) {
    return "";
  }

  const date = new Date(value + "Z");
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${day}.${month}.${year} ${hours}:${minutes}`;
};

