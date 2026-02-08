# Multi-stage build for unified frontend + backend container (Cloud Run)

# Stage 1: Build frontend (React)
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./

# CRA build-time API base (optional)
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

RUN npm run build

# Stage 2: Backend + Nginx + Supervisor
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/

COPY --from=frontend-builder /app/frontend/build /usr/share/nginx/html

COPY nginx/unified.conf /etc/nginx/conf.d/default.conf
COPY supervisor/app.conf /etc/supervisor/conf.d/app.conf

RUN chmod +x backend/start.sh && \
    sed -i 's/\r$//' backend/start.sh || true

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
