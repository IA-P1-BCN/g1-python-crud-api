import { Injectable, inject } from '@angular/core';
import { ApiError } from '../core/http/peticion';
import { ReservasApi } from './api/recursos.api';
import {
  ReservaRechazadaError,
  ReservaService,
  SinPlazasError,
  YaReservadaError,
} from './reserva.service';

/** Reservas reales (/v1/reservas). Los 409 se traducen por el texto del detalle. */
@Injectable()
export class HttpReservaService extends ReservaService {
  private readonly reservas = inject(ReservasApi);

  listarPorClase(idClase: number) {
    return this.reservas.listar({ id_clase: idClase });
  }

  listarDeCliente(idCliente: number) {
    return this.reservas.listar({ id_cliente: idCliente });
  }

  async crear(idCliente: number, idClase: number) {
    try {
      return await this.reservas.crearReserva({ id_cliente: idCliente, id_clase: idClase, asistio: false });
    } catch (error) {
      throw traducirConflicto(error);
    }
  }

  async cancelar(idReserva: number): Promise<void> {
    await this.reservas.eliminar(idReserva);
  }
}

/** Mensajes de conflicto definidos en la API (src/application/use_cases/gym_use_cases.py). */
function traducirConflicto(error: unknown): unknown {
  if (!(error instanceof ApiError) || error.status !== 409) {
    return error;
  }
  if (error.detalle.includes('no tiene plazas')) {
    return new SinPlazasError();
  }
  if (error.detalle.includes('ya tiene una reserva')) {
    return new YaReservadaError();
  }
  return new ReservaRechazadaError(error.detalle);
}
