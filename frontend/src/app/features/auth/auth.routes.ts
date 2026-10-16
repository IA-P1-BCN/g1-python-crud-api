import { Routes } from '@angular/router';
import { LoginComponent } from '../login/login.component';

/** Autenticación pública: login y registro (ambas páginas fuera del shell). */
export const AUTH_ROUTES: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'login' },
  { path: 'login', component: LoginComponent },
  {
    path: 'registro',
    loadChildren: () => import('../registro/registro.routes').then((m) => m.REGISTRO_ROUTES),
  },
];
