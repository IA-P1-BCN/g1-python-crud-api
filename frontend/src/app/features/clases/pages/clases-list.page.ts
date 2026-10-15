import { Component, computed, inject, signal } from '@angular/core';
import { SessionService } from '../../../core/auth/session.service';
import { ClaseService } from '../../../services/clase.service';
import { cargarClasesConCupo } from '../../../services/clases-con-cupo';
import { ReservaService, SinPlazasError, YaReservadaError } from '../../../services/reserva.service';
import { ClaseCardComponent } from '../../../shared/components/clase-card.component';
import { ToastComponent } from '../../../shared/components/toast.component';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { ClaseConCupo } from '../../../shared/models/clase.model';

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

@Component({
  selector: 'app-clases-list',
  imports: [ClaseCardComponent, ToastComponent, HlmInputImports, HlmLabelImports],
  template: `
    <h1 class="mb-4 text-3xl font-semibold">Clases disponibles</h1>

    <label hlmLabel class="mb-4 flex max-w-sm flex-col items-start gap-1">
      Buscar por nombre
      <input hlmInput type="search" [value]="filtro()" (input)="filtro.set($any($event.target).value)" />
    </label>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando clases…</p>
    } @else if (visibles().length === 0) {
      <p class="text-sm text-muted-foreground">No hay clases disponibles.</p>
    } @else {
      <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        @for (item of visibles(); track item.clase.id_clase) {
          <app-clase-card [item]="item" (reservar)="reservar($event)" />
        }
      </section>
    }
  `,
})
export class ClasesListPage {
  private readonly clases = inject(ClaseService);
  private readonly reservas = inject(ReservaService);
  private readonly session = inject(SessionService);

  protected readonly cargando = signal(true);
  protected readonly items = signal<ClaseConCupo[]>([]);
  protected readonly filtro = signal('');
  protected readonly aviso = signal<Aviso | null>(null);

  protected readonly visibles = computed(() => {
    const texto = this.filtro().trim().toLowerCase();
    return texto
      ? this.items().filter((i) => i.clase.nombre_clase.toLowerCase().includes(texto))
      : this.items();
  });

  constructor() {
    void this.cargar();
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

function mensajeDeReserva(error: unknown): string {
  if (error instanceof SinPlazasError || error instanceof YaReservadaError) {
    return error.message;
  }
  return 'No se pudo completar la reserva. Inténtalo de nuevo.';
}
