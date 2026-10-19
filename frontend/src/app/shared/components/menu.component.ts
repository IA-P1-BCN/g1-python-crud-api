import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { SessionService } from '../../core/auth/session.service';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmDropdownMenuImports } from '@spartan-ng/helm/dropdown-menu';

/** Botón de menú con dropdown de Spartan: por rol (marketplace, staff, admin). */
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
          @if (usuario.rol === 'admin') {
            <a hlmDropdownMenuItem routerLink="/perfil">Mi perfil</a>
            <div hlmDropdownMenuLabel>Admin</div>
            <a hlmDropdownMenuItem routerLink="/admin">Dashboard</a>
            <a hlmDropdownMenuItem routerLink="/admin/clientes">Clientes</a>
            <a hlmDropdownMenuItem routerLink="/admin/entrenadores">Entrenadores</a>
            <a hlmDropdownMenuItem routerLink="/admin/clases">Clases</a>
            <a hlmDropdownMenuItem routerLink="/admin/pagos">Pagos</a>
            <a hlmDropdownMenuItem routerLink="/admin/cuentas">Cuentas</a>
            <a hlmDropdownMenuItem routerLink="/admin/export">Exportar CSV</a>
          } @else {
            <a hlmDropdownMenuItem routerLink="/marketplace">Catálogo</a>
            <a hlmDropdownMenuItem routerLink="/marketplace/mis-reservas">Mis reservas</a>
            <a hlmDropdownMenuItem routerLink="/perfil">Mi perfil</a>
            @if (usuario.rol === 'staff') {
              <div hlmDropdownMenuLabel>Staff</div>
              <a hlmDropdownMenuItem routerLink="/staff">Mi panel</a>
              <a hlmDropdownMenuItem routerLink="/staff/clases">Mis clases</a>
              <a hlmDropdownMenuItem routerLink="/staff/reservas">Reservas de mis clases</a>
            }
          }
          <div hlmDropdownMenuSeparator></div>
          <button hlmDropdownMenuItem variant="destructive" type="button" (triggered)="cerrarSesion()">
            Cerrar sesión
          </button>
        } @else {
          <a hlmDropdownMenuItem routerLink="/auth/login">Iniciar sesión</a>
          <a hlmDropdownMenuItem routerLink="/auth/registro">Crear cuenta</a>
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
    void this.router.navigateByUrl('/auth/login');
  }
}
