import { Component, input, output } from '@angular/core';
import { RouterLink } from '@angular/router';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { ClaseConCupo } from '../models/clase.model';
import { formatearFechaHora } from '../format/fecha';
import { CupoBarComponent } from './cupo-bar.component';

@Component({
  selector: 'app-clase-card',
  imports: [RouterLink, CupoBarComponent, HlmButtonImports, HlmCardImports],
  template: `
    <article hlmCard class="gap-3 p-4">
      <div hlmCardHeader>
        <h2 hlmCardTitle>
          <a class="text-inherit no-underline" [routerLink]="['/marketplace/clases', item().clase.id_clase]">
            {{ item().clase.nombre_clase }}
          </a>
        </h2>
      </div>
      <div hlmCardContent class="flex flex-col gap-2">
        <p class="text-sm text-muted-foreground">{{ fecha }}</p>
        <p class="text-sm text-muted-foreground">Entrenador: {{ item().entrenador }}</p>
        <app-cupo-bar [plazasLibres]="item().plazasLibres" [capacidad]="item().clase.capacidad_max" />

        @if (item().reservadaPorMi) {
          <p class="font-semibold text-green-700">Ya reservada</p>
        } @else if (item().plazasLibres === 0) {
          <p class="font-semibold text-muted-foreground">Completa</p>
        } @else {
          <button hlmBtn class="w-full" type="button" (click)="reservar.emit(item().clase.id_clase)">Reservar</button>
        }
      </div>
    </article>
  `,
})
export class ClaseCardComponent {
  readonly item = input.required<ClaseConCupo>();
  readonly reservar = output<number>();

  protected get fecha(): string {
    return formatearFechaHora(this.item().clase.horario);
  }
}
