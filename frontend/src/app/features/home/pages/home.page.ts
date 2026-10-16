import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { SessionService } from '../../../core/auth/session.service';
import { ClaseService } from '../../../services/clase.service';
import { cargarClasesConCupo } from '../../../services/clases-con-cupo';
import { ReservaService } from '../../../services/reserva.service';
import { CupoBarComponent } from '../../../shared/components/cupo-bar.component';
import { MenuComponent } from '../../../shared/components/menu.component';
import { formatearFechaHora } from '../../../shared/format/fecha';
import { ClaseConCupo } from '../../../shared/models/clase.model';
import { HlmAlertImports } from '@spartan-ng/helm/alert';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';

/** Home pública: clases en solo lectura. Reservar exige iniciar sesión. */
@Component({
  selector: 'app-home',
  imports: [RouterLink, CupoBarComponent, MenuComponent, HlmAlertImports, HlmButtonImports, HlmCardImports],
  template: `
    <header class="flex items-center justify-between bg-background px-6 py-2 shadow-sm">
      <a class="text-xl font-bold text-primary no-underline" routerLink="/">GymFlow</a>
      <app-menu />
    </header>

    <main class="mx-auto max-w-6xl px-4 py-6">
      <section class="mb-8">
        <h1 class="mb-2 text-3xl font-semibold">Bienvenido a GymFlow</h1>
        <p class="mb-4 text-muted-foreground">Consulta las clases del gimnasio y sus plazas libres. Para reservar necesitas una cuenta.</p>
        @if (!session.autenticado()) {
          <div class="flex flex-wrap gap-2">
            <a hlmBtn routerLink="/login">Iniciar sesión</a>
            <a hlmBtn variant="outline" routerLink="/registro">Crear cuenta</a>
          </div>
        }
      </section>

      <h2 class="mb-4 text-xl font-semibold">Clases</h2>
      @if (cargando()) {
        <p class="text-sm text-muted-foreground">Cargando clases…</p>
      } @else if (items().length === 0) {
        <p class="text-sm text-muted-foreground">No hay clases disponibles.</p>
      } @else {
        <ul class="grid list-none gap-4 p-0 sm:grid-cols-2 lg:grid-cols-3">
          @for (item of items(); track item.clase.id_clase) {
            <li hlmCard class="gap-3 p-4">
              <div hlmCardHeader><h3 hlmCardTitle>{{ item.clase.nombre_clase }}</h3></div>
              <div hlmCardContent class="flex flex-col gap-2">
                <p class="text-sm text-muted-foreground">{{ fecha(item.clase.horario) }}</p>
                <app-cupo-bar [plazasLibres]="item.plazasLibres" [capacidad]="item.clase.capacidad_max" />
                <button hlmBtn variant="outline" type="button" (click)="verDetalle(item)">Ver información</button>
              </div>
            </li>
          }
        </ul>
      }

      @if (seleccionada(); as item) {
        <section class="mt-6" aria-labelledby="titulo-detalle">
          <div hlmCard class="gap-3 p-5">
            <div hlmCardHeader><h2 id="titulo-detalle" hlmCardTitle>{{ item.clase.nombre_clase }}</h2></div>
            <div hlmCardContent class="flex flex-col gap-4">
              <dl class="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1">
                <dt class="text-muted-foreground">Horario</dt><dd class="m-0">{{ fecha(item.clase.horario) }}</dd>
                <dt class="text-muted-foreground">Entrenador</dt><dd class="m-0">{{ item.entrenador }}</dd>
                <dt class="text-muted-foreground">Capacidad</dt><dd class="m-0">{{ item.clase.capacidad_max }} plazas</dd>
                <dt class="text-muted-foreground">Plazas libres</dt><dd class="m-0">{{ item.plazasLibres }}</dd>
              </dl>

              @if (!session.autenticado()) {
                <div hlmAlert>
                  <p hlmAlertDescription>
                    Para reservar, <a class="font-semibold text-primary" routerLink="/login" [queryParams]="{ returnUrl: '/clases' }">inicia sesión</a>.
                  </p>
                </div>
              } @else if (session.idCliente() === null) {
                <div hlmAlert><p hlmAlertDescription>Tu cuenta no tiene ficha de socio, así que no puedes reservar.</p></div>
              } @else if (item.reservadaPorMi) {
                <div hlmAlert><p hlmAlertDescription>Ya tienes plaza reservada en esta clase.</p></div>
              } @else {
                <div hlmAlert><p hlmAlertDescription>Puedes reservarla desde <a class="font-semibold text-primary" routerLink="/clases">Clases</a> en tu portal.</p></div>
              }

              <button hlmBtn variant="outline" type="button" class="self-start" (click)="seleccionada.set(null)">Cerrar</button>
            </div>
          </div>
        </section>
      }
    </main>
  `,
})
export class HomePage {
  protected readonly session = inject(SessionService);
  private readonly clases = inject(ClaseService);
  private readonly reservas = inject(ReservaService);

  protected readonly cargando = signal(true);
  protected readonly items = signal<ClaseConCupo[]>([]);
  protected readonly seleccionada = signal<ClaseConCupo | null>(null);

  constructor() {
    void this.cargar();
  }

  protected verDetalle(item: ClaseConCupo): void {
    this.seleccionada.set(item);
  }

  protected fecha(horario: string): string {
    return formatearFechaHora(horario);
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    this.items.set(await cargarClasesConCupo(this.clases, this.reservas, this.session.idCliente()));
    this.cargando.set(false);
  }
}
