import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideInbox } from '@ng-icons/lucide';
import { toast } from '@spartan-ng/brain/sonner';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmEmptyImports } from '@spartan-ng/helm/empty';
import { HlmSkeletonImports } from '@spartan-ng/helm/skeleton';
import { HlmTabsImports } from '@spartan-ng/helm/tabs';
import { SessionService } from '../../../core/auth/session.service';
import { ClaseService } from '../../../services/clase.service';
import { ReservaService } from '../../../services/reserva.service';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { esPasada, formatearFechaHora } from '../../../shared/format/fecha';
import { Clase } from '../../../shared/models/clase.model';

interface FilaReserva {
  readonly id_reserva: number;
  readonly nombre: string;
  readonly fecha: string;
  readonly horario: string;
}

@Component({
  selector: 'app-mis-reservas',
  imports: [
    ConfirmDialogComponent,
    RouterLink,
    NgIcon,
    HlmButtonImports,
    HlmCardImports,
    HlmEmptyImports,
    HlmSkeletonImports,
    HlmTabsImports,
  ],
  providers: [provideIcons({ lucideInbox })],
  template: `
    <h1 class="mb-4 inline-flex items-center gap-2 text-3xl font-semibold"><ng-icon name="lucideCalendarCheck" class="text-[length:--spacing(6)]" />Mis reservas</h1>

    <hlm-tabs class="mb-4 block" [tab]="pestana()" (tabActivated)="pestana.set($any($event))">
      <hlm-tabs-list aria-label="Reservas">
        <button hlmTabsTrigger="proximas">Próximas</button>
        <button hlmTabsTrigger="pasadas">Pasadas</button>
      </hlm-tabs-list>
    </hlm-tabs>

    @if (cargando()) {
      <ul class="grid list-none gap-3 p-0">
        @for (fila of [1, 2, 3]; track fila) {
          <li hlmCard class="flex-row items-center justify-between gap-4 p-4">
            <div class="flex flex-col gap-2">
              <div hlmSkeleton class="h-5 w-48"></div>
              <div hlmSkeleton class="h-4 w-32"></div>
            </div>
            <div hlmSkeleton class="h-8 w-32"></div>
          </li>
        }
      </ul>
    } @else if (visibles().length === 0) {
      <div hlmEmpty>
        <div hlmEmptyHeader>
          <div hlmEmptyMedia variant="icon"><ng-icon name="lucideInbox" /></div>
          @if (pestana() === 'proximas') {
            <p hlmEmptyTitle>Aún no tienes reservas.</p>
            <p hlmEmptyDescription>
              <a class="font-semibold text-primary" routerLink="/marketplace/resultados">Ver clases</a>
            </p>
          } @else {
            <p hlmEmptyTitle>No tienes clases pasadas.</p>
          }
        </div>
      </div>
    } @else {
      <ul class="grid list-none gap-3 p-0">
        @for (fila of visibles(); track fila.id_reserva) {
          <li hlmCard class="flex-row items-center justify-between gap-4 p-4">
            <div>
              <p class="font-semibold">{{ fila.nombre }}</p>
              <p class="text-sm text-muted-foreground">{{ fila.fecha }}</p>
            </div>
            @if (pestana() === 'proximas') {
              <button hlmBtn class="gap-1.5" variant="destructive" size="sm" type="button" (click)="pendiente.set(fila)"><ng-icon name="lucideX" class="text-[length:--spacing(4)]" />Cancelar reserva</button>
            }
          </li>
        }
      </ul>
    }

    @if (pendiente(); as fila) {
      <app-confirm-dialog
        titulo="Cancelar reserva"
        [mensaje]="'¿Cancelar la reserva de ' + fila.nombre + ' del ' + fila.fecha + '? La plaza quedará libre.'"
        textoCancelar="Volver"
        textoConfirmar="Sí, cancelar"
        (cancelar)="pendiente.set(null)"
        (confirmar)="cancelar(fila)"
      />
    }
  `,
})
export class MisReservasPage {
  private readonly clases = inject(ClaseService);
  private readonly reservas = inject(ReservaService);
  private readonly session = inject(SessionService);

  protected readonly cargando = signal(true);
  protected readonly pestana = signal<'proximas' | 'pasadas'>('proximas');
  protected readonly filas = signal<{ proximas: FilaReserva[]; pasadas: FilaReserva[] }>({
    proximas: [],
    pasadas: [],
  });
  protected readonly pendiente = signal<FilaReserva | null>(null);

  protected readonly visibles = computed(() =>
    this.pestana() === 'proximas' ? this.filas().proximas : this.filas().pasadas,
  );

  constructor() {
    void this.cargar();
  }

  protected async cancelar(fila: FilaReserva): Promise<void> {
    this.pendiente.set(null);
    try {
      await this.reservas.cancelar(fila.id_reserva);
      toast.success('Reserva cancelada');
      await this.cargar();
    } catch {
      toast.error('No se pudo cancelar la reserva. Inténtalo de nuevo.');
    }
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    const idCliente = this.session.idCliente();
    if (idCliente === null) {
      this.filas.set({ proximas: [], pasadas: [] });
      this.cargando.set(false);
      return;
    }
    const [reservas, clases] = await Promise.all([
      this.reservas.listarDeCliente(idCliente),
      this.clases.listar(),
    ]);
    const filas = reservas
      .map((r) => ({ reserva: r, clase: clases.find((c) => c.id_clase === r.id_clase) }))
      .filter((x): x is { reserva: typeof x.reserva; clase: Clase } => x.clase !== undefined)
      .map(({ reserva, clase }) => ({
        id_reserva: reserva.id_reserva,
        nombre: clase.nombre_clase,
        fecha: formatearFechaHora(clase.horario),
        horario: clase.horario,
      }));

    const proximas = filas
      .filter((f) => !esPasada(f.horario))
      .sort((a, b) => a.horario.localeCompare(b.horario));
    const pasadas = filas
      .filter((f) => esPasada(f.horario))
      .sort((a, b) => b.horario.localeCompare(a.horario));

    this.filas.set({ proximas, pasadas });
    this.cargando.set(false);
  }
}
