import { Injectable } from '@angular/core';
import { Clase, CupoClase } from '../shared/models/clase.model';
import { Entrenador } from '../shared/models/entrenador.model';

/** Contrato del catálogo y su disponibilidad. */
@Injectable()
export abstract class ClaseService {
  abstract listar(): Promise<Clase[]>;
  abstract listarEntrenadores(): Promise<Entrenador[]>;
  abstract cupo(idClase: number): Promise<CupoClase>;
}
