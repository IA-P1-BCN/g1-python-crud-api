# Contenedorización de API y frontend — #28

- Herramienta: opencode (mimo-v2.6-flash-free).
- Prompt: crear una task que arranque frontend y API, después «todo hasta la
  inicialización», luego Docker Compose con API + frontend y una cuenta de test
  `demo@gymflow.com` en las migraciones; al final, `task docker:up` equivalente a
  `task up` pero en Docker.
- Spec previa: sin cambio en `openspec/changes/`; la issue #28 (Contenedorización
  con Docker) y `docs/client/CLIENT_SPECS_V2_USER_MNG.md` («Contenedorización con
  Docker y docker-compose») cubren el alcance. Se documenta la ausencia de spec
  en esta entrada.
- Decisiones aceptadas:
  - `task up` = init en host (deps, `.env`, MySQL, migraciones, seed, `npm ci` si
    falta) + API con recarga y Angular en paralelo (`deps`); sin tests.
  - `task docker:up` = `env` + `compose` + seed con
    `docker compose exec -T api python -m scripts.seed_gym` (no `compose run`:
    el `container_name` fijo chocaría con el contenedor en marcha).
  - `task db:up` levanta **solo** `mysql` (`--wait mysql`) para no pisar los
    puertos 8000/4200 de `task up` ni los tests; `task db:down` sigue parando
    todo el proyecto.
  - Compose con tres servicios; la API usa `MYSQL_HOST=mysql`:3306 internos y
    `env_file: .env` (`SECRET_KEY` obligatoria); healthcheck de la API con
    `start_period` para Alembic; frontend nginx reenvía `/v1` a `api:8000` con
    fallback SPA; puertos solo en 127.0.0.1.
  - La cuenta demo entra por migración (`ca6c9ed6b7e8`) con hash Argon2id
    precalculado (no plaintext en el repo), idempotente por email y con
    downgrade que solo borra si el hash coincide; el texto plano se documenta en
    README.
- Errores corregidos (reproducción de `docker:up` fallido):
  - El `exec` del seed falló con «service api is not running»: había dos engines
    (docker nativo `default` + Docker Desktop `desktop-linux`) y Desktop cambió
    el contexto activo entre el `up` (nativo) y el `exec` (vacío). Se limpió el
    arranque parcial en Desktop, se restauró `MYSQL_PORT=3307`, se ejecutó el
    seed en el stack nativo y se volvió al contexto `default`.
  - La primera reproducción en Desktop chocó en el bind 8000 (lo retenía el
    `gym-api` nativo); se descartó ese contexto.
- Verificación: `task lint` y `task test` (ver Validación de la PR);
  `docker compose config` correcto; stack nativo en marcha con
  `/health/db` → 0.3, frontend 200 y login `demo@gymflow.com` → JWT.
- Revisión: `frontend/README.md` (secciones `task up`/`docker:up` y cuenta demo)
  queda en el stash de la rama de #110 porque ese fichero nace en la PR #110;
  aplicar tras su merge. La build de `frontend` en Compose requiere los fuentes
  de Angular que llegan con #110: mergear #110 primero o en el mismo despliegue.
