import { Component, inject, signal } from '@angular/core';
import { NgIcon } from '@ng-icons/core';
import { toast } from '@spartan-ng/brain/sonner';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { textoDeError } from '../../../core/http/peticion';
import { ExportApi, TablaExportable } from '../../../services/api/recursos.api';
import { descargarArchivo } from '../../../shared/format/descargar';

const TABLAS: readonly { valor: TablaExportable; etiqueta: string }[] = [
  { valor: 'clientes', etiqueta: 'Clientes' },
  { valor: 'entrenadores', etiqueta: 'Entrenadores' },
  { valor: 'clases', etiqueta: 'Clases' },
  { valor: 'reservas', etiqueta: 'Reservas' },
  { valor: 'pagos', etiqueta: 'Pagos' },
];

/** Descarga de tablas en CSV con GET /v1/export/csv?tablas=. */
@Component({
  selector: 'app-export',
  imports: [NgIcon, HlmButtonImports, HlmCardImports],
  template: `
    <h1 class="mb-4 inline-flex items-center gap-2 text-3xl font-semibold"><ng-icon name="lucideDownload" class="text-[length:--spacing(6)]" />Exportar datos</h1>

    <section hlmCard class="max-w-2xl p-4">
      <p class="mb-4 text-sm text-muted-foreground">
        Descarga el CSV completo de una tabla (sin filtros, ordenado por ID), igual que
        <code>GET /v1/export/csv</code>.
      </p>
      <div class="flex flex-wrap gap-3">
        @for (tabla of tablas; track tabla.valor) {
          <button hlmBtn class="gap-1.5" type="button" variant="secondary" [disabled]="exportando() === tabla.valor" (click)="exportar(tabla.valor)">
            @if (exportando() === tabla.valor) {
              Descargando…
            } @else {
              <ng-icon name="lucideDownload" class="text-[length:--spacing(4)]" />
              Descargar {{ tabla.etiqueta }}
            }
          </button>
        }
      </div>
    </section>
  `,
})
export class ExportPage {
  private readonly api = inject(ExportApi);

  protected readonly tablas = TABLAS;
  protected readonly exportando = signal<TablaExportable | null>(null);

  protected async exportar(tabla: TablaExportable): Promise<void> {
    if (this.exportando() !== null) {
      return;
    }
    this.exportando.set(tabla);
    try {
      const csv = await this.api.exportarCsv(tabla);
      descargarArchivo(`${tabla}.csv`, csv, 'text/csv');
      toast.success(`Descarga de ${tabla} completada`);
    } catch (error) {
      toast.error(textoDeError(error));
    } finally {
      this.exportando.set(null);
    }
  }
}
