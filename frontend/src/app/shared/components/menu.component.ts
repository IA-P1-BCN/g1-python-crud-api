import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { SessionService } from '../../core/auth/session.service';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmDropdownMenuImports } from '@spartan-ng/helm/dropdown-menu';

/** Botón de menú con dropdown-menu de Spartan: login o nombre y cerrar sesión. */
@Component({
  selector: 'app-menu',
  imports: [RouterLink, HlmButtonImports, HlmDropdownMenuImports],
  template: `
    <button hlmBtn variant="ghost" size="icon" type="button" aria-label="Abrir menú"
            [hlmDropdownMenuTrigger]="menu">
      <span class="flex w-5 flex-col gap-1" aria-hidden="true">
        <span class="h-0.5 rounded bg-foreground"></span>
        <span class="h-0.5 rounded bg-foreground"></span>
        <span class="h-0.5 rounded bg-foreground"></span>
      </span>
    </button>

    <ng-template #menu>
      <hlm-dropdown-menu class="min-w-52 max-h-[28rem] overflow-y-auto">
        @if (session.usuario(); as usuario) {
          <div hlmDropdownMenuLabel>{{ usuario.nombre }}</div>
          <div hlmDropdownMenuSeparator></div>
          @if (session.idCliente() !== null) {
            <a hlmDropdownMenuItem routerLink="/portal">Mi portal</a>
          }
          <a hlmDropdownMenuItem routerLink="/portal/perfil">Mi perfil</a>
          @if (usuario.rol === 'admin' || usuario.rol === 'staff') {
            <div hlmDropdownMenuLabel>Gestión</div>
            <a hlmDropdownMenuItem routerLink="/portal/gestion-clases">Clases</a>
            @if (usuario.rol === 'admin') {
              <a hlmDropdownMenuItem routerLink="/portal/clientes">Clientes</a>
              <a hlmDropdownMenuItem routerLink="/portal/entrenadores">Entrenadores</a>
              <a hlmDropdownMenuItem routerLink="/portal/pagos">Pagos</a>
              <a hlmDropdownMenuItem routerLink="/portal/cuentas">Cuentas</a>
              <a hlmDropdownMenuItem routerLink="/portal/export">Exportar CSV</a>
            }
            <div hlmDropdownMenuSeparator></div>
          }
          <button hlmDropdownMenuItem variant="destructive" type="button" (triggered)="cerrarSesion()">
            Cerrar sesión
          </button>
        } @else {
          <a hlmDropdownMenuItem routerLink="/login">Iniciar sesión</a>
          <a hlmDropdownMenuItem routerLink="/registro">Crear cuenta</a>
        }
      </hlm-dropdown-menu>
    </ng-template>
  `,
})
export class MenuComponent {
  protected readonly session = inject(SessionService);
  private readonly router = inject(Router);

  protected cerrarSesion(): void {
    this.session.cerrar();
    void this.router.navigateByUrl('/');
  }
}
