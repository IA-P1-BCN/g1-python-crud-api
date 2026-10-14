## Context

La API ya tiene uv, Taskfile, ruff y pytest. El equipo usa distintas herramientas
de IA y sus archivos locales están ignorados. Ver `proposal.md` para el alcance.

## Decisions

- Instalar `@fission-ai/openspec` 1.14.1 como dependencia de desarrollo local,
  fijada en `package.json` y `package-lock.json`. Una instalación global no
  garantizaría que todas las personas usen la misma CLI.
- Usar `openspec/specs/` como única carpeta canónica de especificaciones. Es la
  `specs/` solicitada en V2, dentro de la estructura propia de OpenSpec.
- Inicializar con `--tools none`: el contrato y los comandos de terminal
  funcionan con cualquier agente. Cada persona puede generar la integración
  de su herramienta localmente sin imponer una al resto del equipo.
- Usar el esquema oficial `spec-driven`, con contexto y reglas del proyecto.
  Mantener las propuestas en `changes/` hasta completar su revisión; después,
  archivarlas para consolidar los contratos en `specs/`.
- La bitácora describe trabajo real, incluyendo limitaciones del entorno.

## Risks / Trade-offs

- Node.js >=20.19.0 es un requisito adicional para escribir/validar specs;
  no es una dependencia del servidor Python.
- `npm audit` identifica GHSA-vfj7-8cjw-p6xm en `braces`, dependencia indirecta
  de OpenSpec vía `fast-glob`/`micromatch`. A 2026-10-14 no hay versión corregida
  publicada. Afecta al procesamiento de patrones anidados en la herramienta de
  desarrollo. Conservar el aviso para revisión; no aplicar el downgrade
  incompatible sugerido por `npm audit fix --force` ni ocultar el resultado.
  Fuente: https://github.com/advisories/GHSA-vfj7-8cjw-p6xm.
- La CLI comprueba la estructura del contrato, pero no demuestra que el código
  lo cumpla ni que la spec se escribiera primero; eso se verifica en tests y PR.

## Migration Plan

Ejecutar `task spec:install` y `task spec:validate`. Las personas que solo
ejecutan la API conservan su flujo `task install`/`task dev`. No hay migración SQL.
