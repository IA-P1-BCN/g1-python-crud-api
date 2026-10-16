import { Injectable, inject } from '@angular/core';
import { ClaseService, FiltrosClase } from '../clase.service';
import { ReservaService } from '../reserva.service';
import { Clase, CupoClase } from '../../shared/models/clase.model';
import { Entrenador } from '../../shared/models/entrenador.model';
import { CLASES_MOCK, ENTRENADORES_MOCK } from './datos-mock';

/** Mock de catálogo para specs: aplica los filtros básicos sobre los datos ficticios. */
@Injectable()
export class MockClaseService extends ClaseService {
  private readonly reservas = inject(ReservaService);

  async listar(filtros: FiltrosClase = {}): Promise<Clase[]> {
    let lista = structuredClone([...CLASES_MOCK]);
    const texto = String(filtros['q'] ?? filtros['nombre_clase'] ?? '').trim().toLowerCase();
    if (texto) {
      lista = lista.filter((c) => c.nombre_clase.toLowerCase().includes(texto));
    }
    const idEntrenador = filtros['id_entrenador'];
    if (idEntrenador !== null && idEntrenador !== undefined) {
      lista = lista.filter((c) => c.id_entrenador === Number(idEntrenador));
    }
    return lista;
  }

  async obtener(idClase: number): Promise<Clase> {
    const clase = CLASES_MOCK.find((c) => c.id_clase === idClase);
    if (!clase) throw new Error('Clase no encontrada');
    return structuredClone(clase);
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
