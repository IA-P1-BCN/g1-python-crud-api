import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { NgIcon } from '@ng-icons/core';
import { toast } from '@spartan-ng/brain/sonner';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmSkeletonImports } from '@spartan-ng/helm/skeleton';
import { SessionService } from '../../../core/auth/session.service';
import { ClaseService } from '../../../services/clase.service';
import { ReservaService, SinPlazasError, YaReservadaError } from '../../../services/reserva.service';
import { textoDeError } from '../../../core/http/peticion';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { CupoBarComponent } from '../../../shared/components/cupo-bar.component';
import { formatearFechaHora } from '../../../shared/format/fecha';
import { Clase, CupoClase } from '../../../shared/models/clase.model';

/** Detalle de una clase con plazas disponibles y reserva (como space-detail de la referencia). */
@Component({
  selector: 'app-clase-detalle',
  imports: [RouterLink, ConfirmDialogComponent, CupoBarComponent, NgIcon, HlmButtonImports, HlmCardImports, HlmSkeletonImports],
  template: `
    <a class="mb-4 inline-block text-sm text-primary" routerLink="/marketplace/resultados">← Volver al catálogo</a>

    @if (cargando()) {
      <article hlmCard class="max-w-2xl gap-3 p-6">
        <div hlmCardHeader><div hlmSkeleton class="h-8 w-64"></div></div>
        <div hlmCardContent class="flex flex-col gap-3">
          <div hlmSkeleton class="h-4 w-48"></div>
          <div hlmSkeleton class="h-4 w-40"></div>
          <div hlmSkeleton class="h-2 w-full"></div>
          <div hlmSkeleton class="h-9 w-36"></div>
        </div>
      </article>
    } @else if (clase() === null) {
      <p class="text-sm text-muted-foreground">No se pudo cargar la clase.</p>
    } @else {
      <article hlmCard class="max-w-2xl gap-3 p-6">
        <div hlmCardHeader>
          <h1 class="inline-flex items-center gap-2 text-3xl font-semibold"><ng-icon name="lucideCalendar" class="text-[length:--spacing(6)]" />{{ clase()!.nombre_clase }}</h1>
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
              <button hlmBtn class="gap-1.5" type="button" (click)="confirmar.set(true)"><ng-icon name="lucideCalendarCheck" class="text-[length:--spacing(4)]" />Reservar plaza</button>
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
      toast.error('Tu cuenta no tiene ficha de socio');
      return;
    }
    try {
      await this.reservas.crear(idCliente, c.id_clase);
      toast.success('Reserva confirmada');
      this.reservadaPorMi.set(true);
      this.cupo.set(await this.clases.cupo(c.id_clase));
    } catch (error) {
      toast.error(mensajeDe(error));
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
