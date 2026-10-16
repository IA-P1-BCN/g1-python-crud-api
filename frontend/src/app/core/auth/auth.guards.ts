import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SessionService } from './session.service';

/** Portal del socio: exige sesión y ficha de socio. Sin sesión, va a login con returnUrl. */
export const portalGuard: CanActivateFn = (_route, state) => {
  const session = inject(SessionService);
  const router = inject(Router);
  if (!session.autenticado()) {
    return router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
  }
  return session.idCliente() === null ? router.createUrlTree(['/']) : true;
};

/** Login y registro: con sesión activa no se muestran. */
export const invitadoGuard: CanActivateFn = () => {
  const session = inject(SessionService);
  const router = inject(Router);
  if (!session.autenticado()) {
    return true;
  }
  return router.createUrlTree([session.idCliente() !== null ? '/portal' : '/']);
};

/** Home pública: quien tiene ficha de socio va directo a su portal. */
export const homeGuard: CanActivateFn = () => {
  const session = inject(SessionService);
  const router = inject(Router);
  return session.idCliente() !== null ? router.createUrlTree(['/portal']) : true;
};
