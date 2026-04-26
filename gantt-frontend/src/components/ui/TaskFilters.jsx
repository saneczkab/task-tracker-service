import React from "react";
import { ToggleButtonGroup, ToggleButton } from "@mui/material";
import { TOGGLE_BUTTON_STYLES } from "../tasks/tableStyles.js";

const TaskFilters = ({
  filterMode,
  setFilterMode,
  teamFilter,
  setTeamFilter,
  teamName,
}) => {
  return (
    <div
      style={{
        display: "inline-flex",
        gap: "16px",
        flexWrap: "wrap",
        marginBottom: "16px",
      }}
    >
      <div
        style={{
          backgroundColor: "#F5F6F7",
          padding: "8px 12px",
          borderRadius: "8px",
          display: "inline-flex",
          alignItems: "center",
        }}
      >
        <ToggleButtonGroup
          value={teamFilter}
          exclusive
          onChange={(e, newValue) => {
            if (newValue !== null) {
              setTeamFilter(newValue);
            }
          }}
          aria-label="team filter"
          size="small"
          sx={{
            "& .MuiToggleButtonGroup-grouped": {
              border: "none",
              "&:not(:first-of-type)": {
                borderRadius: "8px",
                marginLeft: "8px",
              },
              "&:first-of-type": {
                borderRadius: "8px",
              },
            },
          }}
        >
          <ToggleButton
            value="selected"
            aria-label="selected team"
            sx={TOGGLE_BUTTON_STYLES}
          >
            {teamName}
          </ToggleButton>
          <ToggleButton
            value="all"
            aria-label="all teams"
            sx={TOGGLE_BUTTON_STYLES}
          >
            Все команды
          </ToggleButton>
        </ToggleButtonGroup>
      </div>

      <div
        style={{
          backgroundColor: "#F5F6F7",
          padding: "8px 12px",
          borderRadius: "8px",
          display: "inline-flex",
          alignItems: "center",
        }}
      >
        <ToggleButtonGroup
          value={filterMode}
          exclusive
          onChange={(e, newValue) => {
            if (newValue !== null) {
              setFilterMode(newValue);
            }
          }}
          aria-label="task filter"
          size="small"
          sx={{
            "& .MuiToggleButtonGroup-grouped": {
              border: "none",
              "&:not(:first-of-type)": {
                borderRadius: "8px",
                marginLeft: "8px",
              },
              "&:first-of-type": {
                borderRadius: "8px",
              },
            },
          }}
        >
          <ToggleButton
            value="all"
            aria-label="all tasks"
            sx={TOGGLE_BUTTON_STYLES}
          >
            Все задачи
          </ToggleButton>
          <ToggleButton
            value="my"
            aria-label="my tasks"
            sx={TOGGLE_BUTTON_STYLES}
          >
            Назначенные мне
          </ToggleButton>
        </ToggleButtonGroup>
      </div>
    </div>
  );
};

export default TaskFilters;
