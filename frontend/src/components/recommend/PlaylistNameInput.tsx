import React from "react";
import { TextField } from "@mui/material";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function PlaylistNameInput({ value, onChange }: Props) {
  return (
    <TextField
      label="Playlist Name"
      variant="outlined"
      fullWidth
      margin="normal"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}
