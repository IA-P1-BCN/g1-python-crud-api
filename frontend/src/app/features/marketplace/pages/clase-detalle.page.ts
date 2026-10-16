import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { SessionService } from '../../../core/auth/session.service';
import { ClaseService } from '../../../services/clase.service';
import { ReservaService, SinPlazasError, YaReservadaError } from '../../../services/reserva.service';
import { textoDeError } from '../../../core/http/peticion';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { ToastComponent } from '../../../shared/components/toast.component';
import { CupoBarComponent } from '../../../shared/components/cupo-bar.component';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { formatearFechaHora } from '../../../shared/format/fecha';
import { Clase, CupoClase } from '../../../shared/models/clase.model';

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

/** Detalle de una clase con plazas disponibles y reserva (como space-detail de la referencia). */
@Component({
  selector: 'app-clase-detalle',
  imports: [RouterLink, ConfirmDialogComponent, ToastComponent, CupoBarComponent, HlmButtonImports, HlmCardImports],
  template: `
    <a class="mb-4 inline-block text-sm text-primary" routerLink="/marketplace/resultados">← Volver al catálogo</a>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando clase…</p>
    } @else if (clase() === null) {
      <p class="text-sm text-muted-foreground">No se pudo cargar la clase.</p>
    } @else {
      <article hlmCard class="max-w-2xl gap-3 p-6">
        <div hlmCardHeader>
          <h1 class="text-3xl font-semibold">{{ clase()!.nombre_clase }}</h1>
        </div>
        <div hlmCardContent class="flex flex-col gap-3">
          <p class="text-muted-foreground">Horario (UTC): {{ fecha }}</p>
          <p class="text-muted-foreground">Entrenador: {{ entrenador() }}</p>
          @if (cupo(); as c) {
            <app-cupo-bar [plazasLibres]="c.plazas_disponibles" [capacidad]="c.capacidad_max" />
            <p class="text-sm text-muted-foreground">{{ c.reservas }} de {{ c.capacidad_max }} plazas reservadas</p>
          }
          <div class="flex flex-wrap gap-2">
            @if (reservadaPorMi()) {
              <p class="font-semibold text-green-700">Ya tienes plaza en esta clase</p>
              <a hlmBtn variant="outline" routerLink="/marketplace/mis-reservas">Ver mis reservas</a>
            } @else if ((cupo()?.plazas_disponibles ?? 1) === 0) {
              <p class="font-semibold text-muted-foreground">Clase completa</p>
            } @else {
              <button hlmBtn type="button" (click)="confirmar.set(true)">Reservar plaza</button>
            }
          </div>
        </div>
      </article>
    }

    @if (confirmar()) {
      <app-confirm-dialog
        titulo="Reservar clase"
        [mensaje]="'¿Reservar plaza en ' + clase()?.nombre_clase + '?'"
        textoCancelar="Volver"
        textoConfirmar="Sí, reservar"
        (cancelar)="confirmar.set(false)"
        (confirmar)="reservar()"
      />
    }
  `,
})
export class ClaseDetallePage {
  private readonly clases = inject(ClaseService);
  private readonly reservas = inject(ReservaService);
  private readonly session = inject(SessionService);
  private readonly ruta = inject(ActivatedRoute);
  private readonly router = inject(Router);

  protected readonly cargando = signal(true);
  protected readonly clase = signal<Clase | null>(null);
  protected readonly entrenador = signal('Sin asignar');
  protected readonly cupo = signal<CupoClase | null>(null);
  protected readonly reservadaPorMi = signal(false);
  protected readonly confirmar = signal(false);
  protected readonly aviso = signal<Aviso | null>(null);

  protected get fecha(): string {
    const c = this.clase();
    return c ? formatearFechaHora(c.horario) : '';
  }

  constructor() {
    void this.cargar();
  }

  protected async reservar(): Promise<void> {
    this.confirmar.set(false);
    const c = this.clase();
    const idCliente = this.session.idCliente();
    if (c === null || idCliente === null) {
      this.aviso.set({ mensaje: 'Tu cuenta no tiene ficha de socio', tipo: 'error' });
      return;
    }
    this.aviso.set(null);
    try {
      await this.reservas.crear(idCliente, c.id_clase);
      this.aviso.set({ mensaje: 'Reserva confirmada', tipo: 'exito' });
      this.reservadaPorMi.set(true);
      this.cupo.set(await this.clases.cupo(c.id_clase));
    } catch (error) {
      this.aviso.set({ mensaje: mensajeDe(error), tipo: 'error' });
      this.cupo.set(await this.clases.cupo(c.id_clase).catch(() => null));
    }
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    const id = Number(this.ruta.snapshot.paramMap.get('id'));
    if (!Number.isInteger(id) || id <= 0) {
      this.clase.set(null);
      this.cargando.set(false);
      return;
    }
    try {
      const [clase, entrenadores, cupo] = await Promise.all([
        this.clases.obtener(id),
        this.clases.listarEntrenadores(),
        this.clases.cupo(id),
      ]);
      this.clase.set(clase);
      this.entrenador.set(
        entrenadores.find((e) => e.id_entrenador === clase.id_entrenador)?.nombre ?? 'Sin asignar',
      );
      this.cupo.set(cupo);
      const idCliente = this.session.idCliente();
      if (idCliente !== null) {
        const mias = await this.reservas.listarDeCliente(idCliente);
        this.reservadaPorMi.set(mias.some((r) => r.id_clase === id));
      }
    } catch {
      this.clase.set(null);
    } finally {
      this.cargando.set(false);
    }
  }
}

function mensajeDe(error: unknown): string {
  if (error instanceof SinPlazasError || error instanceof YaReservadaError) {
    return error.message;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return textoDeError(error);
}
