const CLAVE_TOKEN = 'gymflow.token';

/**
 * Token JWT de la sesión. Vive en sessionStorage, igual que la sesión del usuario:
 * se mantiene al recargar la pestaña y se pierde al cerrarla.
 */
function almacenamiento(): Storage | null {
  return typeof sessionStorage === 'undefined' ? null : sessionStorage;
}

export function guardarToken(token: string): void {
  almacenamiento()?.setItem(CLAVE_TOKEN, token);
}

export function leerToken(): string | null {
  return almacenamiento()?.getItem(CLAVE_TOKEN) ?? null;
}

export function borrarToken(): void {
  almacenamiento()?.removeItem(CLAVE_TOKEN);
}
