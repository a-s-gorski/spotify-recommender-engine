import React from "react";
import { Box, Slider, Typography } from "@mui/material";

interface Props {
  value: number;
  onChange: (value: number) => void;
  max: number;
}

export default function RecommendationSlider({ value, onChange, max }: Props) {
  return (
    <Box mt={2}>
      <Typography gutterBottom>
        Number of Recommendations: {value}
      </Typography>
      <Slider
        min={1}
        max={max}
        value={value}
        onChange={(e, newValue) => onChange(newValue as number)}
        valueLabelDisplay="auto"
      />
    </Box>
  );
}
