import { Injectable } from '@angular/core';
import { Clase, CupoClase } from '../shared/models/clase.model';
import { Entrenador } from '../shared/models/entrenador.model';

/** Filtros de listado aceptados por la API (q, rangos de horario, id_entrenador…). */
export type FiltrosClase = Record<string, string | number | boolean | null | undefined>;

/** Contrato del catálogo y su disponibilidad. */
@Injectable()
export abstract class ClaseService {
  abstract listar(filtros?: FiltrosClase): Promise<Clase[]>;
  abstract obtener(idClase: number): Promise<Clase>;
  abstract listarEntrenadores(): Promise<Entrenador[]>;
  abstract cupo(idClase: number): Promise<CupoClase>;
}
