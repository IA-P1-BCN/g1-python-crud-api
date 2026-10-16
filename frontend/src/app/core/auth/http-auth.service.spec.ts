import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { authInterceptor } from '../http/auth.interceptor';
import { AuthService } from './auth.service';
import { EmailDuplicadoError, InvalidCredentialsError } from './auth.errors';
import { HttpAuthService } from './http-auth.service';

/** Deja correr las promesas pendientes (las peticiones encadenadas se emiten tras un turno). */
const turno = () => new Promise((resolver) => setTimeout(resolver));

describe('HttpAuthService', () => {
  let servicio: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        { provide: AuthService, useClass: HttpAuthService },
      ],
    });
    servicio = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('login envía el email como username en formulario y guarda el token', async () => {
    const promesa = servicio.login('ana@gym.test', 'clave-larga-123');
    const login = http.expectOne('/v1/auth/login');
    expect(login.request.method).toBe('POST');
    expect(login.request.body.toString()).toContain('username=ana@gym.test');
    expect(login.request.body.toString()).toContain('password=clave-larga-123');
    login.flush({ access_token: 'token-1', token_type: 'bearer' });

    await turno();
    const yo = http.expectOne('/v1/users/me');
    expect(yo.request.headers.get('Authorization')).toBe('Bearer token-1');
    yo.flush({
      id: 7,
      nombre: 'Ana García',
      email: 'ana@gym.test',
      activo: true,
      rol: 'cliente',
      fecha_creacion: '2026-10-01T10:00:00',
      id_cliente: 3,
    });

    await expect(promesa).resolves.toEqual({
      id: 7,
      nombre: 'Ana García',
      email: 'ana@gym.test',
      rol: 'cliente',
      id_cliente: 3,
    });
    expect(sessionStorage.getItem('gymflow.token')).toBe('token-1');
  });

  it('login con 401 lanza InvalidCredentialsError y no guarda token', async () => {
    const promesa = servicio.login('ana@gym.test', 'mal');
    http
      .expectOne('/v1/auth/login')
      .flush({ detail: 'Credenciales no válidas' }, { status: 401, statusText: 'Unauthorized' });

    await expect(promesa).rejects.toBeInstanceOf(InvalidCredentialsError);
    expect(sessionStorage.getItem('gymflow.token')).toBeNull();
  });

  it('register envía los datos del formulario tal cual a la API', async () => {
    const datos = {
      nombre: 'Ana García',
      email: 'ana@gym.test',
      password: 'clave-larga-123',
      crear_cliente: true,
    };
    const promesa = servicio.register(datos);
    const req = http.expectOne('/v1/auth/register');
    expect(req.request.body).toEqual(datos);
    req.flush({}, { status: 201, statusText: 'Created' });

    await expect(promesa).resolves.toBeUndefined();
  });

  it('register con 409 lanza EmailDuplicadoError', async () => {
    const promesa = servicio.register({
      nombre: 'Ana',
      email: 'ana@gym.test',
      password: 'clave-larga-123',
      crear_cliente: false,
    });
    http
      .expectOne('/v1/auth/register')
      .flush({ detail: 'Email de Cuenta ya registrado' }, { status: 409, statusText: 'Conflict' });

    await expect(promesa).rejects.toBeInstanceOf(EmailDuplicadoError);
  });
});
