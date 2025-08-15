# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_SPOTIFY_CLIENT_ID
ARG VITE_BACKEND_URL
ARG VITE_SPOTIFY_REDIRECT_URI

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 5173

CMD ["nginx", "-g", "daemon off;"]
