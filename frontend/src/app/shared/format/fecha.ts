/**
 * La API guarda `horario` como UTC sin sufijo de zona: se formatea en UTC
 * para mostrar la misma hora que se guardó.
 */
export function formatearFechaHora(horarioIso: string): string {
  const fecha = new Date(`${horarioIso}Z`);
  const dia = new Intl.DateTimeFormat('es-ES', {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
    timeZone: 'UTC',
  }).format(fecha);
  const hora = new Intl.DateTimeFormat('es-ES', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
  }).format(fecha);
  return `${dia} · ${hora}`;
}

/** Indica si una clase ya ha ocurrido respecto a `ahora`. */
export function esPasada(horarioIso: string, ahora: Date = new Date()): boolean {
  return new Date(`${horarioIso}Z`).getTime() < ahora.getTime();
}
