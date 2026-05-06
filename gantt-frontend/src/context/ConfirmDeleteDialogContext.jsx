import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from "@mui/material";

const ConfirmDeleteDialogContext = createContext(null);

export function ConfirmDeleteDialogProvider({ children }) {
  const [open, setOpen] = useState(false);
  const [objectLabel, setObjectLabel] = useState("");
  const resolveRef = useRef(null);

  const confirm = useCallback((object) => {
    return new Promise((resolve) => {
      setObjectLabel(object);
      resolveRef.current = resolve;
      setOpen(true);
    });
  }, []);

  const finish = useCallback((value) => {
    const r = resolveRef.current;
    resolveRef.current = null;
    setOpen(false);
    setObjectLabel("");
    r?.(value);
  }, []);

  const value = useMemo(() => ({ confirm }), [confirm]);

  return (
    <ConfirmDeleteDialogContext.Provider value={value}>
      {children}
      <Dialog open={open} onClose={() => finish(false)}>
        <DialogTitle>Подтверждение</DialogTitle>
        <DialogContent>
          Вы действительно хотите удалить {objectLabel}?
        </DialogContent>
        <DialogActions>
          <Button variant="text" color="primary" onClick={() => finish(false)}>
            Нет
          </Button>
          <Button
            onClick={() => finish(true)}
            variant="contained"
            color="primary"
          >
            Да
          </Button>
        </DialogActions>
      </Dialog>
    </ConfirmDeleteDialogContext.Provider>
  );
}

export function useConfirmDelete() {
  const ctx = useContext(ConfirmDeleteDialogContext);
  if (!ctx) {
    throw new Error("useConfirmDelete requires ConfirmDeleteDialogProvider");
  }
  return ctx;
}
