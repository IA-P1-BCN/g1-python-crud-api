import { Component, computed, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { SessionService } from '../../../core/auth/session.service';
import { ClaseService } from '../../../services/clase.service';
import { cargarClasesConCupo } from '../../../services/clases-con-cupo';
import { ReservaService, SinPlazasError, YaReservadaError } from '../../../services/reserva.service';
import { ClaseCardComponent } from '../../../shared/components/clase-card.component';
import { ToastComponent } from '../../../shared/components/toast.component';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { esPasada } from '../../../shared/format/fecha';
import { ClaseConCupo } from '../../../shared/models/clase.model';

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

/** Home del marketplace: hero, buscador y próximas clases (como el home de la referencia). */
@Component({
  selector: 'app-home-marketplace',
  imports: [
    ReactiveFormsModule,
    RouterLink,
    ClaseCardComponent,
    ToastComponent,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
  ],
  template: `
    <section class="mb-8 rounded-xl bg-primary/10 p-8">
      <h1 class="mb-2 text-3xl font-semibold">Reserva tu plaza en GymFlow</h1>
      <p class="mb-4 text-muted-foreground">
        Consulta las clases del gimnasio, mira las plazas libres y reserva en un clic.
      </p>
      <form class="flex flex-wrap items-end gap-3" (submit)="buscar($event)">
        <label hlmLabel class="flex min-w-56 flex-col items-start gap-1">
          Buscar clase
          <input hlmInput type="search" placeholder="Nombre de la clase" [formControl]="busqueda" />
        </label>
        <button hlmBtn type="submit">Buscar</button>
      </form>
    </section>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h2 class="text-xl font-semibold">Próximas clases</h2>
      <a hlmBtn variant="outline" routerLink="/marketplace/resultados">Ver todas</a>
    </div>

    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando clases…</p>
    } @else if (proximas().length === 0) {
      <p class="text-sm text-muted-foreground">No hay clases programadas.</p>
    } @else {
      <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        @for (item of proximas(); track item.clase.id_clase) {
          <app-clase-card [item]="item" (reservar)="reservar($event)" />
        }
      </section>
    }
  `,
})
export class HomeMarketplacePage {
  private readonly clases = inject(ClaseService);
  private readonly reservas = inject(ReservaService);
  private readonly session = inject(SessionService);
  private readonly router = inject(Router);

  protected readonly cargando = signal(true);
  protected readonly items = signal<ClaseConCupo[]>([]);
  protected readonly aviso = signal<Aviso | null>(null);
  protected readonly busqueda = new FormControl('', { nonNullable: true });

  protected readonly proximas = computed(() =>
    this.items()
      .filter((i) => !esPasada(i.clase.horario))
      .sort((a, b) => a.clase.horario.localeCompare(b.clase.horario))
      .slice(0, 6),
  );

  constructor() {
    void this.cargar();
  }

  protected buscar(evento: Event): void {
    evento.preventDefault();
    const q = this.busqueda.value.trim();
    void this.router.navigate(['/marketplace/resultados'], { queryParams: q ? { q } : {} });
  }

  protected async reservar(idClase: number): Promise<void> {
    const idCliente = this.session.idCliente();
    if (idCliente === null) {
      this.aviso.set({ mensaje: 'Tu cuenta no tiene ficha de socio', tipo: 'error' });
      return;
    }
    this.aviso.set(null);
    try {
      await this.reservas.crear(idCliente, idClase);
      this.aviso.set({ mensaje: 'Reserva confirmada', tipo: 'exito' });
      await this.cargar();
    } catch (error) {
      this.aviso.set({ mensaje: mensajeDeReserva(error), tipo: 'error' });
    }
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    this.items.set(await cargarClasesConCupo(this.clases, this.reservas, this.session.idCliente()));
    this.cargando.set(false);
  }
}

export function mensajeDeReserva(error: unknown): string {
  if (error instanceof SinPlazasError || error instanceof YaReservadaError) {
    return error.message;
  }
  return 'No se pudo completar la reserva. Inténtalo de nuevo.';
}
