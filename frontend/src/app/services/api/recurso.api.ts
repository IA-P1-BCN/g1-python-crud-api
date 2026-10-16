import { HttpClient } from '@angular/common/http';
import { inject } from '@angular/core';
import { aParams, ejecutar, listarTodas, RUTA_API, TAMANO_PAGINA } from '../../core/http/peticion';

/** Filtros de un listado: se envían como query params junto a offset/limit. */
export type FiltrosApi = Record<string, string | number | boolean | null | undefined>;

/**
 * Operaciones CRUD genéricas sobre un recurso de la API. Cada subclase fija la
 * ruta. Los errores llegan ya traducidos (ApiError o NetworkError).
 */
export abstract class RecursoApi<T, Entrada> {
  protected abstract readonly ruta: string;
  protected readonly http = inject(HttpClient);

  /** Una página del listado (offset/limit). */
  pagina(filtros: FiltrosApi = {}, offset = 0, limit = TAMANO_PAGINA): Promise<T[]> {
    return ejecutar(
      this.http.get<T[]>(this.url(), { params: aParams({ ...filtros, offset, limit }) }),
    );
  }

  /** Todas las páginas del listado, en orden por ID. */
  listar(filtros: FiltrosApi = {}): Promise<T[]> {
    return listarTodas((offset, limit) => this.pagina(filtros, offset, limit));
  }

  obtener(id: number): Promise<T> {
    return ejecutar(this.http.get<T>(this.url(`/${id}`)));
  }

  /** Sustituye todos los campos editables (PUT). */
  reemplazar(id: number, datos: Entrada): Promise<T> {
    return ejecutar(this.http.put<T>(this.url(`/${id}`), datos));
  }

  eliminar(id: number): Promise<void> {
    return ejecutar(this.http.delete<void>(this.url(`/${id}`)));
  }

  protected crear(datos: Entrada): Promise<T> {
    return ejecutar(this.http.post<T>(this.url(), datos));
  }

  protected url(sufijo = ''): string {
    return `${RUTA_API}${this.ruta}${sufijo}`;
  }
}
