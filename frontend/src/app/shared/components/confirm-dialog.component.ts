import { Component, input, output } from '@angular/core';
import { HlmAlertDialogImports } from '@spartan-ng/helm/alert-dialog';
import { HlmButtonImports } from '@spartan-ng/helm/button';

/**
 * Diálogo de confirmación con alert-dialog de Spartan. Controlado por `abierto`:
 * cualquier cierre (Cancelar, Escape o clic fuera) emite `cancelar`.
 */
@Component({
  selector: 'app-confirm-dialog',
  imports: [HlmAlertDialogImports, HlmButtonImports],
  template: `
    <hlm-alert-dialog [state]="abierto() ? 'open' : 'closed'" (stateChanged)="alCambiar($event)">
      <hlm-alert-dialog-content *hlmAlertDialogPortal="let ctx">
        <hlm-alert-dialog-header>
          <h2 hlmAlertDialogTitle>{{ titulo() }}</h2>
          <p hlmAlertDialogDescription>{{ mensaje() }}</p>
        </hlm-alert-dialog-header>
        <hlm-alert-dialog-footer>
          <button hlmAlertDialogCancel type="button">{{ textoCancelar() }}</button>
          <button hlmAlertDialogAction type="button" variant="destructive" (click)="confirmar.emit()">
            {{ textoConfirmar() }}
          </button>
        </hlm-alert-dialog-footer>
      </hlm-alert-dialog-content>
    </hlm-alert-dialog>
  `,
})
export class ConfirmDialogComponent {
  readonly abierto = input(true);
  readonly titulo = input.required<string>();
  readonly mensaje = input.required<string>();
  readonly textoCancelar = input('Volver');
  readonly textoConfirmar = input('Confirmar');
  readonly confirmar = output<void>();
  readonly cancelar = output<void>();

  protected alCambiar(estado: 'open' | 'closed'): void {
    if (estado === 'closed') {
      this.cancelar.emit();
    }
  }
}
