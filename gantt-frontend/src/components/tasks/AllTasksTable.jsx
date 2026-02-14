import React from "react";
import {
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
  Paper,
} from "@mui/material";
import {
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
} from "@mui/icons-material";
import {
  CELL_STYLES,
  TABLE_CONTAINER_STYLES,
  TASKS_TABLE_BODY_STYLES,
  SORTABLE_HEADER_CELL_STYLES,
} from "./tableStyles.js";
import { toLocaleDateWithTimeHM } from "../../utils/datetime.js";

const AllTasksTable = ({ tasks, sortField, sortOrder, handleSort }) => {
  const renderSortIcon = (field) => {
    if (sortField !== field) {
      return null;
    }

    return sortOrder === "asc" ? (
      <ArrowUpwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    ) : (
      <ArrowDownwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    );
  };

  return (
    <TableContainer component={Paper} sx={TABLE_CONTAINER_STYLES}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell
              sx={SORTABLE_HEADER_CELL_STYLES}
              onClick={() => handleSort("team")}
            >
              <div style={{ display: "flex", alignItems: "center" }}>
                Команда
                {renderSortIcon("team")}
              </div>
            </TableCell>
            <TableCell
              sx={SORTABLE_HEADER_CELL_STYLES}
              onClick={() => handleSort("project")}
            >
              <div style={{ display: "flex", alignItems: "center" }}>
                Проект
                {renderSortIcon("project")}
              </div>
            </TableCell>
            <TableCell
              sx={SORTABLE_HEADER_CELL_STYLES}
              onClick={() => handleSort("stream")}
            >
              <div style={{ display: "flex", alignItems: "center" }}>
                Стрим
                {renderSortIcon("stream")}
              </div>
            </TableCell>
            <TableCell
              sx={SORTABLE_HEADER_CELL_STYLES}
              onClick={() => handleSort("name")}
            >
              <div style={{ display: "flex", alignItems: "center" }}>
                Название
                {renderSortIcon("name")}
              </div>
            </TableCell>
            <TableCell
              sx={SORTABLE_HEADER_CELL_STYLES}
              onClick={() => handleSort("deadline")}
            >
              <div style={{ display: "flex", alignItems: "center" }}>
                Дедлайн
                {renderSortIcon("deadline")}
              </div>
            </TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {tasks.map((task) => (
            <TableRow key={task.id} sx={TASKS_TABLE_BODY_STYLES}>
              <TableCell sx={CELL_STYLES}>{task.team_name || "-"}</TableCell>
              <TableCell sx={CELL_STYLES}>{task.project_name || "-"}</TableCell>
              <TableCell sx={CELL_STYLES}>{task.stream_name || "-"}</TableCell>
              <TableCell sx={CELL_STYLES}>{task.name}</TableCell>
              <TableCell sx={CELL_STYLES}>
                {task.deadline ? toLocaleDateWithTimeHM(task.deadline) : "-"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default AllTasksTable;
