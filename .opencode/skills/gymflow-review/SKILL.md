---
name: gymflow-review
description: Revisa un diff de GymFlow frente a sus criterios de aceptación, arquitectura por capas y reglas de negocio; devuelve hallazgos concretos con archivo, impacto y comprobación sugerida. Úsala antes de revisión humana o cuando se solicite revisar una PR.
---

# Revisar cambios de GymFlow

Identificar la base de la PR o la revisión solicitada. Leer `AGENTS.md`,
`CONTEXT.md`, la issue y su spec. Examinar el diff completo y los archivos
relacionados que permitan comprobar un posible defecto. Incluir archivos
nuevos y cambios sin commit cuando formen parte del alcance.

En cambios de API, revisar estas invariantes cuando resulten afectadas:

- `interfaces → application → domain`; infraestructura solo en adaptadores
  y wiring. Pydantic no entra en dominio ni casos de uso.
- Cuenta y Cliente son distintos; `activo` de Cuenta no es estado de membresía.
  No exigir auth en rutas todavía públicas ni afirmar que V2 ya está implementada.
- Reservas: cliente activo y con pago, unicidad y aforo protegidos por transacción;
  cancelar libera plaza. No inventar vencimiento de pagos.
- `PUT` sustituye campos editables y conserva la fecha original de reserva.
  Revisar FK/RESTRICT y los errores HTTP realmente observables.
- Para futuros cambios de auth, revisar hash, salida sin contraseña, validación
  de token y permisos conforme a la spec de esa funcionalidad.

En tooling/documentación, comprobar que los comandos existen, que los enlaces
resuelven y que la guía distingue requisitos futuros de comportamiento entregado.
Comprobar que la bitácora y la PR describen evidencia real. No leer ni mostrar
el contenido de `.env` para una revisión ordinaria.

Priorizar defectos demostrables introducidos por el diff. Cada hallazgo debe
indicar archivo/línea, condición que lo dispara, impacto y una forma de comprobarlo.
Separar una limitación ya documentada de un defecto nuevo. Si no hay hallazgos,
decirlo e indicar qué no se pudo comprobar; no inventar problemas para completar
una lista. La revisión automática no sustituye la aprobación humana.

La revisión produce un informe: no editar, publicar comentarios, aprobar ni
mergear salvo que esas acciones se hayan autorizado por separado. Registrar
su resultado en la bitácora cuando forme parte de la implementación autorizada.
