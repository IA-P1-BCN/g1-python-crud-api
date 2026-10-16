import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ClaseService } from '../../../services/clase.service';
import { textoDeError } from '../../../core/http/peticion';
import { ToastComponent } from '../../../shared/components/toast.component';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { esPasada, formatearFechaHora } from '../../../shared/format/fecha';
import { Clase } from '../../../shared/models/clase.model';

/** Panel del staff: resumen y accesos (como host-panel de la referencia). */
@Component({
  selector: 'app-staff-panel',
  imports: [RouterLink, ToastComponent, HlmButtonImports, HlmCardImports],
  template: `
    <h1 class="mb-4 text-3xl font-semibold">Panel del staff</h1>

    <app-toast [mensaje]="aviso()" [tipo]="'error'" />

    <section class="mb-6 grid gap-4 sm:grid-cols-2">
      <article hlmCard class="gap-3 p-4">
        <div hlmCardHeader>
          <h2 hlmCardTitle>Mis clases</h2>
        </div>
        <div hlmCardContent class="flex flex-col gap-2">
          <p class="text-sm text-muted-foreground">
            {{ proximas().length }} próximas · {{ total() }} en total
          </p>
          <a hlmBtn routerLink="/staff/clases">Gestionar clases</a>
        </div>
      </article>
      <article hlmCard class="gap-3 p-4">
        <div hlmCardHeader>
          <h2 hlmCardTitle>Reservas de mis clases</h2>
        </div>
        <div hlmCardContent class="flex flex-col gap-2">
          <p class="text-sm text-muted-foreground">Cancela reservas y marca la asistencia.</p>
          <a hlmBtn routerLink="/staff/reservas">Ver reservas</a>
        </div>
      </article>
    </section>

    <h2 class="mb-3 text-xl font-semibold">Próximas clases</h2>
    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando clases…</p>
    } @else if (proximas().length === 0) {
      <p class="text-sm text-muted-foreground">
        No tienes clases programadas. <a class="font-semibold text-primary" routerLink="/staff/clases">Crea una</a>
      </p>
    } @else {
      <ul class="grid list-none gap-3 p-0 sm:grid-cols-2 lg:grid-cols-3">
        @for (clase of proximas(); track clase.id_clase) {
          <li hlmCard class="flex flex-col gap-1 p-4">
            <p class="font-semibold">{{ clase.nombre_clase }}</p>
            <p class="text-sm text-muted-foreground">{{ formatear(clase.horario) }}</p>
          </li>
        }
      </ul>
    }
  `,
})
export class StaffPanelPage {
  private readonly clases = inject(ClaseService);

  protected readonly formatear = formatearFechaHora;
  protected readonly cargando = signal(true);
  protected readonly items = signal<Clase[]>([]);
  protected readonly aviso = signal<string | null>(null);

  protected readonly proximas = computed(() =>
    this.items()
      .filter((c) => !esPasada(c.horario))
      .sort((a, b) => a.horario.localeCompare(b.horario))
      .slice(0, 6),
  );
  protected readonly total = computed(() => this.items().length);

  constructor() {
    void this.cargar();
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    try {
      // El alcance de servidor limita el listado a las clases del staff.
      this.items.set(await this.clases.listar());
    } catch (error) {
      this.aviso.set(textoDeError(error));
    } finally {
      this.cargando.set(false);
    }
  }
}
