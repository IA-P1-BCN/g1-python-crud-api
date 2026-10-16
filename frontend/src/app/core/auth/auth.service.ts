import { Injectable } from '@angular/core';
import { EmailDuplicadoError, InvalidCredentialsError, NetworkError } from './auth.errors';

export type RolUsuario = 'admin' | 'staff' | 'cliente';

export interface UsuarioAutenticado {
  readonly id: number;
  readonly nombre: string;
  readonly email: string;
  readonly rol: RolUsuario;
  /** Ficha de socio vinculada; null si la cuenta no tiene ficha. */
  readonly id_cliente: number | null;
}

/** Datos del registro público, con los mismos nombres que CuentaRegister de la API. */
export interface DatosRegistro {
  readonly nombre: string;
  readonly email: string;
  readonly password: string;
  readonly crear_cliente: boolean;
}

/**
 * Contrato de autenticación de la interfaz. Los componentes dependen solo de esta
 * clase abstracta; la implementación se elige en app.config.ts.
 */
@Injectable()
export abstract class AuthService {
  /**
   * Inicia sesión con correo y contraseña.
   * @throws {InvalidCredentialsError} si las credenciales no son válidas.
   * @throws {NetworkError} si no se puede contactar con el servidor.
   */
  abstract login(email: string, password: string): Promise<UsuarioAutenticado>;

  /**
   * Crea una cuenta de rol cliente.
   * @throws {EmailDuplicadoError} si el correo ya existe.
   * @throws {NetworkError} si no se puede contactar con el servidor.
   */
  abstract register(datos: DatosRegistro): Promise<void>;
}

export { EmailDuplicadoError, InvalidCredentialsError, NetworkError };
