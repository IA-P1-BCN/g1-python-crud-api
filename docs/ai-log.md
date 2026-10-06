# Bitácora de desarrollo con IA

## Issue 10 y cambio de alcance del 6 de octubre de 2026

Herramienta: Codex. La usuaria dirige el alcance y revisa el resultado;
la revisión humana del PR sigue siendo obligatoria antes del merge.

Prompts que determinaron el trabajo:

- «agora preciso fazer a tarefa que esta asinada a mim API REST con
  operaciones CRUD básicas #10».
- «ler la carpeta docs veja se encontra» y las peticiones de actualizar
  el repositorio al subir los documentos del equipo.
- «A V2 substitui o escopo anterior»: la especificación de usuarios con JWT
  sustituye el CRUD del gimnasio inicialmente descrito por la issue.
- «Incluir os campos opcionais e Suspendido»: decisión conservada para una
  eventual continuación del modelo GymFlow, fuera de la implementación V2.

El primer borrador del gimnasio seguía el PR #19. Al revisar el PR #20 ya
integrado se detectó la especificación V2 y se confirmó el cambio con la
usuaria. El borrador quedó guardado en un stash local recuperable; no se
publicó ni se aplicó su migración. Los tests unitarios de ese borrador
habían pasado (52). Ese resultado no valida la implementación V2.

Decisiones para la V2: spec previa en `specs/10-usuarios-crud.md`, arquitectura
existente por capas, hash Argon2 y JWT mediante bibliotecas mantenidas,
permisos de propietario/administrador y credenciales de demostración locales.
La validación de entrada debe omitir valores de contraseñas en los errores.

Errores corregidos durante la implementación: `Path.open` no admite `opener`;
se sustituyó por `open` para crear archivos con permisos 0600. Dos tests
compartían nombre de módulo; se renombró el test unitario para que pytest
pueda recopilar ambas suites. No se eliminaron casos de prueba.

Validación local de la V2: `task lint` aprobado; `task test` con **49 tests
pasando**, incluidos HTTP real con MySQL, permisos, revocación de sesiones,
registro concurrente y repetición de los datos demo. `uv run alembic check`
no detecta diferencias entre modelos y esquema migrado. La suite muestra
un aviso de deprecación de Starlette sobre el transporte httpx de TestClient;
no hay tests omitidos ni fallos.
