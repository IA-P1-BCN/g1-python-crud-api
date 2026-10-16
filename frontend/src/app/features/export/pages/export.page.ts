import { Component, inject, signal } from '@angular/core';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { textoDeError } from '../../../core/http/peticion';
import { ExportApi, TablaExportable } from '../../../services/api/recursos.api';
import { descargarArchivo } from '../../../shared/format/descargar';
import { ToastComponent } from '../../../shared/components/toast.component';

const TABLAS: readonly { valor: TablaExportable; etiqueta: string }[] = [
  { valor: 'clientes', etiqueta: 'Clientes' },
  { valor: 'entrenadores', etiqueta: 'Entrenadores' },
  { valor: 'clases', etiqueta: 'Clases' },
  { valor: 'reservas', etiqueta: 'Reservas' },
  { valor: 'pagos', etiqueta: 'Pagos' },
];

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

/** Descarga de tablas en CSV con GET /v1/export/csv?tablas=. */
@Component({
  selector: 'app-export',
  imports: [ToastComponent, HlmButtonImports, HlmCardImports],
  template: `
    <h1 class="mb-4 text-3xl font-semibold">Exportar datos</h1>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    <section hlmCard class="max-w-2xl p-4">
      <p class="mb-4 text-sm text-muted-foreground">
        Descarga el CSV completo de una tabla (sin filtros, ordenado por ID), igual que
        <code>GET /v1/export/csv</code>.
      </p>
      <div class="flex flex-wrap gap-3">
        @for (tabla of tablas; track tabla.valor) {
          <button hlmBtn type="button" variant="secondary" [disabled]="exportando() === tabla.valor" (click)="exportar(tabla.valor)">
            @if (exportando() === tabla.valor) {
              Descargando…
            } @else {
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
  protected readonly aviso = signal<Aviso | null>(null);

  protected async exportar(tabla: TablaExportable): Promise<void> {
    if (this.exportando() !== null) {
      return;
    }
    this.exportando.set(tabla);
    this.aviso.set(null);
    try {
      const csv = await this.api.exportarCsv(tabla);
      descargarArchivo(`${tabla}.csv`, csv, 'text/csv');
      this.aviso.set({ mensaje: `Descarga de ${tabla} completada`, tipo: 'exito' });
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    } finally {
      this.exportando.set(null);
    }
  }
}
