import { Component, input } from '@angular/core';
import { HlmAlertImports } from '@spartan-ng/helm/alert';

/** Aviso breve de éxito o error con hlm-alert. El padre decide cuándo mostrarlo. */
@Component({
  selector: 'app-toast',
  imports: [HlmAlertImports],
  template: `
    @if (mensaje()) {
      <div hlmAlert [variant]="tipo() === 'error' ? 'destructive' : 'default'" class="mb-4">
        <p hlmAlertDescription>{{ mensaje() }}</p>
      </div>
    }
  `,
})
export class ToastComponent {
  readonly mensaje = input<string | null>(null);
  readonly tipo = input<'exito' | 'error'>('exito');
}
