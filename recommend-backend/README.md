# Spotify Recommender Engine - Backend

This directory contains the backend service for the Spotify Recommender Engine project.

## Structure

- `app/` - Main application code (API, business logic)
- `requirements.txt` - Python dependencies
- `Dockerfile` - Containerization setup
- `config/` - Configuration files
- `tests/` - Unit and integration tests

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/spotify-recommender-engine.git
    cd spotify-recommender-engine/backend
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure environment:**
    - Copy `.env.example` to `.env` and update values as needed.

4. **Run the backend:**
    ```bash
    python -m app
    ```

    Or with Docker:
    ```bash
    docker build -t spotify-backend .
    docker run --env-file .env -p 8000:8000 spotify-backend
    ```

## Testing

```bash
pytest
```

## API

- RESTful endpoints for recommendations and user management.
- See `app/routes/` for details.

## License

MIT License.