# Conseillify - Spotify Music Recommendation System

A full-stack application that provides personalized Spotify music recommendations using multiple machine learning approaches including clustering-based and collaborative filtering algorithms.

## Architecture Overview

The system consists of three main components:

- **Frontend (React + TypeScript)**: User interface with Spotify integration
- **Auth Backend (Spring Boot)**: JWT-based authentication and authorization
- **Recommendation Backend (FastAPI)**: ML-powered recommendation engine
- **Reverse Proxy (Nginx)**: Routes requests and serves static content

## Project Structure

```
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── AuthProvider.tsx # JWT authentication context
│   │   └── App.tsx         # Main application
│   ├── Dockerfile
│   └── nginx.conf
├── auth-backend/            # Spring Boot authentication service
│   ├── src/main/java/com/example/authbackend/
│   │   ├── controllers/    # REST controllers
│   │   ├── models/         # JPA entities
│   │   ├── security/       # JWT & security config
│   │   └── services/       # Business logic
│   └── Dockerfile
├── recommend-backend/       # FastAPI recommendation service
│   ├── src/
│   │   ├── auth/           # API key authentication
│   │   ├── recommend/      # Recommendation algorithms
│   │   │   ├── clustering/ # PostgreSQL + pgvector
│   │   │   └── collaborative/ # MongoDB-based filtering
│   └── Dockerfile
├── docker-compose.yaml      # Multi-service orchestration
├── nginx.conf              # Reverse proxy configuration
└── .env.example            # Environment variables template
```

## Features

### Authentication & Authorization
- **JWT-based authentication** with refresh tokens
- **Role-based access control** (USER, MODERATOR, ADMIN)
- **Spotify OAuth 2.0 integration** with PKCE flow
- **Secure token management** with automatic refresh

### Music Recommendations
- **Clustering-based recommendations**: Uses TF-IDF vectorization with PostgreSQL + pgvector for similarity search
- **Collaborative filtering**: MongoDB-based co-occurrence analysis
- **Hybrid approach**: Combines both methods for improved accuracy
- **Real-time Spotify integration**: Fetches user's recently played tracks

### User Experience
- **Modern React UI** with Material-UI components
- **Responsive design** with dark theme
- **Spotify playlist creation** from recommendations
- **Real-time recommendation generation**

## 🛠️ Technology Stack

### Frontend
- **React 19** with TypeScript
- **Material-UI (MUI)** for components
- **Vite** for build tooling
- **Spotify Web API** integration

### Auth Backend
- **Spring Boot 3** with Java 17
- **Spring Security** with JWT
- **JPA/Hibernate** for data persistence
- **PostgreSQL** database
- **Maven** for dependency management

### Recommendation Backend
- **FastAPI** with Python 3.12
- **scikit-learn** for TF-IDF vectorization
- **PostgreSQL + pgvector** for similarity search
- **MongoDB** for collaborative filtering
- **Motor** for async MongoDB operations
- **SQLAlchemy** with async support

### Infrastructure
- **Docker & Docker Compose** for containerization
- **Nginx** as reverse proxy
- **Multi-stage Docker builds** for optimization

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Frontend Configuration
FRONTEND_URL=https://localhost:5173
VITE_SPOTIFY_CLIENT_ID=your_spotify_client_id
VITE_BACKEND_URL=http://localhost:8080
VITE_SPOTIFY_REDIRECT_URI=http://127.0.0.1:5173

# Database Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=spotify
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db

