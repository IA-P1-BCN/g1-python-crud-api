import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { NgIcon } from '@ng-icons/core';
import { SessionService } from '../../core/auth/session.service';
import { MenuComponent } from './menu.component';

/**
 * Shell del portal (layout): cabecera en escritorio, barra inferior en móvil.
 * La cabecera muestra los enlaces más usados de cada rol; el resto (perfil,
 * reservas del staff, pagos, cuentas, export…) vive en el menú desplegable.
 */
@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, MenuComponent, NgIcon],
  template: `
    <header class="cabecera flex items-center gap-6 bg-background px-6 py-2 shadow-sm">
      <a class="logo text-xl font-bold text-primary no-underline" routerLink="/marketplace">GymFlow</a>
      <nav class="enlaces flex flex-1 gap-4" aria-label="Principal">
        @switch (session.usuario()?.rol) {
          @case ('admin') {
            <a routerLink="/admin" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }" class="inline-flex items-center gap-1.5">
              <ng-icon name="lucideLayoutDashboard" class="text-[length:--spacing(4)]" />Dashboard
            </a>
            <a routerLink="/admin/clientes" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
              <ng-icon name="lucideUsers" class="text-[length:--spacing(4)]" />Clientes
            </a>
            <a routerLink="/admin/entrenadores" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
              <ng-icon name="lucideDumbbell" class="text-[length:--spacing(4)]" />Entrenadores
            </a>
            <a routerLink="/admin/clases" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
              <ng-icon name="lucideCalendar" class="text-[length:--spacing(4)]" />Clases
            </a>
          }
          @case ('staff') {
            <a routerLink="/staff" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }" class="inline-flex items-center gap-1.5">
              <ng-icon name="lucideLayoutDashboard" class="text-[length:--spacing(4)]" />Mi panel
            </a>
            <a routerLink="/staff/clases" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
              <ng-icon name="lucideCalendar" class="text-[length:--spacing(4)]" />Mis clases
            </a>
          }
          @case ('cliente') {
            <a routerLink="/marketplace" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }" class="inline-flex items-center gap-1.5">
              <ng-icon name="lucideSearch" class="text-[length:--spacing(4)]" />Catálogo
            </a>
            <a routerLink="/marketplace/mis-reservas" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
              <ng-icon name="lucideCalendarCheck" class="text-[length:--spacing(4)]" />Mis reservas
            </a>
          }
        }
      </nav>
      <app-menu />
    </header>

    <main class="contenido">
      <router-outlet />
    </main>

    <nav class="barra-inferior" aria-label="Principal móvil">
      @switch (session.usuario()?.rol) {
        @case ('admin') {
          <a routerLink="/admin" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }" class="inline-flex items-center gap-1.5">
            <ng-icon name="lucideLayoutDashboard" class="text-[length:--spacing(4)]" />Panel
          </a>
          <a routerLink="/admin/clientes" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
            <ng-icon name="lucideUsers" class="text-[length:--spacing(4)]" />Clientes
          </a>
          <a routerLink="/admin/entrenadores" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
            <ng-icon name="lucideDumbbell" class="text-[length:--spacing(4)]" />Entren.
          </a>
          <a routerLink="/admin/clases" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
            <ng-icon name="lucideCalendar" class="text-[length:--spacing(4)]" />Clases
          </a>
        }
        @case ('staff') {
          <a routerLink="/staff" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }" class="inline-flex items-center gap-1.5">
            <ng-icon name="lucideLayoutDashboard" class="text-[length:--spacing(4)]" />Mi panel
          </a>
          <a routerLink="/staff/clases" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
            <ng-icon name="lucideCalendar" class="text-[length:--spacing(4)]" />Mis clases
          </a>
        }
        @case ('cliente') {
          <a routerLink="/marketplace" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }" class="inline-flex items-center gap-1.5">
            <ng-icon name="lucideSearch" class="text-[length:--spacing(4)]" />Catálogo
          </a>
          <a routerLink="/marketplace/mis-reservas" routerLinkActive="activo" class="inline-flex items-center gap-1.5">
            <ng-icon name="lucideCalendarCheck" class="text-[length:--spacing(4)]" />Reservas
          </a>
        }
      }
    </nav>
  `,
  styleUrl: './app-shell.component.css',
})
export class AppShellComponent {
  protected readonly session = inject(SessionService);
}
