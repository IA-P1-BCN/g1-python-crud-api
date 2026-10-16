import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { vi } from 'vitest';
import {
  AuthService,
  DatosRegistro,
  UsuarioAutenticado,
} from '../../../core/auth/auth.service';
import { EmailDuplicadoError, NetworkError } from '../../../core/auth/auth.errors';
import { esperarCarga } from '../../../testing/esperar';
import { RegistroPage } from './registro.page';

class AuthServiceFalso extends AuthService {
  login = vi.fn<(email: string, password: string) => Promise<UsuarioAutenticado>>();
  register = vi.fn<(datos: DatosRegistro) => Promise<void>>();
}

describe('RegistroPage', () => {
  let fixture: ComponentFixture<RegistroPage>;
  let auth: AuthServiceFalso;
  let router: Router;

  beforeEach(async () => {
    auth = new AuthServiceFalso();
    await TestBed.configureTestingModule({
      imports: [RegistroPage],
      providers: [provideRouter([]), { provide: AuthService, useValue: auth }],
    }).compileComponents();

    router = TestBed.inject(Router);
    vi.spyOn(router, 'navigateByUrl').mockResolvedValue(true);
    fixture = TestBed.createComponent(RegistroPage);
    fixture.detectChanges();
  });

  const elemento = () => fixture.nativeElement as HTMLElement;
  const texto = () => elemento().textContent ?? '';
  const componente = () => fixture.componentInstance;

  function rellenar(nombre: string, email: string, password: string, crear = false): void {
    componente()['form'].setValue({ nombre, email, password, crearCliente: crear });
    fixture.detectChanges();
  }

  function enviar(): void {
    elemento().querySelector('form')!.dispatchEvent(new Event('submit'));
    fixture.detectChanges();
  }

  it('no envía el formulario vacío y muestra los errores obligatorios', () => {
    enviar();
    expect(auth.register).not.toHaveBeenCalled();
    expect(texto()).toContain('El nombre es obligatorio.');
    expect(texto()).toContain('El correo electrónico es obligatorio.');
    expect(texto()).toContain('La contraseña es obligatoria.');
  });

  it('exige una contraseña de al menos 12 caracteres', () => {
    rellenar('Ana', 'ana@gym.test', 'corta');
    enviar();
    expect(auth.register).not.toHaveBeenCalled();
    expect(texto()).toContain('al menos 12 caracteres');
  });

  it('envía los datos con los nombres de la API y vuelve al login con aviso', async () => {
    auth.register.mockResolvedValue(undefined);
    rellenar('  Ana García ', 'ana@gym.test', 'contraseña-larga-1', true);
    enviar();
    await esperarCarga(fixture);

    expect(auth.register).toHaveBeenCalledWith({
      nombre: 'Ana García',
      email: 'ana@gym.test',
      password: 'contraseña-larga-1',
      crear_cliente: true,
    });
    expect(router.navigateByUrl).toHaveBeenCalledWith('/login', {
      state: { mensaje: 'Cuenta creada. Ya puedes iniciar sesión' },
    });
  });

  it('muestra el error de correo duplicado y permanece en la página', async () => {
    auth.register.mockRejectedValue(new EmailDuplicadoError());
    rellenar('Ana', 'ana@gym.test', 'contraseña-larga-1');
    enviar();
    await esperarCarga(fixture);
    expect(texto()).toContain('Ya existe una cuenta con este correo');
    expect(router.navigateByUrl).not.toHaveBeenCalled();
  });

  it('muestra el error de conexión conservando los datos', async () => {
    auth.register.mockRejectedValue(new NetworkError());
    rellenar('Ana', 'ana@gym.test', 'contraseña-larga-1');
    enviar();
    await esperarCarga(fixture);
    expect(texto()).toContain('No se pudo conectar con el servidor. Inténtalo de nuevo.');
    expect(componente()['form'].getRawValue().email).toBe('ana@gym.test');
  });

  it('alterna la visibilidad de la contraseña', () => {
    const input = elemento().querySelector<HTMLInputElement>('input[formcontrolname="password"]')!;
    expect(input.type).toBe('password');
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Mostrar')!.click();
    fixture.detectChanges();
    expect(input.type).toBe('text');
  });
});
