import { FormControl, InputLabel, Select, MenuItem } from "@mui/material";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function StrategySelector({ value, onChange }: Props) {
  return (
    <FormControl fullWidth margin="normal">
      <InputLabel id="strategy-label">Recommendation Strategy</InputLabel>
      <Select
        labelId="strategy-label"
        value={value}
        label="Recommendation Strategy"
        onChange={(e) => onChange(e.target.value)}
      >
        <MenuItem value="hybrid">Hybrid</MenuItem>
        <MenuItem value="clustering">Clustering</MenuItem>
        <MenuItem value="collaborative">Collaborative</MenuItem>
      </Select>
    </FormControl>
  );
}
