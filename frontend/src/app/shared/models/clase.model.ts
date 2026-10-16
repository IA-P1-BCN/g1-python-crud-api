/** Espejo de ClaseResponse de la API (/v1/clases). horario: UTC sin zona. */
export interface Clase {
  readonly id_clase: number;
  readonly nombre_clase: string;
  readonly horario: string;
  readonly capacidad_max: number;
  readonly id_entrenador: number;
}

/** Cupo agregado: no contiene datos de clientes ni reservas individuales. */
export interface CupoClase {
  readonly id_clase: number;
  readonly capacidad_max: number;
  readonly reservas: number;
  readonly plazas_disponibles: number;
}

/** Clase con las plazas calculadas (capacidad menos reservas). */
export interface ClaseConCupo {
  readonly clase: Clase;
  readonly entrenador: string;
  readonly plazasLibres: number;
  readonly reservadaPorMi: boolean;
}
