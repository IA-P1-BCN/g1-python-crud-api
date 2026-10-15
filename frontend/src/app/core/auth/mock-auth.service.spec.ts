import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';
import { EmailDuplicadoError, InvalidCredentialsError, NetworkError } from './auth.errors';
import { MockAuthService } from './mock-auth.service';
import { USUARIO_ANA, USUARIO_STAFF } from './usuarios-prueba';

describe('MockAuthService', () => {
  let servicio: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{ provide: AuthService, useClass: MockAuthService }],
    });
    servicio = TestBed.inject(AuthService);
  });

  it('devuelve el usuario con nombre y ficha con credenciales válidas', async () => {
    expect(await servicio.login('cliente@gym.test', 'cliente123')).toEqual(USUARIO_ANA);
  });

  it('devuelve el staff sin ficha de socio', async () => {
    expect(await servicio.login('staff@gym.test', 'staff123')).toEqual(USUARIO_STAFF);
  });

  it('ignora mayúsculas y espacios en el correo', async () => {
    const usuario = await servicio.login('  STAFF@gym.test ', 'staff123');
    expect(usuario.rol).toBe('staff');
  });

  it('lanza InvalidCredentialsError con contraseña incorrecta o usuario inexistente', async () => {
    await expect(servicio.login('cliente@gym.test', 'mala')).rejects.toBeInstanceOf(InvalidCredentialsError);
    await expect(servicio.login('nadie@gym.test', 'x')).rejects.toBeInstanceOf(InvalidCredentialsError);
  });

  it('lanza NetworkError con el correo que simula la caída de red', async () => {
    await expect(servicio.login('sin-red@gym.test', 'x')).rejects.toBeInstanceOf(NetworkError);
  });

  it('registra una cuenta nueva que después puede iniciar sesión', async () => {
    await servicio.register({
      nombre: 'Luis',
      email: 'Luis@gym.test',
      password: 'contraseña-larga-1',
      crear_cliente: false,
    });
    const usuario = await servicio.login('luis@gym.test', 'contraseña-larga-1');
    expect(usuario).toMatchObject({ nombre: 'Luis', rol: 'cliente', id_cliente: null });
  });

  it('asigna ficha al registrarse con crear_cliente', async () => {
    await servicio.register({
      nombre: 'Marta',
      email: 'marta@gym.test',
      password: 'contraseña-larga-2',
      crear_cliente: true,
    });
    const usuario = await servicio.login('marta@gym.test', 'contraseña-larga-2');
    expect(usuario.id_cliente).not.toBeNull();
  });

  it('rechaza un correo ya registrado con EmailDuplicadoError', async () => {
    await expect(
      servicio.register({ nombre: 'X', email: 'cliente@gym.test', password: 'contraseña-larga-1', crear_cliente: false }),
    ).rejects.toBeInstanceOf(EmailDuplicadoError);
  });

  it('rechaza contraseñas de menos de 12 caracteres', async () => {
    await expect(
      servicio.register({ nombre: 'X', email: 'nuevo@gym.test', password: 'corta', crear_cliente: false }),
    ).rejects.toBeInstanceOf(RangeError);
  });
});
