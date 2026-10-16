import { esPasada, formatearFechaHora } from './fecha';

describe('fecha', () => {
  it('muestra la hora guardada en UTC sin desplazarla', () => {
    expect(formatearFechaHora('2026-10-20T09:00:00')).toContain('09:00');
  });

  it('distingue clases pasadas de futuras', () => {
    const ahora = new Date('2026-10-15T12:00:00Z');
    expect(esPasada('2026-10-10T18:00:00', ahora)).toBe(true);
    expect(esPasada('2026-10-20T09:00:00', ahora)).toBe(false);
  });
});
