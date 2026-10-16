/** Espejo de CuentaResponse de la API (/v1/users y /v1/users/me). Sin credenciales. */
export interface Cuenta {
  readonly id: number;
  readonly nombre: string;
  readonly email: string;
  readonly activo: boolean;
  readonly rol: 'admin' | 'staff' | 'cliente';
  readonly fecha_creacion: string;
  readonly id_cliente: number | null;
}

/** Edición completa de una Cuenta (CuentaPut): nombre y email obligatorios. */
export interface CuentaPut {
  readonly nombre: string;
  readonly email: string;
  readonly password?: string;
}
