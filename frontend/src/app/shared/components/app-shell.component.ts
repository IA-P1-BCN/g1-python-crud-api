import { Component } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MenuComponent } from './menu.component';

/** Shell del portal (layout): cabecera en escritorio, barra inferior en móvil. */
@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, MenuComponent],
  template: `
    <header class="cabecera flex items-center gap-6 bg-background px-6 py-2 shadow-sm">
      <a class="logo text-xl font-bold text-primary no-underline" routerLink="/marketplace">GymFlow</a>
      <nav class="enlaces flex flex-1 gap-4" aria-label="Principal">
        <a routerLink="/marketplace" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }">Catálogo</a>
        <a routerLink="/marketplace/mis-reservas" routerLinkActive="activo">Mis reservas</a>
        <a routerLink="/perfil" routerLinkActive="activo">Mi perfil</a>
      </nav>
      <app-menu />
    </header>

    <main class="contenido">
      <router-outlet />
    </main>

    <nav class="barra-inferior" aria-label="Principal móvil">
      <a routerLink="/marketplace" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }">Catálogo</a>
      <a routerLink="/marketplace/mis-reservas" routerLinkActive="activo">Reservas</a>
      <a routerLink="/perfil" routerLinkActive="activo">Perfil</a>
    </nav>
  `,
  styleUrl: './app-shell.component.css',
})
export class AppShellComponent {}
