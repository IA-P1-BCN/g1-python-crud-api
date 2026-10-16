import { Injectable, computed, signal } from '@angular/core';
import { UsuarioAutenticado } from './auth.service';
import { borrarToken } from './token.storage';

const CLAVE_SESION = 'gymflow.sesion';

/**
 * Sesión del usuario autenticado. Se guarda en sessionStorage: se mantiene al
 * recargar la pestaña y se pierde al cerrarla.
 */
@Injectable({ providedIn: 'root' })
export class SessionService {
  private readonly estado = signal<UsuarioAutenticado | null>(leerSesion());

  readonly usuario = this.estado.asReadonly();
  readonly autenticado = computed(() => this.estado() !== null);
  /** Ficha de socio; null sin sesión o si la cuenta no tiene ficha. */
  readonly idCliente = computed(() => this.estado()?.id_cliente ?? null);

  iniciar(usuario: UsuarioAutenticado): void {
    this.estado.set(usuario);
    almacenamiento()?.setItem(CLAVE_SESION, JSON.stringify(usuario));
  }

  /** Borra la sesión y el token JWT de este navegador. */
  cerrar(): void {
    this.estado.set(null);
    almacenamiento()?.removeItem(CLAVE_SESION);
    borrarToken();
  }
}

function almacenamiento(): Storage | null {
  return typeof sessionStorage === 'undefined' ? null : sessionStorage;
}

function leerSesion(): UsuarioAutenticado | null {
  const raw = almacenamiento()?.getItem(CLAVE_SESION);
  if (!raw) {
    return null;
  }
  try {
    const usuario = JSON.parse(raw) as UsuarioAutenticado;
    return typeof usuario.id === 'number' && typeof usuario.nombre === 'string' ? usuario : null;
  } catch {
    return null;
  }
}
