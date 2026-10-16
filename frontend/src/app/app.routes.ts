import { Routes } from '@angular/router';
import { LoginComponent } from './features/login/login.component';
import { AppShellComponent } from './shared/components/app-shell.component';

/** El portal vive en la raíz; los enlaces antiguos conservan redirección. */
export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: 'registro',
    loadChildren: () => import('./features/registro/registro.routes').then((m) => m.REGISTRO_ROUTES),
  },
  {
    path: 'portal',
    children: [
      { path: '', pathMatch: 'full', redirectTo: '/' },
      { path: '**', redirectTo: ({ url }) => '/' + url.map((segment) => segment.toString()).join('/') },
    ],
  },
  {
    path: '',
    component: AppShellComponent,
    children: [
      {
        path: '',
        loadChildren: () => import('./features/inicio/inicio.routes').then((m) => m.INICIO_ROUTES),
      },
      {
        path: 'clases',
        loadChildren: () => import('./features/clases/clases.routes').then((m) => m.CLASES_ROUTES),
      },
      {
        path: 'reservas',
        loadChildren: () => import('./features/reservas/reservas.routes').then((m) => m.RESERVAS_ROUTES),
      },
      {
        path: 'clientes',
        loadChildren: () => import('./features/clientes/clientes.routes').then((m) => m.CLIENTES_ROUTES),
      },
      {
        path: 'entrenadores',
        loadChildren: () => import('./features/entrenadores/entrenadores.routes').then((m) => m.ENTRENADORES_ROUTES),
      },
      {
        path: 'gestion-clases',
        loadChildren: () => import('./features/gestion-clases/gestion-clases.routes').then((m) => m.GESTION_CLASES_ROUTES),
      },
      {
        path: 'pagos',
        loadChildren: () => import('./features/pagos/pagos.routes').then((m) => m.PAGOS_ROUTES),
      },
      {
        path: 'cuentas',
        loadChildren: () => import('./features/cuentas/cuentas.routes').then((m) => m.CUENTAS_ROUTES),
      },
      {
        path: 'perfil',
        loadChildren: () => import('./features/perfil/perfil.routes').then((m) => m.PERFIL_ROUTES),
      },
      {
        path: 'export',
        loadChildren: () => import('./features/export/export.routes').then((m) => m.EXPORT_ROUTES),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
