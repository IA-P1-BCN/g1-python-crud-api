import { Injectable, inject } from '@angular/core';
import { ClaseService } from '../clase.service';
import { ReservaService } from '../reserva.service';
import { Clase, CupoClase } from '../../shared/models/clase.model';
import { Entrenador } from '../../shared/models/entrenador.model';
import { CLASES_MOCK, ENTRENADORES_MOCK } from './datos-mock';

@Injectable()
export class MockClaseService extends ClaseService {
  private readonly reservas = inject(ReservaService);

  async listar(): Promise<Clase[]> {
    return structuredClone([...CLASES_MOCK]);
  }

  async listarEntrenadores(): Promise<Entrenador[]> {
    return structuredClone([...ENTRENADORES_MOCK]);
  }

  async cupo(idClase: number): Promise<CupoClase> {
    const clase = CLASES_MOCK.find((c) => c.id_clase === idClase);
    if (!clase) throw new Error('Clase no encontrada');
    const reservas = (await this.reservas.listarPorClase(idClase)).length;
    return {
      id_clase: idClase,
      capacidad_max: clase.capacidad_max,
      reservas,
      plazas_disponibles: Math.max(0, clase.capacidad_max - reservas),
    };
  }
}
