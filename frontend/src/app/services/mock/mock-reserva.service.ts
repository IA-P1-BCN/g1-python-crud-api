import { Injectable } from '@angular/core';
import { ReservaService, SinPlazasError, YaReservadaError } from '../reserva.service';
import { Reserva } from '../../shared/models/reserva.model';
import { CLASES_MOCK, reservasIniciales } from './datos-mock';

/** Estado en memoria: reservar o cancelar cambia los cupos durante la sesión. */
@Injectable()
export class MockReservaService extends ReservaService {
  private reservas: Reserva[] = reservasIniciales();
  private siguienteId = this.reservas.length + 1;

  async listarPorClase(idClase: number): Promise<Reserva[]> {
    return this.reservas.filter((r) => r.id_clase === idClase).map((r) => ({ ...r }));
  }

  async listarDeCliente(idCliente: number): Promise<Reserva[]> {
    return this.reservas.filter((r) => r.id_cliente === idCliente).map((r) => ({ ...r }));
  }

  async crear(idCliente: number, idClase: number): Promise<Reserva> {
    const clase = CLASES_MOCK.find((c) => c.id_clase === idClase);
    if (!clase) {
      throw new Error('Clase no encontrada');
    }
    const ocupadas = this.reservas.filter((r) => r.id_clase === idClase).length;
    if (ocupadas >= clase.capacidad_max) {
      throw new SinPlazasError();
    }
    if (this.reservas.some((r) => r.id_cliente === idCliente && r.id_clase === idClase)) {
      throw new YaReservadaError();
    }
    const nueva: Reserva = {
      id_reserva: this.siguienteId++,
      id_cliente: idCliente,
      id_clase: idClase,
      asistio: false,
      fecha_reserva: new Date().toISOString().slice(0, 19),
      id_user: null,
      nombre: null,
      email: null,
    };
    this.reservas = [...this.reservas, nueva];
    return { ...nueva };
  }

  async cancelar(idReserva: number): Promise<void> {
    this.reservas = this.reservas.filter((r) => r.id_reserva !== idReserva);
  }
}
