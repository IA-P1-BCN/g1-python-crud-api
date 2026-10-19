import { Component, computed, input } from '@angular/core';
import { NgIcon } from '@ng-icons/core';
import { HlmBadgeImports } from '@spartan-ng/helm/badge';
import { EstadoMembresia } from '../models/cliente.model';

type VarianteBadge = 'default' | 'secondary' | 'destructive';

const VARIANTES: Record<EstadoMembresia, VarianteBadge> = {
  Activo: 'default',
  Inactivo: 'secondary',
  Suspendido: 'destructive',
};

const ICONOS: Record<EstadoMembresia, string> = {
  Activo: 'lucideCircleCheck',
  Inactivo: 'lucideMinusCircle',
  Suspendido: 'lucideTriangleAlert',
};

/** Estado de membresía con el badge de Spartan (texto siempre visible). */
@Component({
  selector: 'app-estado-badge',
  imports: [NgIcon, HlmBadgeImports],
  template: `<span hlmBadge [variant]="variante()" class="gap-1">
    <ng-icon [name]="icono()" class="text-[length:--spacing(3)]" />{{ estado() }}
  </span>`,
})
export class EstadoBadgeComponent {
  readonly estado = input.required<EstadoMembresia>();
  protected readonly variante = computed(() => VARIANTES[this.estado()]);
  protected readonly icono = computed(() => ICONOS[this.estado()]);
}
