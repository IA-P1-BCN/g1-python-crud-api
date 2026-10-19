import { toastState } from '@spartan-ng/brain/sonner';

/**
 * Mensajes en la cola global de sonner. El `<hlm-toaster/>` vive en `app.html`,
 * así que en los tests de página aislados el aviso solo queda en este estado.
 * El mensaje se guarda en `title` (ver create() de brain/sonner).
 */
export function mensajesDeToast(): string[] {
  return toastState.toasts().map((t) => String(t.title));
}

/** Vacía la cola de toasts (el estado es global y se comparte entre tests). */
export function limpiarToasts(): void {
  toastState.dismiss();
}
