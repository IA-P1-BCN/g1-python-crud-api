import { Injectable, inject } from '@angular/core';
import { ClaseService } from './clase.service';
import { ClasesApi, EntrenadoresApi } from './api/recursos.api';

/** Clases y entrenadores reales (/v1/clases y /v1/entrenadores). */
@Injectable()
export class HttpClaseService extends ClaseService {
  private readonly clases = inject(ClasesApi);
  private readonly entrenadores = inject(EntrenadoresApi);

  listar() {
    return this.clases.listar();
  }

  listarEntrenadores() {
    return this.entrenadores.listar();
  }

  cupo(idClase: number) {
    return this.clases.cupo(idClase);
  }
}
