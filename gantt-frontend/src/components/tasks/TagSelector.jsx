import React, { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Menu,
  MenuItem,
  IconButton,
  Tooltip,
  Divider,
  InputAdornment,
} from "@mui/material";
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ArrowDropDown as ArrowDropDownIcon,
  Check as CheckIcon,
} from "@mui/icons-material";

const DEFAULT_COLOR = "#2196f3";

const TagSelector = ({
  teamTags = [],
  selectedTagIds = [],
  onTagToggle,
  onCreateTag,
  onDeleteTag,
}) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [createMode, setCreateMode] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const [newTagColor, setNewTagColor] = useState(DEFAULT_COLOR);
  const [creating, setCreating] = useState(false);

  const handleOpen = (e) => setAnchorEl(e.currentTarget);
  const handleClose = () => {
    setAnchorEl(null);
    setCreateMode(false);
    setNewTagName("");
    setNewTagColor(DEFAULT_COLOR);
  };

  const handleCreate = async () => {
    if (!newTagName.trim()) return;
    setCreating(true);
    await onCreateTag(newTagName.trim(), newTagColor);
    setNewTagName("");
    setNewTagColor(DEFAULT_COLOR);
    setCreateMode(false);
    setCreating(false);
  };

  const open = Boolean(anchorEl);
  const isDuplicate = teamTags.some(
    (tag) => tag.name.trim().toLowerCase() === newTagName.trim().toLowerCase(),
  );

  return (
    <Box>
      <Box
        onClick={handleOpen}
        sx={{
          display: "flex",
          alignItems: "center",
          minHeight: 40,
          px: 1.5,
          py: 0.5,
          border: "1px solid",
          borderRadius: 1,
          cursor: "pointer",
        }}
      >
        <Typography variant="body2" sx={{ flexGrow: 1 }}>
          Выберите теги...
        </Typography>
      </Box>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        slotProps={{
          paper: {
            sx: { width: anchorEl?.offsetWidth ?? 280, maxHeight: 400 },
          },
        }}
        anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
        transformOrigin={{ vertical: "top", horizontal: "left" }}
      >
        {teamTags.length === 0 && !createMode && (
          <MenuItem disabled>
            <Typography variant="body2" color="text.secondary">
              Нет тегов. Создайте первый!
            </Typography>
          </MenuItem>
        )}

        {teamTags.map((tag) => {
          const isSelected = selectedTagIds.includes(tag.id);
          return (
            <MenuItem
              key={tag.id}
              onClick={() => onTagToggle(tag.id)}
              sx={{ display: "flex", alignItems: "center", gap: 1, pr: 1 }}
            >
              <CheckIcon
                sx={{
                  fontSize: 16,
                  visibility: isSelected ? "visible" : "hidden",
                }}
              />
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  bgcolor: tag.color,
                  flexShrink: 0,
                }}
              />
              <Typography variant="body2" sx={{ flexGrow: 1 }}>
                {tag.name}
              </Typography>
              <Tooltip title="Удалить тег из команды">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteTag(tag.id);
                  }}
                  sx={{ p: 0.3 }}
                >
                  <DeleteIcon sx={{ fontSize: 14 }} />
                </IconButton>
              </Tooltip>
            </MenuItem>
          );
        })}

        <Divider />

        {createMode ? (
          <Box
            sx={{
              px: 2,
              py: 1,
              display: "flex",
              flexDirection: "column",
              gap: 1,
            }}
          >
            <TextField
              size="small"
              placeholder="Название тега"
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
              onKeyDown={(e) => {
                e.stopPropagation();
                if (e.key === "Enter" && !isDuplicate) handleCreate();
              }}
              error={isDuplicate}
              helperText={
                isDuplicate
                  ? "Тег с таким названием уже существует!"
                  : undefined
              }
              autoFocus
              fullWidth
              slotProps={{
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <input
                        type="color"
                        value={newTagColor}
                        onChange={(e) => setNewTagColor(e.target.value)}
                        style={{
                          width: 24,
                          height: 24,
                          border: "none",
                          cursor: "pointer",
                          padding: 0,
                          borderRadius: 4,
                          background: "none",
                        }}
                      />
                    </InputAdornment>
                  ),
                },
              }}
            />
            <Box sx={{ display: "flex", gap: 1 }}>
              <Button
                size="small"
                variant="contained"
                onClick={handleCreate}
                disabled={!newTagName.trim() || creating || isDuplicate}
                fullWidth
              >
                Создать
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() => {
                  setCreateMode(false);
                  setNewTagName("");
                }}
                fullWidth
              >
                Отмена
              </Button>
            </Box>
          </Box>
        ) : (
          <MenuItem onClick={() => setCreateMode(true)}>
            <AddIcon sx={{ fontSize: 16, mr: 1 }} />
            <Typography variant="body2">Создать тег</Typography>
          </MenuItem>
        )}
      </Menu>
    </Box>
  );
};

export default TagSelector;
