import { Injectable } from '@angular/core';
import { ClaseService } from '../clase.service';
import { Clase } from '../../shared/models/clase.model';
import { Entrenador } from '../../shared/models/entrenador.model';
import { CLASES_MOCK, ENTRENADORES_MOCK } from './datos-mock';

@Injectable()
export class MockClaseService extends ClaseService {
  async listar(): Promise<Clase[]> {
    return structuredClone([...CLASES_MOCK]);
  }

  async listarEntrenadores(): Promise<Entrenador[]> {
    return structuredClone([...ENTRENADORES_MOCK]);
  }
}
