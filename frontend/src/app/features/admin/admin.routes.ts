import { Routes } from '@angular/router';
import { AdminDashboardPage } from './pages/admin-dashboard.page';

/** Administración: dashboard y pantallas de gestión existentes, con adminGuard en la raíz. */
export const ADMIN_ROUTES: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
  { path: 'dashboard', component: AdminDashboardPage },
  {
    path: 'clientes',
    loadChildren: () => import('../clientes/clientes.routes').then((m) => m.CLIENTES_ROUTES),
  },
  {
    path: 'entrenadores',
    loadChildren: () => import('../entrenadores/entrenadores.routes').then((m) => m.ENTRENADORES_ROUTES),
  },
  {
    path: 'clases',
    loadChildren: () =>
      import('../gestion-clases/gestion-clases.routes').then((m) => m.GESTION_CLASES_ROUTES),
  },
  {
    path: 'pagos',
    loadChildren: () => import('../pagos/pagos.routes').then((m) => m.PAGOS_ROUTES),
  },
  {
    path: 'cuentas',
    loadChildren: () => import('../cuentas/cuentas.routes').then((m) => m.CUENTAS_ROUTES),
  },
  {
    path: 'export',
    loadChildren: () => import('../export/export.routes').then((m) => m.EXPORT_ROUTES),
  },
];
