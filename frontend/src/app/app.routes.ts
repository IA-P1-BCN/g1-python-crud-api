import { Routes } from '@angular/router';
import { adminGuard, authGuard, invitadoGuard, staffGuard } from './core/auth/auth.guards';
import { AppShellComponent } from './shared/components/app-shell.component';

/**
 * Portal en la raíz del dominio (estilo #116): marketplace, panel staff y
 * administración, con guards por rol. Las rutas antiguas redirigen.
 */
export const routes: Routes = [
  {
    path: 'auth',
    canActivate: [invitadoGuard],
    loadChildren: () => import('./features/auth/auth.routes').then((m) => m.AUTH_ROUTES),
  },
  // Compatibilidad con enlaces antiguos.
  { path: 'login', pathMatch: 'full', redirectTo: 'auth/login' },
  { path: 'registro', pathMatch: 'full', redirectTo: 'auth/registro' },
  {
    path: '',
    component: AppShellComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'marketplace' },
      {
        path: 'marketplace',
        canActivate: [authGuard],
        loadChildren: () =>
          import('./features/marketplace/marketplace.routes').then((m) => m.MARKETPLACE_ROUTES),
      },
      {
        path: 'staff',
        canActivate: [staffGuard],
        loadChildren: () => import('./features/staff/staff.routes').then((m) => m.STAFF_ROUTES),
      },
      {
        path: 'admin',
        canActivate: [adminGuard],
        loadChildren: () => import('./features/admin/admin.routes').then((m) => m.ADMIN_ROUTES),
      },
      {
        path: 'perfil',
        canActivate: [authGuard],
        loadChildren: () => import('./features/perfil/perfil.routes').then((m) => m.PERFIL_ROUTES),
      },
      // Compatibilidad con enlaces antiguos del portal.
      { path: 'portal', children: [{ path: '**', redirectTo: ({ url }) => '/' + url.join('/') }] },
      { path: 'clases', redirectTo: 'marketplace' },
      { path: 'reservas', redirectTo: 'marketplace/mis-reservas' },
      { path: 'clientes', redirectTo: 'admin/clientes' },
      { path: 'entrenadores', redirectTo: 'admin/entrenadores' },
      { path: 'gestion-clases', redirectTo: 'staff/clases' },
      { path: 'pagos', redirectTo: 'admin/pagos' },
      { path: 'cuentas', redirectTo: 'admin/cuentas' },
      { path: 'export', redirectTo: 'admin/export' },
    ],
  },
  { path: '**', redirectTo: 'marketplace' },
];
