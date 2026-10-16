import { Component, computed, input } from '@angular/core';
import { HlmProgressImports } from '@spartan-ng/helm/progress';

/** Plazas ocupadas con el progreso de Spartan. Naranja cuando quedan menos de 3. */
@Component({
  selector: 'app-cupo-bar',
  imports: [HlmProgressImports],
  template: `
    <p class="mb-1 text-sm text-muted-foreground">{{ texto() }}</p>
    <hlm-progress [value]="ocupadas()" [max]="capacidad()" [attr.aria-label]="texto()">
      <hlm-progress-indicator [style.background]="pocasPlazas() ? 'var(--color-acento)' : null" />
    </hlm-progress>
  `,
})
export class CupoBarComponent {
  readonly plazasLibres = input.required<number>();
  readonly capacidad = input.required<number>();

  protected readonly ocupadas = computed(() => this.capacidad() - this.plazasLibres());
  protected readonly pocasPlazas = computed(() => this.plazasLibres() > 0 && this.plazasLibres() < 3);

  protected readonly texto = computed(() => {
    const libres = this.plazasLibres();
    return libres === 0 ? 'Completa' : `${libres} de ${this.capacidad()} plazas libres`;
  });
}
