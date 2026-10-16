import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { SessionService } from '../auth/session.service';
import { USUARIO_ANA } from '../auth/usuarios-prueba';
import { authInterceptor } from './auth.interceptor';

describe('authInterceptor', () => {
  let http: HttpClient;
  let mock: HttpTestingController;

  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
      ],
    });
    http = TestBed.inject(HttpClient);
    mock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => mock.verify());

  it('añade Bearer a las peticiones de /v1 cuando hay token', () => {
    sessionStorage.setItem('gymflow.token', 'abc');
    http.get('/v1/clases').subscribe();

    const req = mock.expectOne('/v1/clases');
    expect(req.request.headers.get('Authorization')).toBe('Bearer abc');
    req.flush([]);
  });

  it('no añade cabecera sin token', () => {
    http.get('/v1/clases').subscribe();

    const req = mock.expectOne('/v1/clases');
    expect(req.request.headers.has('Authorization')).toBe(false);
    req.flush([]);
  });

  it('no envía el token fuera de /v1', () => {
    sessionStorage.setItem('gymflow.token', 'abc');
    http.get('https://ejemplo.test/otro').subscribe();

    const req = mock.expectOne('https://ejemplo.test/otro');
    expect(req.request.headers.has('Authorization')).toBe(false);
    req.flush({});
  });

  it('un 401 con token cierra la sesión y borra el token', () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    sessionStorage.setItem('gymflow.token', 'caducado');
    let error: unknown;
    http.get('/v1/users/me').subscribe({ error: (e: unknown) => (error = e) });

    mock
      .expectOne('/v1/users/me')
      .flush({ detail: 'No autenticado' }, { status: 401, statusText: 'Unauthorized' });

    expect(error).toBeDefined();
    expect(sessionStorage.getItem('gymflow.token')).toBeNull();
    expect(TestBed.inject(SessionService).autenticado()).toBe(false);
  });

  it('un 401 del propio login no cierra ninguna sesión', () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    sessionStorage.setItem('gymflow.token', 'previo');
    http.post('/v1/auth/login', {}).subscribe({ error: () => undefined });

    mock
      .expectOne('/v1/auth/login')
      .flush({ detail: 'Credenciales no válidas' }, { status: 401, statusText: 'Unauthorized' });

    expect(sessionStorage.getItem('gymflow.token')).toBe('previo');
    expect(TestBed.inject(SessionService).autenticado()).toBe(true);
  });
});
