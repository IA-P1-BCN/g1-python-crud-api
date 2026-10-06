# 🔐 Proyecto: User Management API (FastAPI)

![Banner Proyectos](https://github.com/user-attachments/assets/94ecebe4-ceba-47ae-8f3c-af14bdfe8606)

## 📋 Planteamiento

Formas parte del equipo de backend de una startup que está lanzando varios productos digitales (una plataforma de cursos, una app de reservas y un marketplace). Todos ellos necesitan lo mismo: registrar usuarios, autenticarlos de forma segura y controlar qué puede hacer cada uno.

En lugar de reimplementar esta lógica en cada producto, el CTO ha decidido construir un **servicio centralizado de gestión de usuarios** que el resto de aplicaciones consumirán a través de una API REST. Tu equipo es el responsable de diseñarlo, desarrollarlo y documentarlo.

Como en la mayoría de equipos de desarrollo actuales, **el trabajo se hará con agentes de IA**: el código lo escribe un agente (como [OpenCode](https://opencode.ai)) con modelos gratuitos, y tu equipo hace de *tech lead*: define qué construir, divide el trabajo en tareas, da contexto al agente, revisa lo que genera y decide qué entra en el repositorio. El agente programa, pero la responsabilidad del código es vuestra.

## 🎯 Objetivo

Desarrollar una API REST con **FastAPI** que permita gestionar usuarios (alta, consulta, edición y baja) con **autenticación basada en JWT** y **documentación interactiva con Swagger (OpenAPI)**, de forma que cualquier equipo pueda integrarse con ella sin necesidad de leer el código.

## 🛠️ Requisitos Técnicos

1. API REST desarrollada con **FastAPI**
2. Base de datos SQL (PostgreSQL, MySQL, SQLite) gestionada con un ORM (SQLAlchemy, SQLModel, etc.)
3. Validación de datos con **Pydantic**
4. Contraseñas almacenadas con hash (bcrypt, argon2…), **nunca en texto plano**
5. Autenticación con **JWT** (OAuth2 Password Flow)
6. Documentación automática con **Swagger UI** (`/docs`) y ReDoc (`/redoc`)
7. Tests unitarios y de integración (pytest + `TestClient`)
8. Control de versiones con Git y GitHub
9. Gestión del proyecto con metodologías ágiles (SCRUM)
10. Desarrollo asistido por **agentes de IA** con modelos gratuitos (ver sección siguiente)

## 🤖 Desarrollo Agéntico con IA

El proyecto debe desarrollarse usando un agente de código en la terminal, trabajando como se hace hoy en la industria.

**Herramientas**

- Agente: **[OpenCode](https://opencode.ai)** (recomendado). Se pueden usar alternativas abiertas o gratuitas (Aider, Cline, Kilo Code…), pero hay que justificar la elección.
- Modelos **gratuitos**, por ejemplo: los modelos gratuitos de OpenCode Zen, modelos `:free` de OpenRouter, la capa gratuita de Groq o Gemini, o modelos locales con **Ollama**.
- Si tienen IAs de pago pueden utilizarlas, solo que tenerlo en cuenta para no pisar el trabajo del equipo, delimitar muy bien el alcance que tendrán.

**Forma de trabajo**

1. **Contexto antes que código:** crear un `AGENTS.md` en la raíz con el stack, la estructura de carpetas, las convenciones, los comandos para lanzar los tests y lo que el agente **no** debe hacer (por ejemplo: no subir secretos, no saltarse los tests).
2. **SDD & Ontologías:** antes de pedirle código al agente, cada funcionalidad se define con *Spec-Driven Development* en una spec (`specs/`) con requisitos y criterios de aceptación, apoyada en una ontología del dominio: entidades (`User`, `Role`, `Token`…), sus atributos, relaciones y reglas. Así el agente y el equipo comparten el mismo vocabulario y no inventan conceptos.
3. **Spec antes de programar:** cada historia de usuario se describe en una especificación breve (`specs/`) con los criterios de aceptación antes de pedírsela al agente.
4. **Tareas pequeñas:** una tarea del Kanban equivale a una sesión del agente, una rama y una Pull Request.
5. **Revisión humana obligatoria:** todo el código generado se lee, se prueba y se revisa en la PR antes de mergear. Hay que prestar especial atención a la seguridad: hash de contraseñas, validación del JWT, secretos y permisos.
6. **Los tests son el contrato:** el agente debe dejar los tests pasando. Si un test falla, se arregla el código, no se borra el test.
7. **Trazabilidad:** registrar los prompts más relevantes y las decisiones que se tomaron (qué se aceptó, qué se rechazó y por qué).

## 📦 Entregables

1. Diagrama ER de la base de datos
2. Repositorio en GitHub con código fuente y README con instrucciones de instalación y uso
3. Documentación de la API accesible en Swagger, con ejemplos de peticiones y respuestas
4. Colección de Postman/Bruno o similar con los endpoints
5. Suite de tests completa y pasando
6. Documento de retrospectiva del proyecto
7. Tablero Kanban (Trello, Jira, GitHub Projects, etc.) con historias de usuario
8. `AGENTS.md` y carpeta `specs/` con las especificaciones de cada funcionalidad
9. **Bitácora de IA** (`docs/ai-log.md`): herramienta y modelos usados, prompts clave, errores o alucinaciones del agente y cómo se corrigieron
10. Historial de PRs con revisiones visibles del código generado

## 🏆 Niveles de Entrega

### 🟢 Nivel Esencial

- Modelo `User` (id, nombre, email único, contraseña hasheada, fecha de creación, activo)
- CRUD completo de usuarios (`POST`, `GET`, `PUT/PATCH`, `DELETE`)
- Registro (`/auth/register`) y login (`/auth/login`) que devuelve un JWT
- Endpoints protegidos que requieren token válido (ej. `/users/me`)
- Schemas Pydantic separados para entrada y salida (la contraseña nunca se devuelve)
- Swagger funcionando con el botón **Authorize**
- Tests unitarios para cada endpoint
- Variables de entorno para datos sensibles (`SECRET_KEY`, URL de la BBDD…)
- Logging básico y manejo de excepciones con códigos HTTP apropiados (400, 401, 403, 404, 409…)
- Gestión de proyecto con Kanban
- `AGENTS.md` funcional y bitácora de IA con al menos los prompts de cada funcionalidad principal

### 🟡 Nivel Medio

- Roles de usuario (`admin`, `user`) y permisos: solo un admin puede listar o borrar a otros usuarios
- Cambio de contraseña y actualización del propio perfil
- Filtrado, búsqueda y paginación en `GET /users`
- Expiración del token configurable
- Migraciones de base de datos con **Alembic**
- Documentación Swagger enriquecida (tags, descripciones, ejemplos, respuestas de error)
- Arquitectura por capas (routers, services, repositories, schemas)
- Flujo spec → agente → PR → revisión aplicado a todas las historias de usuario
- Comparativa de al menos 2 modelos gratuitos en una misma tarea (calidad, velocidad, errores)

### 🟠 Nivel Avanzado

- **Refresh tokens** y logout (lista de tokens revocados)
- Verificación de email y recuperación de contraseña mediante token temporal
- Rate limiting en el endpoint de login para mitigar ataques de fuerza bruta
- Soft delete y auditoría (quién creó/modificó cada usuario y cuándo)
- Cobertura de tests ≥ 80 %
- Pipeline de CI con GitHub Actions (lint + tests en cada PR)
- Comandos, skills o subagentes personalizados en OpenCode para tareas repetitivas (generar tests, revisar seguridad…)

### 🔴 Nivel Experto

- Contenedorización con **Docker** y `docker-compose` (API + base de datos)
- Despliegue en la nube (Render, Railway, AWS, Google Cloud, etc.)
- Login social con OAuth2 (Google, GitHub…)
- Autenticación en dos pasos (2FA / TOTP)
- Interfaz de usuario básica (web o móvil) que consuma la API
- Revisión automática de PRs con un agente de IA en GitHub Actions usando un modelo gratuito
- Servidor MCP propio o integración de herramientas MCP en el flujo del agente
