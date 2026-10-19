/** Espejo de EntrenadorResponse de la API (/v1/entrenadores). */
export interface Entrenador {
  readonly id_entrenador: number;
  readonly nombre: string;
  readonly especialidad: string | null;
  readonly telefono: string | null;
  /** Cuenta staff vinculada, resuelta de users (null si no tiene). */
  readonly id_user: number | null;
  readonly email: string | null;
}
