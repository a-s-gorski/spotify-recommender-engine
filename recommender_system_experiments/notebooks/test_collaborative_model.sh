curl -X POST http://localhost:8000/recommend/ \
  -H "Content-Type: application/json" \
  -d '{
    "track_uris": ["spotify:track:1xznGGDReH1oQq0xzbwXa3"],
    "top_k": 10,
    "max_neighbors": 50
  }'
