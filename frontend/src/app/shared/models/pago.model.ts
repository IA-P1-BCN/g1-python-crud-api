/** Espejo de PagoResponse de la API (/v1/pagos). monto llega como texto decimal. */
export interface Pago {
  readonly id_pago: number;
  readonly id_cliente: number;
  readonly monto: string;
  readonly fecha_pago: string;
  readonly metodo_pago: 'Tarjeta' | 'Transferencia' | 'Efectivo' | null;
}

/** Cuerpo de alta/edición de un pago (PagoInput). */
export interface PagoEntrada {
  readonly id_cliente: number;
  readonly monto: string;
  readonly fecha_pago: string;
  readonly metodo_pago: Pago['metodo_pago'];
}
