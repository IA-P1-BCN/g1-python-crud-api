import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SessionService } from './session.service';

/** Ruta destino cuando no hay sesión (o la sesión ha caducado). */
function aLogin(returnUrl: string) {
  const router = inject(Router);
  return router.createUrlTree(['/auth/login'], { queryParams: { returnUrl } });
}

/** Catálogo y portal: exige sesión válida (la API /v1 pide JWT). */
export const authGuard: CanActivateFn = (_route, state) => {
  const session = inject(SessionService);
  const router = inject(Router);
  if (!session.autenticado()) {
    return router.createUrlTree(['/auth/login'], { queryParams: { returnUrl: state.url } });
  }
  return true;
};

/** Panel del staff: rol staff o admin. */
export const staffGuard: CanActivateFn = (_route, state) => {
  const session = inject(SessionService);
  const rol = session.usuario()?.rol;
  if (rol === 'staff' || rol === 'admin') {
    return true;
  }
  if (rol === undefined) {
    return aLogin(state.url);
  }
  const router = inject(Router);
  return router.createUrlTree(['/marketplace']);
};

/** Administración: solo rol admin. */
export const adminGuard: CanActivateFn = (_route, state) => {
  const session = inject(SessionService);
  const rol = session.usuario()?.rol;
  if (rol === 'admin') {
    return true;
  }
  if (rol === undefined) {
    return aLogin(state.url);
  }
  const router = inject(Router);
  return rol === 'staff' ? router.createUrlTree(['/staff']) : router.createUrlTree(['/marketplace']);
};

/** Login y registro: con sesión activa no se muestran. */
export const invitadoGuard: CanActivateFn = () => {
  const session = inject(SessionService);
  const router = inject(Router);
  if (!session.autenticado()) {
    return true;
  }
  const rol = session.usuario()?.rol;
  return router.createUrlTree(rol === 'admin' ? ['/admin'] : rol === 'staff' ? ['/staff'] : ['/marketplace']);
};
