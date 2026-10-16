import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, Router, RouterStateSnapshot, UrlTree, provideRouter } from '@angular/router';
import { SessionService } from './session.service';
import { homeGuard, invitadoGuard, portalGuard } from './auth.guards';
import { USUARIO_ANA, USUARIO_STAFF } from './usuarios-prueba';

describe('guardas de autenticación', () => {
  let router: Router;
  let sesion: SessionService;
  const estado = (url: string) => ({ url }) as RouterStateSnapshot;
  const ruta = {} as ActivatedRouteSnapshot;

  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({ providers: [provideRouter([])] });
    router = TestBed.inject(Router);
    sesion = TestBed.inject(SessionService);
  });

  it('portal: sin sesión redirige a login conservando la ruta pedida', () => {
    const resultado = TestBed.runInInjectionContext(() => portalGuard(ruta, estado('/portal/clases')));
    expect(resultado).toBeInstanceOf(UrlTree);
    const url = router.serializeUrl(resultado as UrlTree);
    expect(url).toContain('/login');
    expect(url).toContain('returnUrl');
  });

  it('portal: con socio permite el acceso', () => {
    sesion.iniciar(USUARIO_ANA);
    expect(TestBed.runInInjectionContext(() => portalGuard(ruta, estado('/portal')))).toBe(true);
  });

  it('portal: staff sin ficha vuelve a la home', () => {
    sesion.iniciar(USUARIO_STAFF);
    const resultado = TestBed.runInInjectionContext(() => portalGuard(ruta, estado('/portal')));
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/');
  });

  it('invitado: con sesión de socio, login y registro llevan al portal', () => {
    sesion.iniciar(USUARIO_ANA);
    const resultado = TestBed.runInInjectionContext(() => invitadoGuard(ruta, estado('/login')));
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/');
  });

  it('invitado: sin sesión puede ver login', () => {
    expect(TestBed.runInInjectionContext(() => invitadoGuard(ruta, estado('/login')))).toBe(true);
  });

  it('home: socio y visitante permanecen en la raíz sin bucle', () => {
    expect(TestBed.runInInjectionContext(() => homeGuard(ruta, estado('/')))).toBe(true);
    sesion.iniciar(USUARIO_ANA);
    const resultado = TestBed.runInInjectionContext(() => homeGuard(ruta, estado('/')));
    expect(resultado).toBe(true);
  });

  it('home: staff sin ficha se queda en la home', () => {
    sesion.iniciar(USUARIO_STAFF);
    expect(TestBed.runInInjectionContext(() => homeGuard(ruta, estado('/')))).toBe(true);
  });
});
