import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { SessionService } from '../../../core/auth/session.service';
import { ClaseService } from '../../../services/clase.service';
import { cargarClasesConCupo } from '../../../services/clases-con-cupo';
import { ReservaService } from '../../../services/reserva.service';
import { textoDeError } from '../../../core/http/peticion';
import { ClaseCardComponent } from '../../../shared/components/clase-card.component';
import { ToastComponent } from '../../../shared/components/toast.component';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { ClaseConCupo } from '../../../shared/models/clase.model';
import { mensajeDeReserva } from './home-marketplace.page';

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

/** Resultados del catálogo: buscador `q` y filtro de horario contra GET /v1/clases. */
@Component({
  selector: 'app-resultados',
  imports: [RouterLink, ClaseCardComponent, ToastComponent, HlmButtonImports, HlmInputImports, HlmLabelImports],
  template: `
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-3xl font-semibold">Clases disponibles</h1>
      <a hlmBtn variant="outline" routerLink="/marketplace">Volver al inicio</a>
    </div>

    <form class="mb-4 flex flex-wrap items-end gap-3" (submit)="buscar($event)">
      <label hlmLabel class="flex min-w-48 flex-col items-start gap-1">
        Buscar por nombre
        <input hlmInput type="search" name="q" [value]="q()" (input)="q.set($any($event.target).value)" />
      </label>
      <label hlmLabel class="flex flex-col items-start gap-1">
        Desde (UTC)
        <input hlmInput type="datetime-local" name="desde" [value]="desde()"
               (input)="desde.set($any($event.target).value)" />
      </label>
      <label hlmLabel class="flex flex-col items-start gap-1">
        Hasta (UTC)
        <input hlmInput type="datetime-local" name="hasta" [value]="hasta()"
               (input)="hasta.set($any($event.target).value)" />
      </label>
      <button hlmBtn type="submit">Buscar</button>
      <button hlmBtn type="button" variant="ghost" (click)="limpiar()">Limpiar</button>
    </form>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando clases…</p>
    } @else if (items().length === 0) {
      <p class="text-sm text-muted-foreground">No hay clases que coincidan con la búsqueda.</p>
    } @else {
      <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        @for (item of items(); track item.clase.id_clase) {
          <app-clase-card [item]="item" (reservar)="reservar($event)" />
        }
      </section>
      <p class="mt-2 text-sm text-muted-foreground">{{ items().length }} clases</p>
    }
  `,
})
export class ResultadosPage {
  private readonly clases = inject(ClaseService);
  private readonly reservas = inject(ReservaService);
  private readonly session = inject(SessionService);
  private readonly ruta = inject(ActivatedRoute);

  protected readonly cargando = signal(true);
  protected readonly items = signal<ClaseConCupo[]>([]);
  protected readonly aviso = signal<Aviso | null>(null);
  protected readonly q = signal('');
  protected readonly desde = signal('');
  protected readonly hasta = signal('');

  protected readonly filtros = computed(() => {
    const filtros: Record<string, string> = {};
    const texto = this.q().trim();
    if (texto) filtros['q'] = texto;
    if (this.desde()) filtros['horario_desde'] = `${this.desde()}:00`;
    if (this.hasta()) filtros['horario_hasta'] = `${this.hasta()}:00`;
    return filtros;
  });

  constructor() {
    this.q.set(this.ruta.snapshot.queryParamMap.get('q') ?? '');
    void this.cargar();
  }

  protected buscar(evento: Event): void {
    evento.preventDefault();
    void this.cargar();
  }

  protected limpiar(): void {
    this.q.set('');
    this.desde.set('');
    this.hasta.set('');
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
    try {
      this.items.set(
        await cargarClasesConCupo(this.clases, this.reservas, this.session.idCliente(), this.filtros()),
      );
      this.aviso.set(null);
    } catch (error) {
      this.items.set([]);
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    } finally {
      this.cargando.set(false);
    }
  }
}
