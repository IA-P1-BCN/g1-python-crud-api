import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { routes } from './app.routes';
import { ClaseService } from './services/clase.service';
import { ReservaService } from './services/reserva.service';

describe('portal en la raíz', () => {
  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        provideRouter(routes),
        { provide: ClaseService, useValue: { listar: async () => [], listarEntrenadores: async () => [] } },
        { provide: ReservaService, useValue: { listarDeCliente: async () => [] } },
      ],
    });
  });

  it('muestra el shell y el inicio en /', async () => {
    const harness = await RouterTestingHarness.create('/');
    expect(harness.routeNativeElement?.textContent).toContain('Próxima clase');
    expect(harness.routeNativeElement?.querySelector('a[href="/clases"]')).not.toBeNull();
  });

  it('redirige las rutas antiguas al portal y sus pantallas en raíz', async () => {
    const harness = await RouterTestingHarness.create('/portal');
    const router = TestBed.inject(Router);
    expect(router.url).toBe('/');
    await harness.navigateByUrl('/portal/clases');
    expect(router.url).toBe('/clases');
    expect(harness.routeNativeElement?.textContent).toContain('Clases');
  });
});
