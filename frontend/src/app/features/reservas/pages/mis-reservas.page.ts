import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { SessionService } from '../../../core/auth/session.service';
import { ClaseService } from '../../../services/clase.service';
import { ReservaService } from '../../../services/reserva.service';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { ToastComponent } from '../../../shared/components/toast.component';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmTabsImports } from '@spartan-ng/helm/tabs';
import { esPasada, formatearFechaHora } from '../../../shared/format/fecha';
import { Clase } from '../../../shared/models/clase.model';

interface FilaReserva {
  readonly id_reserva: number;
  readonly nombre: string;
  readonly fecha: string;
  readonly horario: string;
}

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

@Component({
  selector: 'app-mis-reservas',
  imports: [ConfirmDialogComponent, RouterLink, ToastComponent, HlmButtonImports, HlmCardImports, HlmTabsImports],
  template: `
    <h1 class="mb-4 text-3xl font-semibold">Mis reservas</h1>

    <hlm-tabs class="mb-4 block" [tab]="pestana()" (tabActivated)="pestana.set($any($event))">
      <hlm-tabs-list aria-label="Reservas">
        <button hlmTabsTrigger="proximas">Próximas</button>
        <button hlmTabsTrigger="pasadas">Pasadas</button>
      </hlm-tabs-list>
    </hlm-tabs>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando reservas…</p>
    } @else if (visibles().length === 0) {
      <p class="text-sm text-muted-foreground">
        @if (pestana() === 'proximas') {
          Aún no tienes reservas. <a class="font-semibold text-primary" routerLink="/portal/clases">Ver clases</a>
        } @else {
          No tienes clases pasadas.
        }
      </p>
    } @else {
      <ul class="grid list-none gap-3 p-0">
        @for (fila of visibles(); track fila.id_reserva) {
          <li hlmCard class="flex-row items-center justify-between gap-4 p-4">
            <div>
              <p class="font-semibold">{{ fila.nombre }}</p>
              <p class="text-sm text-muted-foreground">{{ fila.fecha }}</p>
            </div>
            @if (pestana() === 'proximas') {
              <button hlmBtn variant="destructive" size="sm" type="button" (click)="pendiente.set(fila)">Cancelar reserva</button>
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
  protected readonly aviso = signal<Aviso | null>(null);

  protected readonly visibles = computed(() =>
    this.pestana() === 'proximas' ? this.filas().proximas : this.filas().pasadas,
  );

  constructor() {
    void this.cargar();
  }

  protected async cancelar(fila: FilaReserva): Promise<void> {
    this.pendiente.set(null);
    this.aviso.set(null);
    try {
      await this.reservas.cancelar(fila.id_reserva);
      this.aviso.set({ mensaje: 'Reserva cancelada', tipo: 'exito' });
      await this.cargar();
    } catch {
      this.aviso.set({ mensaje: 'No se pudo cancelar la reserva. Inténtalo de nuevo.', tipo: 'error' });
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
