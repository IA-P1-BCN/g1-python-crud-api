/** Espejo de ClienteResponse de la API (/v1/clientes). */
export type EstadoMembresia = 'Activo' | 'Inactivo' | 'Suspendido';

export interface Cliente {
  readonly id_cliente: number;
  readonly nombre: string;
  readonly email: string | null;
  readonly estado_membresia: EstadoMembresia;
  readonly fecha_inscripcion: string | null;
}
