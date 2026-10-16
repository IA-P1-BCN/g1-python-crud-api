import { Injectable } from '@angular/core';
import { Reserva } from '../shared/models/reserva.model';

/** Contrato de reservas. Implementación mock hasta conectar /v1/reservas. */
@Injectable()
export abstract class ReservaService {
  /** Reservas de una clase (usa el filtro id_clase de la API). */
  abstract listarPorClase(idClase: number): Promise<Reserva[]>;
  /** Reservas de un socio (filtro id_cliente). */
  abstract listarDeCliente(idCliente: number): Promise<Reserva[]>;
  /**
   * @throws {SinPlazasError} si la clase no tiene plazas libres.
   * @throws {YaReservadaError} si el socio ya tiene reserva en esa clase.
   */
  abstract crear(idCliente: number, idClase: number): Promise<Reserva>;
  abstract cancelar(idReserva: number): Promise<void>;
}

export class SinPlazasError extends Error {
  constructor() {
    super('La clase ya no tiene plazas');
  }
}

export class YaReservadaError extends Error {
  constructor() {
    super('Ya tienes una reserva en esta clase');
  }
}

/** Reserva rechazada por otra regla de negocio (cliente inactivo, sin pago, etc.). */
export class ReservaRechazadaError extends Error {
  constructor(mensaje: string) {
    super(mensaje);
    this.name = 'ReservaRechazadaError';
  }
}
