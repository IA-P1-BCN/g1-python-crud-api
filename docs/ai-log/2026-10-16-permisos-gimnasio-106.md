# #106 — Permisos por rol y propietario (2026-10-16)

- Herramienta/modelo: Codex, GPT-6 según el entorno.
- Petición: completar las demás tareas asignadas, en orden y respetando el proyecto.
  Aclaración de la usuaria: «Só as próprias classes e reservas; criar vínculo
  explícito entre conta e treinador».
- Spec previa: `openspec/changes/add-gym-role-permissions/`; continúa sobre
  #105, #65, #66 y #67. Sin vínculo inferido por email/nombre/igualdad de IDs.
- Decisiones: admin gestiona todo y exporta; cliente lee su perfil de gimnasio,
  pagos y reservas, consulta catálogo y reserva solo para sí; staff gestiona
  sus clases y reservas asociadas. Los IDs ajenos devuelven 404; operaciones
  prohibidas, 403. No se permite a cliente cambiar asistencia ni a staff
  transferir una clase/reserva a otro entrenador.
- Arquitectura: Cuenta autenticada se inyecta en GymUseCases; la política vive
  en aplicación, GymScope en dominio y el filtro se aplica en SQL antes de
  paginar. Los controladores siguen convirtiendo entidades a schemas.
- Migración: `7a0f6a730e04` agrega id_entrenador nullable, UNIQUE y FK RESTRICT
  a users; sube versions a 0.4 sin alterar datos existentes. PUT exclusivo de
  admin asigna/desvincula una Cuenta staff; la siguiente petición relee vínculo
  y rol con el mismo JWT. No se ejecutó downgrade sobre la base poblada.
- Compatibilidad: el catálogo frontend deja de contar reservas individuales
  para obtener cupo, porque ahora son privadas. Usa GET /clases/{id}/cupo con
  datos agregados; el menú staff ofrece solo gestión de clases.
- Correcciones: Ruff detectó importación, fechas sin zona y un Decimal literal
  en los tests nuevos; corregidos. Los tests HTTP/MySQL pasaron a la primera.
- Skills: gymflow-review y gymflow-verify. Revisión de diff, spec y casos de
  abuso: filtros, IDs ajenos, cambio de propietario, asistencia, asignación
  exclusiva, FK, revocación de vínculo/rol y cuenta sin vínculo. Sin hallazgos
  pendientes en esa revisión; la aprobación humana sigue pendiente.
- Validación inicial: `task migrate`, `task lint`, `task test` (**363 aprobados,
  0 fallidos, 0 saltados**, HTTP/MySQL reales), `task spec:validate` (20/20),
  `git diff --check`. Frontend: **115 tests en 25 suites**, build aprobado.
  Persiste el aviso previo de deprecación de Starlette TestClient/httpx.
- Integración: main recibió después #109/#116 (Render y portal en raíz);
  incorporados a toda la cadena de PRs, hasta `1e1efb9`. Resueltos conflictos
  de imports/bitácora y menú preservando CORS, JWT y las rutas en raíz.
- Validación final tras integrar main: **372 tests backend aprobados, cero
  fallidos/saltados**, **117 tests frontend en 26 suites**, build aprobado,
  lint aprobado y OpenSpec **22/22**. Verificación AST de dominio/aplicación
  sin imports de infraestructura, interfaces, FastAPI, Pydantic o SQLAlchemy.
  El último ajuste de lint solo elimina una línea vacía en imports del test.
