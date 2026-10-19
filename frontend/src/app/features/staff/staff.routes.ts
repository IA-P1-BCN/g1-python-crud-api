import { Routes } from '@angular/router';
import { StaffPanelPage } from './pages/staff-panel.page';
import { ReservasStaffPage } from './pages/reservas-staff.page';

/** Panel del staff: sus clases y sus reservas (el alcance de servidor limita los datos). */
export const STAFF_ROUTES: Routes = [
  { path: '', component: StaffPanelPage },
  {
    path: 'clases',
    loadChildren: () =>
      import('../gestion-clases/gestion-clases.routes').then((m) => m.GESTION_CLASES_ROUTES),
  },
  { path: 'reservas', component: ReservasStaffPage },
];
