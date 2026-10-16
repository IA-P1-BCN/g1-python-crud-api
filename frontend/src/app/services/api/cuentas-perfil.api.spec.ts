import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { CuentasApi } from './recursos.api';

describe('CuentasApi: perfil propio', () => {
  it('envía ambas contraseñas literales a PATCH /me, sin ID externo', async () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const api = TestBed.inject(CuentasApi);
    const http = TestBed.inject(HttpTestingController);
    const data = { password: ' nueva contraseña ', current_password: ' contraseña actual ' };
    const result = api.actualizarYo(data);
    const request = http.expectOne('/v1/users/me');
    expect(request.request.method).toBe('PATCH');
    expect(request.request.body).toEqual(data);
    request.flush({ id: 1, nombre: 'Ana', email: 'ana@example.com' });
    await expect(result).resolves.toMatchObject({ id: 1, nombre: 'Ana' });
    http.verify();
  });
});
