import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { NgIcon } from '@ng-icons/core';
import { SessionService } from '../../core/auth/session.service';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmDropdownMenuImports } from '@spartan-ng/helm/dropdown-menu';

/** Botón de menú con dropdown de Spartan: por rol (marketplace, staff, admin). */
@Component({
  selector: 'app-menu',
  imports: [RouterLink, NgIcon, HlmButtonImports, HlmDropdownMenuImports],
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
            <a hlmDropdownMenuItem routerLink="/perfil" class="gap-2">
              <ng-icon name="lucideUser" class="text-[length:--spacing(4)]" />Mi perfil
            </a>
            <div hlmDropdownMenuLabel>Admin</div>
            <a hlmDropdownMenuItem routerLink="/admin" class="gap-2">
              <ng-icon name="lucideLayoutDashboard" class="text-[length:--spacing(4)]" />Dashboard
            </a>
            <a hlmDropdownMenuItem routerLink="/admin/clientes" class="gap-2">
              <ng-icon name="lucideUsers" class="text-[length:--spacing(4)]" />Clientes
            </a>
            <a hlmDropdownMenuItem routerLink="/admin/entrenadores" class="gap-2">
              <ng-icon name="lucideDumbbell" class="text-[length:--spacing(4)]" />Entrenadores
            </a>
            <a hlmDropdownMenuItem routerLink="/admin/clases" class="gap-2">
              <ng-icon name="lucideCalendar" class="text-[length:--spacing(4)]" />Clases
            </a>
            <a hlmDropdownMenuItem routerLink="/admin/pagos" class="gap-2">
              <ng-icon name="lucideCreditCard" class="text-[length:--spacing(4)]" />Pagos
            </a>
            <a hlmDropdownMenuItem routerLink="/admin/cuentas" class="gap-2">
              <ng-icon name="lucideUserCog" class="text-[length:--spacing(4)]" />Cuentas
            </a>
            <a hlmDropdownMenuItem routerLink="/admin/export" class="gap-2">
              <ng-icon name="lucideDownload" class="text-[length:--spacing(4)]" />Exportar CSV
            </a>
          } @else {
            <a hlmDropdownMenuItem routerLink="/marketplace" class="gap-2">
              <ng-icon name="lucideSearch" class="text-[length:--spacing(4)]" />Catálogo
            </a>
            <a hlmDropdownMenuItem routerLink="/marketplace/mis-reservas" class="gap-2">
              <ng-icon name="lucideCalendarCheck" class="text-[length:--spacing(4)]" />Mis reservas
            </a>
            <a hlmDropdownMenuItem routerLink="/perfil" class="gap-2">
              <ng-icon name="lucideUser" class="text-[length:--spacing(4)]" />Mi perfil
            </a>
            @if (usuario.rol === 'staff') {
              <div hlmDropdownMenuLabel>Staff</div>
              <a hlmDropdownMenuItem routerLink="/staff" class="gap-2">
                <ng-icon name="lucideLayoutDashboard" class="text-[length:--spacing(4)]" />Mi panel
              </a>
              <a hlmDropdownMenuItem routerLink="/staff/clases" class="gap-2">
                <ng-icon name="lucideCalendar" class="text-[length:--spacing(4)]" />Mis clases
              </a>
              <a hlmDropdownMenuItem routerLink="/staff/reservas" class="gap-2">
                <ng-icon name="lucideClipboardList" class="text-[length:--spacing(4)]" />Reservas de mis clases
              </a>
            }
          }
          <div hlmDropdownMenuSeparator></div>
          <button hlmDropdownMenuItem variant="destructive" type="button" (triggered)="cerrarSesion()" class="gap-2">
            <ng-icon name="lucideLogOut" class="text-[length:--spacing(4)]" />Cerrar sesión
          </button>
        } @else {
          <a hlmDropdownMenuItem routerLink="/auth/login" class="gap-2">
            <ng-icon name="lucideLogIn" class="text-[length:--spacing(4)]" />Iniciar sesión
          </a>
          <a hlmDropdownMenuItem routerLink="/auth/registro" class="gap-2">
            <ng-icon name="lucideUserPlus" class="text-[length:--spacing(4)]" />Crear cuenta
          </a>
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
