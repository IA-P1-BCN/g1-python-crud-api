import { Injectable, inject } from '@angular/core';
import { ClaseService, FiltrosClase } from './clase.service';
import { ClasesApi, EntrenadoresApi } from './api/recursos.api';

/** Clases y entrenadores reales (/v1/clases y /v1/entrenadores). */
@Injectable()
export class HttpClaseService extends ClaseService {
  private readonly clases = inject(ClasesApi);
  private readonly entrenadores = inject(EntrenadoresApi);

  listar(filtros: FiltrosClase = {}) {
    return this.clases.listar(filtros);
  }

  obtener(idClase: number) {
    return this.clases.obtener(idClase);
  }

  listarEntrenadores() {
    return this.entrenadores.listar();
  }

  cupo(idClase: number) {
    return this.clases.cupo(idClase);
  }
}
