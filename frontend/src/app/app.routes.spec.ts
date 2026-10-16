import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { routes } from './app.routes';
import { AuthService, UsuarioAutenticado } from './core/auth/auth.service';
import { SessionService } from './core/auth/session.service';
import { USUARIO_ANA } from './core/auth/usuarios-prueba';
import { ClaseService } from './services/clase.service';
import { ReservaService } from './services/reserva.service';

describe('rutas del portal rediseñado', () => {
  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        provideRouter(routes),
        {
          provide: AuthService,
          useValue: { login: async () => USUARIO_ANA, register: async () => undefined },
        },
        {
          provide: ClaseService,
          useValue: {
            listar: async () => [],
            obtener: async () => null,
            listarEntrenadores: async () => [],
            cupo: async () => null,
          },
        },
        { provide: ReservaService, useValue: { listarDeCliente: async () => [], crear: async () => ({}) } },
      ],
    });
  });

  it('la raíz redirige al marketplace; sin sesión, el guard envía a login', async () => {
    const harness = await RouterTestingHarness.create('/');
    const router = TestBed.inject(Router);
    expect(router.url).toContain('/auth/login');
    expect(router.url).toContain('returnUrl');
    expect(harness.routeNativeElement?.textContent).toContain('GymFlow');
  });

  it('con sesión, la raíz muestra el home del marketplace', async () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    const harness = await RouterTestingHarness.create('/');
    const router = TestBed.inject(Router);
    expect(router.url).toBe('/marketplace');
    expect(harness.routeNativeElement?.textContent).toContain('Reserva tu plaza');
  });

  it('las rutas antiguas redirigen a las nuevas y respetan el guard', async () => {
    const router = TestBed.inject(Router);
    const harness = await RouterTestingHarness.create('/login');
    expect(router.url).toContain('/auth/login');
    await harness.navigateByUrl('/clientes');
    expect(router.url).toContain('/auth/login');
    expect(router.url).toContain('returnUrl');
  });
});
