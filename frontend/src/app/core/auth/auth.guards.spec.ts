import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, Router, RouterStateSnapshot, UrlTree, provideRouter } from '@angular/router';
import { SessionService } from './session.service';
import { adminGuard, authGuard, invitadoGuard, marketplaceGuard, staffGuard } from './auth.guards';
import { USUARIO_ADMIN, USUARIO_ANA, USUARIO_STAFF } from './usuarios-prueba';

describe('guardas del portal', () => {
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

  it('auth: sin sesión redirige a /auth/login con returnUrl', () => {
    const resultado = TestBed.runInInjectionContext(() => authGuard(ruta, estado('/marketplace')));
    expect(resultado).toBeInstanceOf(UrlTree);
    const url = router.serializeUrl(resultado as UrlTree);
    expect(url).toContain('/auth/login');
    expect(url).toContain('returnUrl');
  });

  it('auth: con sesión permite el marketplace', () => {
    sesion.iniciar(USUARIO_ANA);
    expect(TestBed.runInInjectionContext(() => authGuard(ruta, estado('/marketplace')))).toBe(true);
  });

  it('marketplace: el staff se redirige a /staff', () => {
    sesion.iniciar(USUARIO_STAFF);
    const resultado = TestBed.runInInjectionContext(() => marketplaceGuard(ruta, estado('/marketplace')));
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/staff');
  });

  it('marketplace: el cliente y el admin sí entran', () => {
    sesion.iniciar(USUARIO_ANA);
    expect(TestBed.runInInjectionContext(() => marketplaceGuard(ruta, estado('/marketplace')))).toBe(true);
    sesion.cerrar();
    sesion.iniciar(USUARIO_ADMIN);
    expect(TestBed.runInInjectionContext(() => marketplaceGuard(ruta, estado('/marketplace')))).toBe(true);
  });

  it('marketplace: sin sesión va a login con returnUrl', () => {
    const resultado = TestBed.runInInjectionContext(() => marketplaceGuard(ruta, estado('/marketplace')));
    const url = router.serializeUrl(resultado as UrlTree);
    expect(url).toContain('/auth/login');
    expect(url).toContain('returnUrl');
  });

  it('staff: el cliente no entra y va al marketplace', () => {
    sesion.iniciar(USUARIO_ANA);
    const resultado = TestBed.runInInjectionContext(() => staffGuard(ruta, estado('/staff')));
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/marketplace');
  });

  it('staff: el staff y el admin sí entran', () => {
    sesion.iniciar(USUARIO_STAFF);
    expect(TestBed.runInInjectionContext(() => staffGuard(ruta, estado('/staff')))).toBe(true);
    sesion.cerrar();
    sesion.iniciar(USUARIO_ADMIN);
    expect(TestBed.runInInjectionContext(() => staffGuard(ruta, estado('/staff')))).toBe(true);
  });

  it('staff: sin sesión va a login', () => {
    const resultado = TestBed.runInInjectionContext(() => staffGuard(ruta, estado('/staff')));
    expect(router.serializeUrl(resultado as UrlTree)).toContain('/auth/login');
  });

  it('admin: el staff redirige a /staff y el cliente a /marketplace', () => {
    sesion.iniciar(USUARIO_STAFF);
    let resultado = TestBed.runInInjectionContext(() => adminGuard(ruta, estado('/admin')));
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/staff');
    sesion.cerrar();
    sesion.iniciar(USUARIO_ANA);
    resultado = TestBed.runInInjectionContext(() => adminGuard(ruta, estado('/admin')));
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/marketplace');
  });

  it('admin: solo el admin entra', () => {
    sesion.iniciar(USUARIO_ADMIN);
    expect(TestBed.runInInjectionContext(() => adminGuard(ruta, estado('/admin')))).toBe(true);
  });

  it('invitado: sin sesión ve login; con sesión va a su destino por rol', () => {
    expect(TestBed.runInInjectionContext(() => invitadoGuard(ruta, estado('/auth/login')))).toBe(true);
    sesion.iniciar(USUARIO_ANA);
    let resultado = TestBed.runInInjectionContext(() => invitadoGuard(ruta, estado('/auth/login')));
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/marketplace');
    sesion.cerrar();
    sesion.iniciar(USUARIO_STAFF);
    resultado = TestBed.runInInjectionContext(() => invitadoGuard(ruta, estado('/auth/login')));
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/staff');
    sesion.cerrar();
    sesion.iniciar(USUARIO_ADMIN);
    resultado = TestBed.runInInjectionContext(() => invitadoGuard(ruta, estado('/auth/login')));
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/admin');
  });
});
