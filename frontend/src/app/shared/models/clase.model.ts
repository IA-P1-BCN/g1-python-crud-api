/** Espejo de ClaseResponse de la API (/v1/clases). horario: UTC sin zona. */
export interface Clase {
  readonly id_clase: number;
  readonly nombre_clase: string;
  readonly horario: string;
  readonly capacidad_max: number;
  readonly id_entrenador: number;
}

/** Clase con las plazas calculadas (capacidad menos reservas). */
export interface ClaseConCupo {
  readonly clase: Clase;
  readonly entrenador: string;
  readonly plazasLibres: number;
  readonly reservadaPorMi: boolean;
}
