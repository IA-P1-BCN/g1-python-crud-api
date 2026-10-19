import { Routes } from '@angular/router';
import { HomeMarketplacePage } from './pages/home-marketplace.page';
import { ResultadosPage } from './pages/resultados.page';
import { ClaseDetallePage } from './pages/clase-detalle.page';
import { MisReservasPage } from './pages/mis-reservas.page';

/** Catálogo del gimnasio: home, búsqueda, detalle de clase y reservas del socio. */
export const MARKETPLACE_ROUTES: Routes = [
  { path: '', component: HomeMarketplacePage },
  { path: 'resultados', component: ResultadosPage },
  { path: 'clases/:id', component: ClaseDetallePage },
  { path: 'mis-reservas', component: MisReservasPage },
];
