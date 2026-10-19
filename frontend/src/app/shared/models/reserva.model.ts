/** Espejo de ReservaResponse de la API (/v1/reservas). */
export interface Reserva {
  readonly id_reserva: number;
  readonly id_cliente: number;
  readonly id_clase: number;
  readonly asistio: boolean;
  readonly fecha_reserva: string;
  /** Identidad de quien reserva, resuelta de la Cuenta vinculada. */
  readonly id_user: number | null;
  readonly nombre: string | null;
  readonly email: string | null;
}
