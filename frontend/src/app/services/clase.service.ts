import { Injectable } from '@angular/core';
import { Clase } from '../shared/models/clase.model';
import { Entrenador } from '../shared/models/entrenador.model';

/** Contrato de clases. Implementación mock hasta conectar /v1/clases. */
@Injectable()
export abstract class ClaseService {
  abstract listar(): Promise<Clase[]>;
  abstract listarEntrenadores(): Promise<Entrenador[]>;
}
