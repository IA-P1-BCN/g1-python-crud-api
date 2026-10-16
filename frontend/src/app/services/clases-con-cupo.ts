import { ClaseConCupo } from '../shared/models/clase.model';
import { Reserva } from '../shared/models/reserva.model';
import { ClaseService } from './clase.service';
import { ReservaService } from './reserva.service';

/**
 * Clases con plazas libres (capacidad menos reservas). Si hay socio, marca las
 * clases que ya tiene reservadas; sin socio (visitante), ninguna.
 */
export async function cargarClasesConCupo(
  clases: ClaseService,
  reservas: ReservaService,
  idCliente: number | null,
): Promise<ClaseConCupo[]> {
  const mias: Promise<Reserva[]> =
    idCliente === null ? Promise.resolve([]) : reservas.listarDeCliente(idCliente);
  const [lista, entrenadores, reservadasPorMi] = await Promise.all([
    clases.listar(),
    clases.listarEntrenadores(),
    mias,
  ]);
  const idsMias = new Set(reservadasPorMi.map((r) => r.id_clase));

  return Promise.all(
    lista.map(async (clase): Promise<ClaseConCupo> => {
      const reservadas = (await reservas.listarPorClase(clase.id_clase)).length;
      return {
        clase,
        entrenador: entrenadores.find((e) => e.id_entrenador === clase.id_entrenador)?.nombre ?? 'Sin asignar',
        plazasLibres: Math.max(clase.capacidad_max - reservadas, 0),
        reservadaPorMi: idsMias.has(clase.id_clase),
      };
    }),
  );
}
