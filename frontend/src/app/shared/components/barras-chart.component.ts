import { input } from '@angular/core';
import { Component } from '@angular/core';

export interface BarraDato {
  readonly etiqueta: string;
  readonly valor: number;
}

/** Gráfica de barras horizontal en CSS puro (sin dependencias de gráficos). */
@Component({
  selector: 'app-barras-chart',
  template: `
    @if (datos().length === 0) {
      <p class="text-sm text-muted-foreground">Sin datos.</p>
    } @else {
      <ul class="flex list-none flex-col gap-2 p-0">
        @for (d of datos(); track d.etiqueta) {
          <li class="grid grid-cols-[8rem_1fr_3rem] items-center gap-2 text-sm">
            <span class="truncate text-muted-foreground">{{ d.etiqueta }}</span>
            <span class="h-4 rounded bg-primary/70" [style.width.%]="ancho(d.valor)"></span>
            <span class="text-right font-semibold">{{ d.valor }}</span>
          </li>
        }
      </ul>
    }
  `,
})
export class BarrasChartComponent {
  readonly datos = input.required<BarraDato[]>();

  protected ancho(valor: number): number {
    const max = Math.max(...this.datos().map((d) => d.valor), 1);
    return Math.max(4, Math.round((valor / max) * 100));
  }
}
