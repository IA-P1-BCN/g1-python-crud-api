import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';
import { InvalidCredentialsError, NetworkError } from './auth.errors';
import { MockAuthService } from './mock-auth.service';

describe('MockAuthService', () => {
  let servicio: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{ provide: AuthService, useClass: MockAuthService }],
    });
    servicio = TestBed.inject(AuthService);
  });

  it('devuelve el usuario con credenciales válidas', async () => {
    const usuario = await servicio.login('cliente@gym.test', 'cliente123');
    expect(usuario).toEqual({ id: 'mock-1', email: 'cliente@gym.test', rol: 'cliente' });
  });

  it('ignora mayúsculas y espacios en el correo', async () => {
    const usuario = await servicio.login('  STAFF@gym.test ', 'staff123');
    expect(usuario.rol).toBe('staff');
  });

  it('lanza InvalidCredentialsError con contraseña incorrecta', async () => {
    await expect(servicio.login('cliente@gym.test', 'mala')).rejects.toBeInstanceOf(
      InvalidCredentialsError,
    );
  });

  it('lanza InvalidCredentialsError con un usuario que no existe', async () => {
    await expect(servicio.login('nadie@gym.test', 'x')).rejects.toBeInstanceOf(
      InvalidCredentialsError,
    );
  });

  it('lanza NetworkError con el correo que simula la caída de red', async () => {
    await expect(servicio.login('sin-red@gym.test', 'x')).rejects.toBeInstanceOf(NetworkError);
  });
});
