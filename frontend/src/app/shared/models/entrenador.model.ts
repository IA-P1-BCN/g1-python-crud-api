/** Espejo de EntrenadorResponse de la API (/v1/entrenadores). */
export interface Entrenador {
  readonly id_entrenador: number;
  readonly nombre: string;
  readonly especialidad: string | null;
  readonly telefono: string | null;
}
