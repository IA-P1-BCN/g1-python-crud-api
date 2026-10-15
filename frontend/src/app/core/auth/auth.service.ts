import { Injectable } from '@angular/core';
import { InvalidCredentialsError, NetworkError } from './auth.errors';

export type RolUsuario = 'admin' | 'staff' | 'cliente';

export interface UsuarioAutenticado {
  readonly id: string;
  readonly email: string;
  readonly rol: RolUsuario;
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
}

export { InvalidCredentialsError, NetworkError };
