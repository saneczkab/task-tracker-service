import React from "react";

const CurrentTimeMarker = ({ xNow }) => {
  return (
    <div
      style={{
        position: "absolute",
        left: xNow,
        top: 66,
        bottom: 0,
        width: 2,
        background: "#ff0000",
        zIndex: 42,
      }}
    />
  );
};

export default CurrentTimeMarker;
