import React, { useState } from "react";
import {
  CircularProgress,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { getAISummaryApi } from "../../api/analytics.js";

const AISummaryButton = ({ tasks, teamId, analyticsFilters, token }) => {
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");

  const handleGetSummary = async () => {
    setLoading(true);
    setError("");
    setSummary("");

    try {
      const response = await getAISummaryApi(teamId, analyticsFilters, token);

      if (response.ok) {
        setSummary(response.summary || "Нет данных для резюме");
        setOpenDialog(true);
      } else {
        setError("Не удалось получить резюме. Попробуйте позже.");
      }
    } catch (err) {
      setError("Ошибка при загрузке резюме: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        variant="contained"
        onClick={handleGetSummary}
        disabled={loading || tasks.length === 0}
        sx={{
          textTransform: "none",
          fontSize: "14px",
          padding: "8px 16px",
          fontFamily: "Montserrat, sans-serif",
          color: "#2563EB",
          backgroundColor: "#E5E7EB",
          boxShadow: "none",
          "&:hover": {
            backgroundColor: "#D1D5DB",
            boxShadow: "none",
          },
          "&.Mui-disabled": {
            color: "#93C5FD",
            backgroundColor: "#E5E7EB",
          },
        }}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <CircularProgress size={16} sx={{ color: "white" }} />
            Загрузка...
          </span>
        ) : (
          "ИИ резюме"
        )}
      </Button>

      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>ИИ резюме</DialogTitle>
        <DialogContent dividers>
          {summary ? (
            <div className="whitespace-pre-wrap text-sm text-gray-700">
              {summary}
            </div>
          ) : (
            <p className="text-gray-500">Загрузка...</p>
          )}
        </DialogContent>
      </Dialog>

      {error && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}
    </>
  );
};

export default AISummaryButton;
