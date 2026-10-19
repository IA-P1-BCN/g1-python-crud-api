import { Clase } from '../../shared/models/clase.model';
import { Entrenador } from '../../shared/models/entrenador.model';
import { Reserva } from '../../shared/models/reserva.model';

/** Datos ficticios solo para desarrollo. El socio mock es Ana García (id_cliente 1). */
export const ID_ANA = 1;

export const ENTRENADORES_MOCK: readonly Entrenador[] = [
  { id_entrenador: 1, nombre: 'Laura Martín', especialidad: 'Yoga y Pilates', telefono: null },
  { id_entrenador: 2, nombre: 'Carlos Ruiz', especialidad: 'Spinning y Zumba', telefono: null },
];

export const CLASES_MOCK: readonly Clase[] = [
  { id_clase: 1, nombre_clase: 'Yoga', horario: '2026-10-20T09:00:00', capacidad_max: 12, id_entrenador: 1 },
  { id_clase: 2, nombre_clase: 'Spinning', horario: '2026-10-21T19:30:00', capacidad_max: 15, id_entrenador: 2 },
  { id_clase: 3, nombre_clase: 'Pilates', horario: '2026-10-23T18:00:00', capacidad_max: 10, id_entrenador: 1 },
  { id_clase: 4, nombre_clase: 'Zumba', horario: '2026-10-24T10:00:00', capacidad_max: 20, id_entrenador: 2 },
  { id_clase: 5, nombre_clase: 'Pilates', horario: '2026-10-10T18:00:00', capacidad_max: 10, id_entrenador: 1 },
];

/** Reservas iniciales: Yoga 9/12, Spinning 14/15, Pilates 10/10, Zumba 0/20. */
function reservasDeOtros(idClase: number, cantidad: number, inicio: number): Reserva[] {
  return Array.from({ length: cantidad }, (_, i) => ({
    id_reserva: 0,
    id_cliente: inicio + i,
    id_clase: idClase,
    asistio: false,
    fecha_reserva: '2026-10-01T10:00:00',
    id_user: null,
    nombre: null,
    email: null,
  }));
}

export function reservasIniciales(): Reserva[] {
  const todas: Reserva[] = [
    ...reservasDeOtros(1, 8, 201),
    ...reservasDeOtros(2, 14, 301),
    ...reservasDeOtros(3, 10, 401),
    ...reservasDeOtros(5, 5, 501),
    // Ana: próxima en Yoga y pasada en Pilates del 10/10.
    { id_reserva: 0, id_cliente: ID_ANA, id_clase: 1, asistio: false, fecha_reserva: '2026-10-01T10:00:00', id_user: null, nombre: null, email: null },
    { id_reserva: 0, id_cliente: ID_ANA, id_clase: 5, asistio: true, fecha_reserva: '2026-10-01T10:00:00', id_user: null, nombre: null, email: null },
  ];
  return todas.map((r, i) => ({ ...r, id_reserva: i + 1 }));
}
