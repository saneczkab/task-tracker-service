import React, { useEffect, useState } from "react";
import {
  CircularProgress,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { getAISummaryApi } from "../../api/analytics.js";

const formatRemainingLabel = (requestLimit) => {
  if (!requestLimit || requestLimit.remaining == null) {
    return null;
  }

  const remaining = requestLimit.remaining;
  if (remaining === 0) {
    return "осталось 0";
  }

  const word =
    remaining === 1
      ? "запрос"
      : remaining >= 2 && remaining <= 4
        ? "запроса"
        : "запросов";

  return `осталось ${remaining} ${word}`;
};

const AISummaryButton = ({
  tasks,
  teamId,
  analyticsFilters,
  token,
  requestLimit: requestLimitProp,
  onRequestLimitChange,
}) => {
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");
  const [requestLimit, setRequestLimit] = useState(requestLimitProp ?? null);

  useEffect(() => {
    setRequestLimit(requestLimitProp ?? null);
  }, [requestLimitProp]);

  const updateRequestLimit = (nextLimit) => {
    setRequestLimit(nextLimit);
    onRequestLimitChange?.(nextLimit);
  };

  const handleGetSummary = async () => {
    setLoading(true);
    setError("");
    setSummary("");

    try {
      const response = await getAISummaryApi(teamId, analyticsFilters, token);

      if (response.requestLimit) {
        updateRequestLimit(response.requestLimit);
      }

      if (response.ok) {
        setSummary(response.summary || "Нет данных для резюме");
        setOpenDialog(true);
      } else {
        if (response.status === 429) {
          setError("Вы достигли ежедневного лимита запросов!");
        } else {
          setError("Не удалось получить резюме. Попробуйте позже.");
        }
      }
    } catch (err) {
      setError("Ошибка при загрузке резюме: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const remainingLabel = formatRemainingLabel(requestLimit);
  const isLimitReached = requestLimit?.remaining === 0;

  return (
    <>
      <div className="flex flex-col items-end">
        <Button
          variant="contained"
          onClick={handleGetSummary}
          disabled={loading || tasks.length === 0 || isLimitReached}
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
            <span className="flex items-center gap-2">
              <span>ИИ резюме</span>
              {remainingLabel && (
                <span className="text-xs opacity-80">({remainingLabel})</span>
              )}
            </span>
          )}
        </Button>

        {error && (
          <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700 w-full">
            {error}
          </div>
        )}
      </div>

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
    </>
  );
};

export default AISummaryButton;
