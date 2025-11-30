export const TABLE_CONTAINER_STYLES = {
  overflow: "hidden",
  mt: 1,
  border: "none",
  boxShadow: "none",
};

export const TASKS_TABLE_BODY_STYLES = {
  "&:hover": { backgroundColor: "#fafafa" },
  "& .task-actions": {
    opacity: 0,
    transition: "opacity 0.2s",
  },
  "&:hover .task-actions": { opacity: 1 },
};

export const GOALS_TABLE_BODY_STYLES = {
  "&:hover": { backgroundColor: "#fafafa" },
  "& .goal-actions": {
    opacity: 0,
    transition: "opacity 0.2s",
  },
  "&:hover .goal-actions": { opacity: 1 },
};

export const HEADER_CELL_STYLES = {
  color: "rgba(31, 31, 31, 0.6)",
  fontWeight: 600,
  fontFamily: "Montserrat, sans-serif",
};

export const CELL_STYLES = {
  fontFamily: "Montserrat, sans-serif",
};

export const LAST_CELL_STYLES = {
  position: "relative",
  pr: 5,
  fontFamily: "Montserrat, sans-serif",
};

export const CREATE_BUTTON_STYLES = {
  color: "rgba(31, 31, 31, 0.6)",
  fontWeight: "bold",
  fontFamily: "Montserrat, sans-serif",
  textTransform: "none",
  "&:hover": {
    backgroundColor: "transparent",
    color: "rgba(31, 31, 31, 0.8)",
  },
};
