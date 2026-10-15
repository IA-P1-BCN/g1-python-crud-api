import { Injectable } from '@angular/core';
import { AuthService, UsuarioAutenticado } from './auth.service';
import { InvalidCredentialsError, NetworkError } from './auth.errors';

interface UsuarioDePrueba {
  readonly password: string;
  readonly usuario: UsuarioAutenticado;
}

/**
 * Datos ficticios solo para desarrollo, hasta que #55 esté disponible en main.
 * No son credenciales reales ni deben usarse fuera de desarrollo.
 */
const USUARIOS_DE_PRUEBA: Readonly<Record<string, UsuarioDePrueba>> = {
  'cliente@gym.test': {
    password: 'cliente123',
    usuario: { id: 'mock-1', email: 'cliente@gym.test', rol: 'cliente' },
  },
  'staff@gym.test': {
    password: 'staff123',
    usuario: { id: 'mock-2', email: 'staff@gym.test', rol: 'staff' },
  },
};

/** Correo que simula un fallo de conexión, para probar ese estado a mano. */
const CORREO_SIMULA_RED_CAIDA = 'sin-red@gym.test';

/** Retardo artificial para que los estados de carga sean visibles en desarrollo. */
const RETARDO_MS = 400;

@Injectable()
export class MockAuthService extends AuthService {
  async login(email: string, password: string): Promise<UsuarioAutenticado> {
    await new Promise((resolve) => setTimeout(resolve, RETARDO_MS));

    const correo = email.trim().toLowerCase();
    if (correo === CORREO_SIMULA_RED_CAIDA) {
      throw new NetworkError();
    }

    const prueba = USUARIOS_DE_PRUEBA[correo];
    if (!prueba || prueba.password !== password) {
      throw new InvalidCredentialsError();
    }
    return prueba.usuario;
  }
}
