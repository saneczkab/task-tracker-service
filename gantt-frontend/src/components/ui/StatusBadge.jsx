import React from "react";
import { Box, Typography } from "@mui/material";

export const getStatusColors = (statusName) => {
  const name = (statusName || "").toLowerCase().trim();
  if (name === "to do") return { bg: "#ffebee", text: "#c62828", border: "#ef9a9a" };
  if (name === "doing") return { bg: "#fff9c4", text: "#f57f17", border: "#fff59d" };
  if (name === "done") return { bg: "#e8f5e9", text: "#2e7d32", border: "#a5d6a7" };
  return { bg: "#e3f2fd", text: "#1565c0", border: "#90caf9" };
};

const StatusBadge = ({ statusName }) => {
  if (!statusName || statusName === "-") {
    return <Typography variant="body2" sx={{ color: "text.secondary" }}>-</Typography>;
  }

  const { bg, text, border } = getStatusColors(statusName);
  
  return (
    <Box
      sx={{
        backgroundColor: bg,
        color: text,
        border: `1px solid ${border}`,
        px: 1,
        py: 0.25,
        borderRadius: 1,
        display: "inline-block",
      }}
    >
      <Typography variant="body2" sx={{ fontWeight: 500, fontFamily: "Montserrat, sans-serif", fontSize: "0.8125rem" }}>
        {statusName}
      </Typography>
    </Box>
  );
};

export default StatusBadge;

