# 2026-10-19 — Admin demo público (continuación #118/#29)

- **Spec:** [add-admin-demo](../../openspec/changes/add-admin-demo/).
- **Herramienta/modelo:** OpenCode, OpenAI gpt-6.1-sol. Flujo de verificación
  `gymflow-verify` disponible en esta sesión aplicado a spec, lint y tests.
- **Prompts clave:** cargar el seed del despliegue y publicar en README una
  Cuenta admin demo con contraseña accesible; ejecutar el plan.
- **Implementación:** helper seed_admin_demo, invocado dentro de la transacción
  de seed_gym. Cuenta activa, rol admin, sin vínculos; hash Argon2id de la
  contraseña demo pública. Se omite si email de Cuenta o Cliente está ocupado.
  README distingue esta identidad del admin privado de ADMIN_EMAIL/PASSWORD.
  El entrypoint ya ejecuta python -m scripts.seed_gym antes de uvicorn.
- **Decisiones:** mantener el seed idempotente, no restablecer claves de
  identidades existentes ni asignarles privilegios. Sin migración, variables
  nuevas o servicio de pago. Las credenciales ficticias demo se publican por
  petición expresa; ninguna credencial privada se incluye.
- **Errores/correcciones:** primera suite: 379 aprobados y 1 fallo en un test
  previo que probaba ADMIN_PASSWORD actual contra un admin local preexistente
  con otra clave. Ese test ahora crea un admin de prueba con email único,
  conservando la validación de login y limpiando solo su identidad. No se ha
  cambiado la contraseña de la Cuenta privada ni se ha eliminado la prueba.
- **Validación:**
  - task spec:validate: 24 elementos válidos.
  - task lint: limpio; task db:up y task migrate correctos (esquema 0.4).
  - Suite final task test: 380 aprobados, 0 fallidos, 0 saltados; MySQL real.
    Aviso Starlette/httpx de deprecación existente.
  - Cuatro casos nuevos comprueban hash, alta, repetición tras cambios, email
    ocupado en Cuenta/Cliente, login por HTTP y acceso al listado admin.
  - task seed dos veces: primera crea admin demo; segunda lo omite.
    Login posterior de la Cuenta documentada, perfil y listado de Cuentas
    devuelven 200 mediante TestClient contra MySQL local.
  - Render MCP list_workspaces devuelve unauthorized. Prueba pública de login
    demo: 401 antes de publicar este cambio. No se afirma carga remota exitosa.
- **Pendiente:** revisión y merge; el push a main activará el auto-deploy con
  seed en Render. Verificar login público tras terminar ese despliegue. Sin
  acceso autorizado de gestión no se puede ejecutar el seed remoto manualmente.
