import { Component, computed, input } from '@angular/core';
import { HlmBadgeImports } from '@spartan-ng/helm/badge';
import { EstadoMembresia } from '../models/cliente.model';

type VarianteBadge = 'default' | 'secondary' | 'destructive';

const VARIANTES: Record<EstadoMembresia, VarianteBadge> = {
  Activo: 'default',
  Inactivo: 'secondary',
  Suspendido: 'destructive',
};

/** Estado de membresía con el badge de Spartan (texto siempre visible). */
@Component({
  selector: 'app-estado-badge',
  imports: [HlmBadgeImports],
  template: `<span hlmBadge [variant]="variante()">{{ estado() }}</span>`,
})
export class EstadoBadgeComponent {
  readonly estado = input.required<EstadoMembresia>();
  protected readonly variante = computed(() => VARIANTES[this.estado()]);
}
