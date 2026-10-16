import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MenuComponent } from './menu.component';

/** Shell del portal (layout): cabecera en escritorio, barra inferior en móvil. */
@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, MenuComponent],
  template: `
    <header class="cabecera flex items-center gap-6 bg-background px-6 py-2 shadow-sm">
      <a class="logo text-xl font-bold text-primary no-underline" routerLink="/">GymFlow</a>
      <nav class="enlaces flex flex-1 gap-4" aria-label="Principal">
        <a routerLink="/" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }">Inicio</a>
        <a routerLink="/clases" routerLinkActive="activo">Clases</a>
        <a routerLink="/reservas" routerLinkActive="activo">Mis reservas</a>
      </nav>
      <app-menu />
    </header>

    <main class="contenido">
      <router-outlet />
    </main>

    <nav class="barra-inferior" aria-label="Principal móvil">
      <a routerLink="/" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }">Inicio</a>
      <a routerLink="/clases" routerLinkActive="activo">Clases</a>
      <a routerLink="/reservas" routerLinkActive="activo">Reservas</a>
    </nav>
  `,
  styleUrl: './app-shell.component.css',
})
export class AppShellComponent {}
