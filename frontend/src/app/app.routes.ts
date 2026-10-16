import { Routes } from '@angular/router';
import { homeGuard, invitadoGuard, portalGuard } from './core/auth/auth.guards';
import { HomePage } from './features/home/pages/home.page';
import { LoginComponent } from './features/login/login.component';
import { AppShellComponent } from './shared/components/app-shell.component';

/**
 * "/" es la home pública. El portal del socio vive bajo "/portal" y exige sesión
 * con ficha de socio. Login y registro solo se muestran sin sesión.
 */
export const routes: Routes = [
  { path: '', component: HomePage }, 
  // canActivate: [homeGuard]
  { path: 'login', component: LoginComponent}, 
  //canActivate: [invitadoGuard] 
  {
    path: 'registro',
    //canActivate: [invitadoGuard],
    loadChildren: () => import('./features/registro/registro.routes').then((m) => m.REGISTRO_ROUTES),
  },
  {
    path: 'portal',
    component: AppShellComponent,
  //  canActivate: [portalGuard],
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