# ML Configuration
TOKENIZER_PATH=artifacts/vectorizer.pkl
API_KEY=your_secure_api_key
```

### Nginx Configuration

The reverse proxy setup routes requests:

```nginx
server {
    listen 120;
    server_name recommend.tojest.dev;

    # Frontend at root
    location / {
        proxy_pass http://127.0.0.1:5173;
        # WebSocket support for Vite HMR
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Spring Boot backend at /auth/
    location /auth/ {
        proxy_pass http://127.0.0.1:8080/;
    }
}
```

## Live Demo

The application is hosted and available at: **https://recommend.tojest.dev/**

Try it out with your Spotify account to see the recommendation engine in action!

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local development)
- Java 17+ (for local development)
- Python 3.12+ (for local development)
- PostgreSQL with pgvector extension
- MongoDB
- Spotify Developer Account

### Quick Start with Docker

1. **Clone the repository**:
```bash
git clone <repository-url>
cd conseillify
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**:
```bash
docker-compose up -d
```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Auth API: http://localhost:8080
   - Recommendation API: http://localhost:8000

### Manual Setup

#### Database Setup

**PostgreSQL with pgvector**:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE playlists (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    tracks TEXT[],
    embedding vector(500)
);
```

**MongoDB**:
```javascript
// Collections: playlists, tracks
db.createCollection("playlists");
db.createCollection("tracks");
```

#### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

#### Auth Backend Development

```bash
cd auth-backend
./mvnw spring-boot:run
```

#### Recommendation Backend Development

```bash
cd recommend-backend
pip install uv
uv venv
uv pip install -r pyproject.toml
python main.py
```

## 📡 API Endpoints

### Authentication Service (Port 8080)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/signin` | POST | User login |
| `/api/auth/signup` | POST | User registration |
| `/api/auth/refreshtoken` | POST | Refresh JWT token |
| `/api/test/user` | GET | Protected user endpoint |
| `/api/test/admin` | GET | Admin-only endpoint |

### Recommendation Service (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/recommend/recommend-clustering` | GET | Clustering-based recommendations |
| `/recommend/recommend-collaborative` | GET | Collaborative filtering |
| `/recommend/recommend-hybrid` | GET | Hybrid recommendations |
| `/health` | GET | Service health check |

## Security Implementation

### JWT Authentication Flow

1. **User Authentication**: Spring Boot validates credentials
2. **Token Generation**: Creates JWT access token + refresh token
3. **Token Storage**: Frontend stores tokens securely
4. **API Protection**: Endpoints validate JWT tokens
5. **Automatic Refresh**: Expired tokens refresh automatically

### API Security

- **API Key Authentication**: Recommendation service uses API keys
- **CORS Configuration**: Properly configured for cross-origin requests
- **Role-based Authorization**: Different access levels for endpoints

## Recommendation Algorithms

### Clustering-Based Recommendations

1. **TF-IDF Vectorization**: Playlist names converted to vectors
2. **pgvector Similarity**: PostgreSQL extension for vector operations
3. **K-Nearest Neighbors**: Finds similar playlists
4. **Track Aggregation**: Combines tracks from similar playlists

```python
# Core algorithm implementation
async def recommend_clustering(vectorizer, playlist_name, k=10, n_neighbors=5):
    query_vec = vectorizer.transform([playlist_name]).toarray()[0].tolist()
    
    stmt = (
        select(Playlist)
        .order_by(Playlist.embedding.l2_distance(query_vec))
        .limit(n_neighbors)
    )
    similar_playlists = await session.execute(stmt)
    # Aggregate and return top-k tracks
```

### Collaborative Filtering

1. **Co-occurrence Analysis**: Finds playlists containing seed tracks
2. **Track Frequency**: Counts track appearances across playlists
3. **Recommendation Ranking**: Orders by co-occurrence frequency

```python
# MongoDB-based collaborative filtering
async def recommend_collaborative(client, query_uris, k=10):
    cursor = db.playlists.find(
        {"tracks": {"$in": query_uris}},
        {"tracks": 1}
    ).limit(max_neighbors)
    
    track_counter = Counter()
    async for doc in cursor:
        track_counter.update(doc["tracks"])
    
    return [t for t, _ in track_counter.most_common() if t not in query_uris][:k]
```

### Hybrid Approach

Combines collaborative filtering with clustering fallback:

1. **Primary**: Collaborative filtering for immediate results
2. **Fallback**: Clustering-based when collaborative insufficient
3. **Deduplication**: Removes duplicate recommendations
4. **Ranking**: Maintains recommendation quality

## Docker Compose Services

The `docker-compose.yaml` orchestrates three services:

```yaml
services:
  recommend-backend:    # FastAPI recommendation engine
    build: ./recommend-backend
    ports: ["8000:8000"]
    
  auth-backend:         # Spring Boot authentication
    build: ./auth-backend
    ports: ["8080:8080"]
    depends_on: [recommend-backend]
    
  frontend:             # React frontend with Nginx
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [auth-backend]
```

## 🧪 Testing

### Frontend Testing
```bash
cd frontend
npm run lint
```

### Backend Testing
```bash
cd auth-backend
./mvnw test

cd recommend-backend
pytest
```

## Deployment

### Production Considerations

1. **Environment Variables**: Use proper secrets management
2. **Database Security**: Configure secure database connections
3. **SSL/TLS**: Enable HTTPS in production
4. **Load Balancing**: Consider multiple instances
5. **Monitoring**: Add logging and metrics collection

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check frontend URL in backend CORS configuration
2. **Database Connection**: Verify database credentials and connectivity
3. **Spotify API**: Ensure valid client ID and redirect URI
4. **Token Expiration**: Check JWT token expiration settings
5. **Port Conflicts**: Ensure ports 5173, 8080, 8000 are available

### Logs

Check service logs:
```bash
docker-compose logs frontend
docker-compose logs auth-backend
docker-compose logs recommend-backend
```

---
