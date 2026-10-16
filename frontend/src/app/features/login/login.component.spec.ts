import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { vi } from 'vitest';
import {
  AuthService,
  DatosRegistro,
  UsuarioAutenticado,
} from '../../core/auth/auth.service';
import { InvalidCredentialsError, NetworkError } from '../../core/auth/auth.errors';
import { SessionService } from '../../core/auth/session.service';
import { USUARIO_ANA } from '../../core/auth/usuarios-prueba';
import { LoginComponent } from './login.component';

class AuthServiceFalso extends AuthService {
  login = vi.fn<(email: string, password: string) => Promise<UsuarioAutenticado>>();
  register = vi.fn<(datos: DatosRegistro) => Promise<void>>();
}

describe('LoginComponent', () => {
  let fixture: ComponentFixture<LoginComponent>;
  let auth: AuthServiceFalso;
  let router: Router;

  beforeEach(async () => {
    sessionStorage.clear();
    auth = new AuthServiceFalso();
    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [provideRouter([]), { provide: AuthService, useValue: auth }],
    }).compileComponents();

    router = TestBed.inject(Router);
    vi.spyOn(router, 'navigateByUrl').mockResolvedValue(true);
    fixture = TestBed.createComponent(LoginComponent);
    fixture.detectChanges();
  });

  const componente = () => fixture.componentInstance;
  const texto = () => (fixture.nativeElement as HTMLElement).textContent ?? '';

  function rellenar(email: string, password: string): void {
    componente()['form'].setValue({ email, password });
    fixture.detectChanges();
  }

  function enviar(): void {
    const formulario = (fixture.nativeElement as HTMLElement).querySelector('form') as HTMLFormElement;
    formulario.dispatchEvent(new Event('submit'));
    fixture.detectChanges();
  }

  it('muestra mensajes de campo obligatorio y no llama a AuthService', () => {
    enviar();
    expect(auth.login).not.toHaveBeenCalled();
    expect(texto()).toContain('El correo electrónico es obligatorio.');
    expect(texto()).toContain('La contraseña es obligatoria.');
  });

  it('rechaza un correo con formato inválido sin enviar la petición', () => {
    rellenar('no-es-correo', 'abc');
    enviar();
    expect(auth.login).not.toHaveBeenCalled();
    expect(texto()).toContain('Introduce un correo electrónico válido.');
  });

  it('guarda la sesión y entra al portal si la cuenta tiene ficha', async () => {
    auth.login.mockResolvedValue(USUARIO_ANA);
    rellenar('cliente@gym.test', 'cliente123');
    enviar();
    await new Promise((r) => setTimeout(r, 0));

    expect(auth.login).toHaveBeenCalledWith('cliente@gym.test', 'cliente123');
    expect(TestBed.inject(SessionService).usuario()).toEqual(USUARIO_ANA);
    expect(router.navigateByUrl).toHaveBeenCalledWith('/');
  });

  it('muestra el error de credenciales y permanece en login', async () => {
    auth.login.mockRejectedValue(new InvalidCredentialsError());
    rellenar('a@b.es', 'mal');
    enviar();
    await new Promise((r) => setTimeout(r, 0));
    fixture.detectChanges();
    expect(texto()).toContain('Correo o contraseña incorrectos');
    expect(router.navigateByUrl).not.toHaveBeenCalled();
    expect(TestBed.inject(SessionService).autenticado()).toBe(false);
  });

  it('muestra el error de conexión y conserva los datos introducidos', async () => {
    auth.login.mockRejectedValue(new NetworkError());
    rellenar('a@b.es', 'secreto');
    enviar();
    await new Promise((r) => setTimeout(r, 0));
    fixture.detectChanges();
    expect(texto()).toContain('No se pudo conectar con el servidor. Inténtalo de nuevo.');
    expect(componente()['form'].getRawValue()).toEqual({ email: 'a@b.es', password: 'secreto' });
  });

  it('deshabilita el botón mientras la petición está en curso', async () => {
    let resolver!: (u: UsuarioAutenticado) => void;
    auth.login.mockReturnValue(new Promise((r) => (resolver = r)));
    rellenar('a@b.es', 'secreto');
    enviar();

    const boton = (fixture.nativeElement as HTMLElement).querySelector('button[type="submit"]') as HTMLButtonElement;
    expect(boton.disabled).toBe(true);
    expect(texto()).toContain('Validando');

    resolver(USUARIO_ANA);
    await new Promise((r) => setTimeout(r, 0));
    fixture.detectChanges();
    expect(boton.disabled).toBe(false);
  });

  it('ofrece enlace a /registro', () => {
    const enlace = (fixture.nativeElement as HTMLElement).querySelector('a[href="/registro"]');
    expect(enlace?.textContent).toContain('Crear cuenta');
  });
});
