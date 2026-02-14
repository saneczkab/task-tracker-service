import React from "react";
import { Button } from "@mui/material";

const Topbar = () => {
  return (
    <header className="w-full h-14 bg-[#F5F6F7] border-b border-gray-200">
      <div className="h-full flex items-center gap-4 px-4">
        <Button variant="text" content="a" href="/">
          Gantt
        </Button>

        <Button variant="text" content="a" href="/login">
          Личный кабинет
        </Button>
      </div>
    </header>
  );
};

export default Topbar;
