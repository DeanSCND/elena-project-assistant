# Multi-stage build for Elena
FROM node:18-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Python backend
FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy backend dependencies
COPY backend/pyproject.toml backend/poetry.lock* ./backend/
WORKDIR /app/backend
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

# Copy backend code
COPY backend/ ./

# Copy documents
COPY backend/documents ./documents

# Copy built frontend (reset WORKDIR to /app first)
WORKDIR /app
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Back to backend directory for running the app
WORKDIR /app/backend

# Expose port
EXPOSE 8100

# Start command
CMD ["python", "app_v2.py"]
