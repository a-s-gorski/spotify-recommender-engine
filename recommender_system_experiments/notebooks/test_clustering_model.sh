curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_name": "chill lofi beats",
    "k": 10,
    "n_neighbors": 5
  }'