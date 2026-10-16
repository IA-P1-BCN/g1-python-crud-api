/** Espejo de ReservaResponse de la API (/v1/reservas). */
export interface Reserva {
  readonly id_reserva: number;
  readonly id_cliente: number;
  readonly id_clase: number;
  readonly asistio: boolean;
  readonly fecha_reserva: string;
}
