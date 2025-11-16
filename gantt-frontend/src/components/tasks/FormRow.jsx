import React from "react";
import { Box, Typography } from "@mui/material";

const FormRow = ({ label, children }) => (
    <Box
        sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", sm: "220px 1fr" },
            alignItems: "center",
            gap: 2,
            px: 1.5,
            py: 1,
            borderRadius: 1,

            "&:hover": { backgroundColor: "#EDEDED" },

            "& .MuiOutlinedInput-root .MuiOutlinedInput-notchedOutline": {
                borderColor: "transparent"
            },
            "& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline": {
                borderColor: "transparent"
            },
            "& .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline": {
                borderColor: "transparent"
            }
        }}
    >
        <Typography
            sx={{
                color: "text.secondary",
                fontFamily: '"Roboto Flex","Roboto",sans-serif',
                fontWeight: 700
            }}
        >{label}
        </Typography>
        <Box>{children}</Box>
    </Box>
);

export default FormRow;