import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { borrarToken, leerToken } from '../auth/token.storage';
import { SessionService } from '../auth/session.service';
import { RUTA_API } from './peticion';

/**
 * Añade `Authorization: Bearer` a las peticiones de /v1. Si el servidor responde 401
 * con un token guardado (expirado o cuenta borrada), cierra la sesión local.
 * El login queda fuera: su 401 significa credenciales incorrectas.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const sesion = inject(SessionService);
  const token = leerToken();
  const esApi = req.url.startsWith(RUTA_API);
  const peticion =
    token && esApi ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req;

  return next(peticion).pipe(
    catchError((error: unknown) => {
      const esLogin = req.url.startsWith(`${RUTA_API}/auth/login`);
      if (error instanceof HttpErrorResponse && error.status === 401 && token && !esLogin) {
        borrarToken();
        sesion.cerrar();
      }
      return throwError(() => error);
    }),
  );
};
