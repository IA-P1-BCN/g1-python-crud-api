#!/bin/sh
# Arranque del contenedor en Render: lo que hace `task demo` (migraciones y
# seed idempotente) y lo que hace `task dev` (uvicorn), en ese orden.
set -e

echo "GymFlow API: aplicando migraciones (alembic upgrade head)..."
intentos=0
until alembic upgrade head; do
  intentos=$((intentos + 1))
  if [ "$intentos" -ge 40 ]; then
    echo "ERROR: MySQL no disponible tras ${intentos} intentos." >&2
    exit 1
  fi
  echo "MySQL aun no disponible (intento ${intentos}/40); reintento en 5 s..."
  sleep 5
done

echo "GymFlow API: cargando datos demo y cuentas (seed idempotente)..."
if ! python -m scripts.seed_gym; then
  echo "ERROR: el seed ha fallado (revisa ADMIN_PASSWORD y MYSQL_*)." >&2
  exit 1
fi

puerto="${PORT:-10000}"
echo "GymFlow API: arrancando uvicorn en 0.0.0.0:${puerto}..."
exec uvicorn main:app --host 0.0.0.0 --port "${puerto}"
