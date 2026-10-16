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
  return router.createUrlTree(['/']);
};

/** La raíz ya contiene el portal y no necesita una redirección. */
export const homeGuard: CanActivateFn = () => {
  return true;
};
