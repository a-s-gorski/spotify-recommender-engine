import { Button, CircularProgress, Box } from "@mui/material";

interface Props {
  loading: boolean;
  disabled: boolean;
  onClick: () => void;
}

export default function FetchButton({ loading, disabled, onClick }: Props) {
  return (
    <Box mt={3}>
      <Button
        variant="contained"
        color="primary"
        fullWidth
        onClick={onClick}
        disabled={disabled || loading}
        startIcon={loading ? <CircularProgress size={20} /> : null}
      >
        {loading ? "Fetching..." : "Get Recommendations"}
      </Button>
    </Box>
  );
}
