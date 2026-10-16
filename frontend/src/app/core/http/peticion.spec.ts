import { HttpErrorResponse } from '@angular/common/http';
import { NetworkError } from '../auth/auth.errors';
import { ApiError, aParams, listarTodas, traducirErrorHttp, TAMANO_PAGINA } from './peticion';

describe('listarTodas', () => {
  it('pide páginas hasta que una llega incompleta', async () => {
    const llamadas: Array<[number, number]> = [];
    const total = TAMANO_PAGINA * 2 + 5;
    const todas = await listarTodas(async (offset, limit) => {
      llamadas.push([offset, limit]);
      const fin = Math.min(offset + limit, total);
      return Array.from({ length: fin - offset }, (_, i) => offset + i);
    });

    expect(todas).toHaveLength(total);
    expect(llamadas).toEqual([
      [0, TAMANO_PAGINA],
      [TAMANO_PAGINA, TAMANO_PAGINA],
      [TAMANO_PAGINA * 2, TAMANO_PAGINA],
    ]);
  });

  it('con página vacía devuelve lista vacía sin repetir', async () => {
    const pedir = vi.fn(async () => [] as number[]);
    await expect(listarTodas(pedir)).resolves.toEqual([]);
    expect(pedir).toHaveBeenCalledTimes(1);
  });
});

describe('traducirErrorHttp', () => {
  it('status 0 (sin conexión) se convierte en NetworkError', () => {
    const error = new HttpErrorResponse({ status: 0, statusText: 'Unknown Error' });
    expect(traducirErrorHttp(error)).toBeInstanceOf(NetworkError);
  });

  it('usa el detail de la API en un ApiError', () => {
    const error = new HttpErrorResponse({
      status: 409,
      statusText: 'Conflict',
      error: { detail: 'La clase no tiene plazas disponibles' },
    });
    const traducido = traducirErrorHttp(error);
    expect(traducido).toBeInstanceOf(ApiError);
    expect((traducido as ApiError).status).toBe(409);
    expect((traducido as ApiError).detalle).toBe('La clase no tiene plazas disponibles');
  });

  it('un detail no textual (422) cae a un mensaje genérico', () => {
    const error = new HttpErrorResponse({
      status: 422,
      statusText: 'Unprocessable',
      error: { detail: [{ msg: 'campo inválido' }] },
    });
    expect((traducirErrorHttp(error) as ApiError).detalle).toBe(
      'Datos no válidos o error del servidor',
    );
  });
});

describe('aParams', () => {
  it('omite null y undefined', () => {
    const params = aParams({ id_clase: 3, id_cliente: null, offset: 0, extra: undefined });
    expect(params.keys()).toEqual(['id_clase', 'offset']);
    expect(params.get('offset')).toBe('0');
  });
});
