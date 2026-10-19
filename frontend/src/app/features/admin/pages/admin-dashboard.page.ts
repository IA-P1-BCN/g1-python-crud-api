import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { toast } from '@spartan-ng/brain/sonner';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmSkeletonImports } from '@spartan-ng/helm/skeleton';
import { textoDeError } from '../../../core/http/peticion';
import {
  ClientesApi,
  EntrenadoresApi,
  ReservasApi,
} from '../../../services/api/recursos.api';
import { ClaseService } from '../../../services/clase.service';
import { BarrasChartComponent, BarraDato } from '../../../shared/components/barras-chart.component';

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

/**
 * Dashboard del admin: gráficas calculadas en cliente con los listados reales.
 * Los listados se limitan a 100 por página de la API (documentado en la UI).
 */
@Component({
  selector: 'app-admin-dashboard',
  imports: [RouterLink, BarrasChartComponent, HlmButtonImports, HlmCardImports, HlmSkeletonImports],
  template: `
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-3xl font-semibold">Dashboard</h1>
      <a hlmBtn variant="outline" routerLink="/admin/cuentas">Gestionar cuentas</a>
    </div>

    <p class="mb-4 text-sm text-muted-foreground">
      Datos reales de la API (hasta 100 registros por listado). Reservas:
      {{ totalReservas() }} · Clientes: {{ totalClientes() }} · Entrenadores: {{ totalEntrenadores() }}
      · Clases: {{ totalClases() }}
    </p>

    @if (cargando()) {
      <section class="grid gap-4 lg:grid-cols-2">
        @for (tarjeta of [1, 2, 3, 4]; track tarjeta) {
          <article hlmCard class="gap-3 p-4">
            <div hlmCardHeader><div hlmSkeleton class="h-6 w-48"></div></div>
            <div hlmCardContent><div hlmSkeleton class="h-48 w-full"></div></div>
          </article>
        }
      </section>
    } @else {
      <section class="grid gap-4 lg:grid-cols-2">
        <article hlmCard class="gap-3 p-4">
          <div hlmCardHeader><h2 hlmCardTitle>Reservas por mes</h2></div>
          <div hlmCardContent>
            <app-barras-chart [datos]="porMes()" />
          </div>
        </article>
        <article hlmCard class="gap-3 p-4">
          <div hlmCardHeader><h2 hlmCardTitle>Asistencia</h2></div>
          <div hlmCardContent>
            <app-barras-chart [datos]="porAsistencia()" />
          </div>
        </article>
        <article hlmCard class="gap-3 p-4">
          <div hlmCardHeader><h2 hlmCardTitle>Clientes vs entrenadores</h2></div>
          <div hlmCardContent>
            <app-barras-chart [datos]="porRolNegocio()" />
          </div>
        </article>
        <article hlmCard class="gap-3 p-4">
          <div hlmCardHeader><h2 hlmCardTitle>Clases por entrenador</h2></div>
          <div hlmCardContent>
            <app-barras-chart [datos]="porEntrenador()" />
          </div>
        </article>
      </section>
    }
  `,
})
export class AdminDashboardPage {
  private readonly reservasApi = inject(ReservasApi);
  private readonly clientesApi = inject(ClientesApi);
  private readonly entrenadoresApi = inject(EntrenadoresApi);
  private readonly clases = inject(ClaseService);

  protected readonly cargando = signal(true);
  protected readonly totalReservas = signal(0);
  protected readonly totalClientes = signal(0);
  protected readonly totalEntrenadores = signal(0);
  protected readonly totalClases = signal(0);
  protected readonly porMes = signal<BarraDato[]>([]);
  protected readonly porAsistencia = signal<BarraDato[]>([]);
  protected readonly porRolNegocio = signal<BarraDato[]>([]);
  protected readonly porEntrenador = signal<BarraDato[]>([]);

  constructor() {
    void this.cargar();
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    try {
      const [reservas, clientes, entrenadores, clases] = await Promise.all([
        this.reservasApi.listar(),
        this.clientesApi.listar(),
        this.entrenadoresApi.listar(),
        this.clases.listar(),
      ]);
      this.totalReservas.set(reservas.length);
      this.totalClientes.set(clientes.length);
      this.totalEntrenadores.set(entrenadores.length);
      this.totalClases.set(clases.length);

      const meses = new Map<string, number>();
      for (const r of reservas) {
        const clave = r.fecha_reserva.slice(0, 7);
        meses.set(clave, (meses.get(clave) ?? 0) + 1);
      }
      this.porMes.set(
        [...meses.entries()]
          .sort(([a], [b]) => a.localeCompare(b))
          .slice(-12)
          .map(([clave, valor]) => ({ etiqueta: etiquetaMes(clave), valor })),
      );

      const asistidas = reservas.filter((r) => r.asistio).length;
      this.porAsistencia.set([
        { etiqueta: 'Asistidas', valor: asistidas },
        { etiqueta: 'No asistidas', valor: reservas.length - asistidas },
      ]);

      this.porRolNegocio.set([
        { etiqueta: 'Clientes', valor: clientes.length },
        { etiqueta: 'Entrenadores', valor: entrenadores.length },
      ]);

      const porEntrenador = new Map<number, number>();
      for (const c of clases) {
        porEntrenador.set(c.id_entrenador, (porEntrenador.get(c.id_entrenador) ?? 0) + 1);
      }
      this.porEntrenador.set(
        [...porEntrenador.entries()]
          .sort((a, b) => b[1] - a[1])
          .map(([id, valor]) => ({
            etiqueta: entrenadores.find((e) => e.id_entrenador === id)?.nombre ?? `#${id}`,
            valor,
          })),
      );
    } catch (error) {
      toast.error(textoDeError(error));
    } finally {
      this.cargando.set(false);
    }
  }
}

function etiquetaMes(clave: string): string {
  const [anio, mes] = clave.split('-');
  const nombre = MESES[Number(mes) - 1] ?? mes;
  return `${nombre} ${anio.slice(2)}`;
}
