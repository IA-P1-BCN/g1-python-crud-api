# Entrenador con Cuenta desde el admin — #134

- Herramienta: ZCode (GLM).
- Prompt: implementar el HOTFIX #134 — crear un entrenador desde el panel de
  admin debe crear también su usuario (nombre + email); reflejar la tabla
  users en DATABASE_SPEC.md.
- Decisión/alcance: `POST /v1/entrenadores` acepta `email` opcional;
  `cuenta_repository.create_entrenador` hace el alta conjunta en un mismo
  flush (precedente de `create_cliente`); contraseña inicial demo común
  `Demo56789012` (constante en cuenta_use_cases); respuestas de
  entrenadores resuelven `id_user`/`email` de la cuenta vinculada; PUT
  rechaza email (422); POST exige admin explícito (requires_admin). El
  formulario pide email obligatorio, muestra credenciales al crear y el
  listado muestra la cuenta o "sin cuenta". DATABASE_SPEC: users como
  diccionario completo con cardinalidades.
- Errores corregidos durante la sesión: typo `telephone`→`telefono` cazado
  por los tests unitarios; `editable()` de test_gym_crud pelaba el nombre de
  entrenadores (regla final: conservarlo solo con `especialidad`) y el
  assert de pertenencia pasó a paginar (la BD compartida supera 100 filas).
- Verificación: 398 tests en verde (unidad + integración MySQL real),
  `task lint`, `task spec:validate` 27/27, `ng build` y `task demo`
  completos.
- Revisión: la evidencia automatizada no sustituye la revisión humana;
  vigilar la política de contraseña inicial (hoy patrón demo documentado).
