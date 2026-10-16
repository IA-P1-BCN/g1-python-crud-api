import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { authInterceptor } from '../core/http/auth.interceptor';
import { HttpReservaService } from './http-reserva.service';
import {
  ReservaRechazadaError,
  ReservaService,
  SinPlazasError,
  YaReservadaError,
} from './reserva.service';

describe('HttpReservaService', () => {
  let servicio: ReservaService;
  let http: HttpTestingController;

  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        { provide: ReservaService, useClass: HttpReservaService },
      ],
    });
    servicio = TestBed.inject(ReservaService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('listarPorClase filtra por id_clase y pagina', async () => {
    const promesa = servicio.listarPorClase(4);
    const req = http.expectOne((r) => r.url === '/v1/reservas');
    expect(req.request.params.get('id_clase')).toBe('4');
    expect(req.request.params.get('limit')).toBe('100');
    req.flush([{ id_reserva: 1, id_cliente: 2, id_clase: 4, asistio: false, fecha_reserva: 'x' }]);

    await expect(promesa).resolves.toHaveLength(1);
  });

  it('listarDeCliente filtra por id_cliente', async () => {
    const promesa = servicio.listarDeCliente(9);
    const req = http.expectOne((r) => r.url === '/v1/reservas');
    expect(req.request.params.get('id_cliente')).toBe('9');
    req.flush([]);

    await expect(promesa).resolves.toEqual([]);
  });

  it('crear envía asistio=false y devuelve la reserva', async () => {
    const promesa = servicio.crear(1, 2);
    const req = http.expectOne({ method: 'POST', url: '/v1/reservas' });
    expect(req.request.body).toEqual({ id_cliente: 1, id_clase: 2, asistio: false });
    req.flush({ id_reserva: 10, id_cliente: 1, id_clase: 2, asistio: false, fecha_reserva: 'x' }, {
      status: 201,
      statusText: 'Created',
    });

    await expect(promesa).resolves.toMatchObject({ id_reserva: 10 });
  });

  it.each([
    ['La clase no tiene plazas disponibles', SinPlazasError],
    ['El cliente ya tiene una reserva para esta clase', YaReservadaError],
    ['Solo los clientes activos pueden reservar', ReservaRechazadaError],
    ['El cliente debe tener al menos un pago registrado', ReservaRechazadaError],
  ])('409 "%s" se traduce al error de la interfaz', async (detalle, esperado) => {
    const promesa = servicio.crear(1, 2);
    http
      .expectOne({ method: 'POST', url: '/v1/reservas' })
      .flush({ detail: detalle }, { status: 409, statusText: 'Conflict' });

    await expect(promesa).rejects.toBeInstanceOf(esperado);
  });

  it('cancelar hace DELETE de la reserva', async () => {
    const promesa = servicio.cancelar(5);
    http.expectOne({ method: 'DELETE', url: '/v1/reservas/5' }).flush(null, {
      status: 204,
      statusText: 'No Content',
    });

    await expect(promesa).resolves.toBeUndefined();
  });
});
