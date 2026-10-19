import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { ClientesApi, EntrenadoresApi, ReservasApi } from '../../../services/api/recursos.api';
import { ClaseService } from '../../../services/clase.service';
import { AdminDashboardPage } from './admin-dashboard.page';

describe('AdminDashboardPage', () => {
  let fixture: ComponentFixture<AdminDashboardPage>;
  const texto = () => (fixture.nativeElement as HTMLElement).textContent ?? '';

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminDashboardPage],
      providers: [
        provideRouter([]),
        {
          provide: ReservasApi,
          useValue: {
            listar: async () => [
              { id_reserva: 1, id_cliente: 1, id_clase: 1, asistio: true, fecha_reserva: '2026-10-01T10:00:00' },
              { id_reserva: 2, id_cliente: 2, id_clase: 1, asistio: false, fecha_reserva: '2026-10-15T10:00:00' },
            ],
          },
        },
        { provide: ClientesApi, useValue: { listar: async () => [{}, {}] } },
        { provide: EntrenadoresApi, useValue: { listar: async () => [{ id_entrenador: 7, nombre: 'Laura' }] } },
        {
          provide: ClaseService,
          useValue: {
            listar: async () => [
              { id_clase: 1, nombre_clase: 'Yoga', horario: '2026-11-01T10:00:00', capacidad_max: 10, id_entrenador: 7 },
              { id_clase: 2, nombre_clase: 'Pilates', horario: '2026-11-02T10:00:00', capacidad_max: 8, id_entrenador: 7 },
            ],
          },
        },
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(AdminDashboardPage);
    fixture.detectChanges();
    await new Promise((r) => setTimeout(r, 0));
    fixture.detectChanges();
  });

  it('suma los totales de los listados reales', () => {
    expect(texto()).toContain('Reservas: 2');
    expect(texto()).toContain('Clientes: 2');
    expect(texto()).toContain('Entrenadores: 1');
    expect(texto()).toContain('Clases: 2');
  });

  it('dibuja asistencia y clases por entrenador', () => {
    expect(texto()).toContain('Asistidas');
    expect(texto()).toContain('No asistidas');
    expect(texto()).toContain('Laura');
  });
});
