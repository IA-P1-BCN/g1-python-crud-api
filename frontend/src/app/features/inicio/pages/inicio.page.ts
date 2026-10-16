import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { SessionService } from '../../../core/auth/session.service';
import { ClaseService } from '../../../services/clase.service';
import { ReservaService } from '../../../services/reserva.service';
import { esPasada, formatearFechaHora } from '../../../shared/format/fecha';
import { Clase } from '../../../shared/models/clase.model';

interface ProximaClase {
  readonly nombre: string;
  readonly fecha: string;
}

@Component({
  selector: 'app-inicio',
  imports: [RouterLink, HlmButtonImports, HlmCardImports],
  template: `
    <h1 class="mb-4 text-3xl font-semibold">Hola, {{ nombre() }}</h1>

    <section class="grid gap-4 sm:grid-cols-2">
      <article hlmCard class="gap-3 p-4">
        <div hlmCardHeader><h2 hlmCardTitle>Próxima clase</h2></div>
        <div hlmCardContent class="flex flex-col gap-1">
          @if (proxima(); as p) {
            <p class="font-semibold">{{ p.nombre }}</p>
            <p class="text-sm text-muted-foreground">{{ p.fecha }}</p>
          } @else {
            <p class="text-sm text-muted-foreground">No tienes clases reservadas.</p>
          }
        </div>
      </article>

      <article hlmCard class="gap-3 p-4">
        <div hlmCardHeader><h2 hlmCardTitle>Clases</h2></div>
        <div hlmCardContent class="flex flex-col items-start gap-3">
          <p class="text-sm text-muted-foreground">Consulta las plazas libres y reserva tu sitio.</p>
          <a hlmBtn routerLink="/portal/clases">Ver clases</a>
        </div>
      </article>
    </section>
  `,
})
export class InicioPage {
  private readonly session = inject(SessionService);
  private readonly clases = inject(ClaseService);
  private readonly reservas = inject(ReservaService);

  protected readonly nombre = computed(() => this.session.usuario()?.nombre.split(' ')[0] ?? '');
  protected readonly proxima = signal<ProximaClase | null>(null);

  constructor() {
    void this.cargar();
  }

  private async cargar(): Promise<void> {
    const idCliente = this.session.idCliente();
    if (idCliente === null) {
      return;
    }
    const [reservas, clases] = await Promise.all([
      this.reservas.listarDeCliente(idCliente),
      this.clases.listar(),
    ]);
    const proximas = reservas
      .map((r) => clases.find((c) => c.id_clase === r.id_clase))
      .filter((c): c is Clase => c !== undefined && !esPasada(c.horario))
      .sort((a, b) => a.horario.localeCompare(b.horario));

    const primera = proximas[0];
    this.proxima.set(
      primera ? { nombre: primera.nombre_clase, fecha: formatearFechaHora(primera.horario) } : null,
    );
  }
}
