# Imagen de producción de la GymFlow API. Render la construye en cada deploy
# de `main` (ver render.yaml). Multi-stage con uv: el builder instala las
# dependencias del uv.lock y la imagen final solo lleva el entorno virtual.

FROM node:24-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Capa de dependencias: solo cambia cuando cambia el lock (mejor caché).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
RUN chmod +x scripts/docker-entrypoint.sh

FROM python:3.14-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=10000

WORKDIR /app

RUN useradd --create-home --uid 1000 appuser

COPY --from=builder --chown=appuser:appuser /app /app
COPY --from=frontend-builder --chown=appuser:appuser /frontend/dist/frontend/browser /app/static
# WORKDIR crea /app como root: el proceso sin privilegios necesita escribir
# dentro (p. ej. el directorio de logs que crea la aplicación).
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 10000

# Render inyecta $PORT (10000 por defecto); el entrypoint aplica migraciones
# y arranca uvicorn en ese puerto.
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
