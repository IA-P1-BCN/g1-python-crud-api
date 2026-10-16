import { SinPlazasError, YaReservadaError } from '../reserva.service';
import { ID_ANA } from './datos-mock';
import { MockReservaService } from './mock-reserva.service';

describe('MockReservaService', () => {
  let servicio: MockReservaService;

  beforeEach(() => {
    servicio = new MockReservaService();
  });

  it('cuenta las reservas iniciales por clase (Yoga 9, Zumba 0)', async () => {
    expect((await servicio.listarPorClase(1)).length).toBe(9);
    expect((await servicio.listarPorClase(4)).length).toBe(0);
  });

  it('crea una reserva y la añade al listado del socio', async () => {
    const antes = (await servicio.listarDeCliente(ID_ANA)).length;
    await servicio.crear(ID_ANA, 4);
    expect((await servicio.listarDeCliente(ID_ANA)).length).toBe(antes + 1);
  });

  it('rechaza reservar una clase completa (Pilates 3 con 10 de 10)', async () => {
    await expect(servicio.crear(ID_ANA, 3)).rejects.toBeInstanceOf(SinPlazasError);
  });

  it('rechaza una segunda reserva en la misma clase', async () => {
    await expect(servicio.crear(ID_ANA, 1)).rejects.toBeInstanceOf(YaReservadaError);
  });

  it('cancelar libera la plaza', async () => {
    const mias = await servicio.listarDeCliente(ID_ANA);
    const yoga = mias.find((r) => r.id_clase === 1);
    expect(yoga).toBeDefined();
    await servicio.cancelar(yoga!.id_reserva);
    expect((await servicio.listarPorClase(1)).length).toBe(8);
  });
});
