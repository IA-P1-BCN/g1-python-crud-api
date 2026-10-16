import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { authInterceptor } from './core/http/auth.interceptor';
import { AuthService } from './core/auth/auth.service';
import { HttpAuthService } from './core/auth/http-auth.service';
import { ClaseService } from './services/clase.service';
import { HttpClaseService } from './services/http-clase.service';
import { ReservaService } from './services/reserva.service';
import { HttpReservaService } from './services/http-reserva.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    // Los mocks (core/auth/mock-auth.service.ts, services/mock/) quedan solo para tests.
    { provide: AuthService, useClass: HttpAuthService },
    { provide: ClaseService, useClass: HttpClaseService },
    { provide: ReservaService, useClass: HttpReservaService },
  ],
};
