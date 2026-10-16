import { HttpErrorResponse, HttpParams } from '@angular/common/http';
import { firstValueFrom, Observable } from 'rxjs';
import { NetworkError } from '../auth/auth.errors';

/** Prefijo de la API; el proxy de `ng serve` lo reenvía a 127.0.0.1:8000. */
export const RUTA_API = '/v1';

/** Límite máximo de la API para listados (ListQuery.limit <= 100). */
export const TAMANO_PAGINA = 100;

/** Error de la API con su código HTTP y el `detail` que devuelve el servidor. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly detalle: string,
  ) {
    super(detalle);
    this.name = 'ApiError';
  }
}

/** Traduce un fallo de HttpClient a un error de la interfaz (red o ApiError). */
export function traducirErrorHttp(error: unknown): Error {
  if (error instanceof HttpErrorResponse) {
    if (error.status === 0) {
      return new NetworkError();
    }
    const detail = (error.error as { detail?: unknown } | null)?.detail;
    const texto = typeof detail === 'string' ? detail : 'Datos no válidos o error del servidor';
    return new ApiError(error.status, texto);
  }
  return error instanceof Error ? error : new Error('Error desconocido');
}

/** Ejecuta una petición HttpClient como promesa con los errores ya traducidos. */
export function ejecutar<T>(peticion: Observable<T>): Promise<T> {
  return firstValueFrom(peticion).catch((error: unknown) => {
    throw traducirErrorHttp(error);
  });
}

/** Texto visible para el usuario a partir de un error ya traducido por `ejecutar`. */
export function textoDeError(error: unknown, porDefecto = 'La operación no se pudo completar.'): string {
  if (error instanceof NetworkError) {
    return 'No se pudo conectar con el servidor. Inténtalo de nuevo.';
  }
  if (error instanceof ApiError) {
    return error.detalle;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return porDefecto;
}

/** Convierte filtros a query params, omitiendo los valores null o undefined. */
export function aParams(valores: Record<string, unknown>): HttpParams {
  let params = new HttpParams();
  for (const [clave, valor] of Object.entries(valores)) {
    if (valor !== null && valor !== undefined) {
      params = params.set(clave, String(valor));
    }
  }
  return params;
}

/** Recorre todas las páginas de un listado paginado (offset/limit). */
export async function listarTodas<T>(
  pedirPagina: (offset: number, limit: number) => Promise<T[]>,
): Promise<T[]> {
  const todas: T[] = [];
  for (let offset = 0; ; offset += TAMANO_PAGINA) {
    const pagina = await pedirPagina(offset, TAMANO_PAGINA);
    todas.push(...pagina);
    if (pagina.length < TAMANO_PAGINA) {
      return todas;
    }
  }
}
