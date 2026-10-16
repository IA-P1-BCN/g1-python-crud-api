import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { ApiError, ejecutar, RUTA_API } from '../http/peticion';
import { CuentasApi } from '../../services/api/recursos.api';
import { AuthService, DatosRegistro, UsuarioAutenticado } from './auth.service';
import { EmailDuplicadoError, InvalidCredentialsError } from './auth.errors';
import { borrarToken, guardarToken } from './token.storage';

interface RespuestaToken {
  readonly access_token: string;
  readonly token_type: 'bearer';
}

/** Autenticación contra /v1/auth (login con OAuth2 password flow, registro público). */
@Injectable()
export class HttpAuthService extends AuthService {
  private readonly http = inject(HttpClient);
  private readonly cuentas = inject(CuentasApi);

  async login(email: string, password: string): Promise<UsuarioAutenticado> {
    // OAuth2 password flow: el formulario usa `username` aunque sea el email.
    const formulario = new HttpParams().set('username', email).set('password', password);
    let token: RespuestaToken;
    try {
      token = await ejecutar(this.http.post<RespuestaToken>(`${RUTA_API}/auth/login`, formulario));
    } catch (error) {
      // El servidor responde el mismo 401 para email desconocido, contraseña errónea o cuenta inactiva.
      if (error instanceof ApiError && error.status === 401) {
        throw new InvalidCredentialsError();
      }
      throw error;
    }

    // El token se guarda antes de pedir el perfil: el interceptor lo adjunta a esa petición.
    guardarToken(token.access_token);
    try {
      const cuenta = await this.cuentas.yo();
      return {
        id: cuenta.id,
        nombre: cuenta.nombre,
        email: cuenta.email,
        rol: cuenta.rol,
        id_cliente: cuenta.id_cliente,
      };
    } catch (error) {
      borrarToken();
      throw error;
    }
  }

  async register(datos: DatosRegistro): Promise<void> {
    try {
      await ejecutar(this.http.post(`${RUTA_API}/auth/register`, datos));
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        throw new EmailDuplicadoError();
      }
      throw error;
    }
  }
}
