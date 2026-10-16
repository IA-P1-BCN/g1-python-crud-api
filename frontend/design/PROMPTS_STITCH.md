# Prompts de Stitch · GymFlow

Proyecto de Stitch: **GymFlow - Portal del socio** (ID `4138124516984207220`).
Sistema de diseño creado: `assets/14686005327976071721` (GymFlow Portal del socio).

Idioma: español. Incluir versión móvil en cada pantalla.

## Datos mock compartidos

- Socia: Ana García, ana.garcia@gym.test, estado Activo, inscrita el 01/09/2026, pago con tarjeta, teléfono 600 123 456.
- Clases:
  - Yoga: lun 20/10, 09:00, Laura Martín, capacidad 12, 9 reservas (3 libres).
  - Spinning: mar 21/10, 19:30, Carlos Ruiz, capacidad 15, 14 reservas (1 libre).
  - Pilates: jue 23/10, 18:00, Laura Martín, capacidad 10, 10 reservas (completa).
  - Zumba: vie 24/10, 10:00, Carlos Ruiz, capacidad 20, 0 reservas (20 libres).
- Entrenadores: Laura Martín, Carlos Ruiz.

Los cupos se calculan como capacidad menos reservas.

## 0. Sistema de diseño

```
Diseña un sistema visual para "GymFlow", una web de gimnasio para socios.
Idioma de la interfaz: español.
Estilo: moderno, limpio, energético, con mucho espacio en blanco.
Paleta: azul o verde intenso como primario, naranja para avisos y acciones
secundarias, fondo claro, texto oscuro con contraste WCAG AA.
Tipografía: sans-serif legible (tipo Inter), escalas de 14, 16, 20 y 28 px.
Componentes: botón primario y secundario, campo de texto con etiqueta y mensaje
de error, tarjeta, badge de estado (Activo, Inactivo, Suspendido), barra de
progreso para cupos, cabecera con logo y menú de usuario, toast de éxito y error,
diálogo de confirmación.
Diseño responsive: versión móvil (navegación inferior) y escritorio (cabecera).
```

## 1. Registro (#83)

```
Diseña la pantalla de registro de GymFlow en español, siguiendo el sistema de
diseño. Layout centrado en tarjeta, logo arriba y enlace "¿Ya tienes cuenta?
Inicia sesión" abajo.
Campos:
- Nombre completo (obligatorio, máximo 100 caracteres)
- Correo electrónico (obligatorio, formato válido)
- Contraseña (obligatoria, mínimo 12 caracteres, con botón mostrar/ocultar y
  pista visible "Mínimo 12 caracteres")
- Casilla "Quiero crear también mi ficha de socio" con ayuda "Tu ficha quedará
  inactiva hasta que el gimnasio la active"
Botón principal "Crear cuenta". Estados:
- Normal y con error de validación en un campo concreto
- Cargando (botón deshabilitado con indicador)
- Error "Ya existe una cuenta con este correo"
- Error de conexión "No se pudo conectar con el servidor. Inténtalo de nuevo."
- Éxito: "Cuenta creada. Ya puedes iniciar sesión" con botón "Ir al login"
Incluye la versión móvil.
```

## 2. Login (#83, referencia)

```
Diseña la pantalla de inicio de sesión de GymFlow en español, con el mismo estilo
que el registro. Campos: correo electrónico y contraseña (con mostrar/ocultar).
Botón "Iniciar sesión". Enlace "Crear cuenta" debajo.
Estados: normal, cargando, error "Correo o contraseña incorrectos" (mismo mensaje
para cualquier fallo de credenciales), error de conexión y versión móvil.
```

## 3. Inicio del socio (STORY #42)

```
Diseña la pantalla de inicio de un socio de GymFlow en español. Cabecera con logo,
enlaces "Clases", "Mis reservas", "Mi perfil" y botón "Cerrar sesión".
Saludo "Hola, Ana". Tres tarjetas: próxima clase ("Yoga, lun 20/10, 09:00"),
estado de membresía (badge verde "Activo") y acceso rápido "Ver clases".
Versión móvil con barra de navegación inferior con los mismos tres enlaces.
```

## 4. Clases disponibles con cupos (#31)

```
Diseña la pantalla "Clases disponibles" de GymFlow en español. Título, buscador
por nombre y lista de tarjetas con: nombre, fecha y hora, entrenador, barra de
cupos con texto "9 de 12 plazas libres" y botón "Reservar".
Datos de ejemplo: Yoga (lun 20/10, 09:00, Laura Martín, 3 libres de 12),
Spinning (mar 21/10, 19:30, Carlos Ruiz, 1 libre de 15), Pilates (jue 23/10,
18:00, Laura Martín, completa), Zumba (vie 24/10, 10:00, Carlos Ruiz, 20 libres de 20).
Estados de la tarjeta:
- Disponible (botón activo)
- Pocas plazas (aviso naranja, menos de 3 libres)
- Completa (sin botón, etiqueta "Completa")
- Ya reservada (botón sustituido por "Reservada")
Estado vacío "No hay clases disponibles" y estado de carga con esqueleto.
Versión móvil en lista y escritorio en cuadrícula de dos o tres columnas.
```

## 5. Mis reservas: reservar y cancelar (#31)

```
Diseña la pantalla "Mis reservas" de GymFlow en español. Pestañas "Próximas" y
"Pasadas". Cada reserva muestra clase, fecha, hora, entrenador y, en las próximas,
botón "Cancelar reserva".
Datos de ejemplo: Yoga (lun 20/10, 09:00) en próximas; Pilates (sáb 10/10, 18:00)
en pasadas.
Diálogo de confirmación: "¿Cancelar la reserva de Yoga del 20/10? La plaza
quedará libre." con botones "Volver" y "Sí, cancelar".
Estados: lista con datos, lista vacía ("Aún no tienes reservas" con enlace a
clases), cargando, toast de error al cancelar, toast de reserva cancelada, y
mensaje "La clase ya no tiene plazas" al intentar reservar una completa.
Versión móvil y escritorio.
```

## 6. Mi perfil y membresía (STORY #42)

```
Diseña la pantalla "Mi perfil" de GymFlow en español. Dos secciones:
- Datos personales: nombre "Ana García", correo ana.garcia@gym.test, teléfono
  "600 123 456", fecha de inscripción "01/09/2026" y botón "Editar".
- Mi membresía: badge "Activo" en verde, método de pago "Tarjeta".
Variante sin ficha de socio: "Aún no tienes ficha de socio. Contacta con el
gimnasio" en lugar de la membresía.
Incluye la pantalla de editar datos con botones "Guardar" y "Cancelar".
Versión móvil y escritorio.
```

## Notas

- Panel de administración (#84): fuera de alcance hasta desbloquear #65.
- Stitch genera HTML/CSS genérico. La conversión a componentes Angular se hace a mano, pantalla a pantalla.
