#!/bin/sh
# Arranque del contenedor en Render: migraciones y después el servidor.
set -e

echo "GymFlow API: aplicando migraciones (alembic upgrade head)..."
alembic upgrade head

puerto="${PORT:-10000}"
echo "GymFlow API: arrancando uvicorn en 0.0.0.0:${puerto}..."
exec uvicorn main:app --host 0.0.0.0 --port "${puerto}"
