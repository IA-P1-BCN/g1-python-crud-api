import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { cargarClasesConCupo } from './clases-con-cupo';
import { ClaseService } from './clase.service';
import { HttpClaseService } from './http-clase.service';
import { HttpReservaService } from './http-reserva.service';
import { ReservaService } from './reserva.service';

describe('Cupo con reservas privadas', () => {
  it('usa la ocupación agregada aunque el cliente solo vea su reserva', async () => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(), provideHttpClientTesting(),
        { provide: ClaseService, useClass: HttpClaseService },
        { provide: ReservaService, useClass: HttpReservaService },
      ],
    });
    const http = TestBed.inject(HttpTestingController);
    const result = cargarClasesConCupo(
      TestBed.inject(ClaseService), TestBed.inject(ReservaService), 7,
    );
    http.expectOne((r) => r.url === '/v1/clases').flush([
      { id_clase: 1, capacidad_max: 10, nombre_clase: 'Yoga', id_entrenador: 3, horario: '2026-11-01T10:00:00' },
    ]);
    http.expectOne((r) => r.url === '/v1/entrenadores').flush([{ id_entrenador: 3, nombre: 'Ana' }]);
    const mine = http.expectOne((r) => r.url === '/v1/reservas');
    expect(mine.request.params.get('id_cliente')).toBe('7');
    mine.flush([{ id_reserva: 4, id_cliente: 7, id_clase: 1 }]);
    await new Promise<void>((resolve) => setTimeout(resolve, 0));
    http.expectOne({ method: 'GET', url: '/v1/clases/1/cupo' }).flush({
      id_clase: 1, capacidad_max: 10, reservas: 8, plazas_disponibles: 2,
    });
    await expect(result).resolves.toMatchObject([{ plazasLibres: 2, reservadaPorMi: true }]);
    http.verify();
  });
});
