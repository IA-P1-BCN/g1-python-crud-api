import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { SessionService } from '../../../core/auth/session.service';
import { USUARIO_ANA } from '../../../core/auth/usuarios-prueba';
import { ClaseService } from '../../../services/clase.service';
import { ReservaService } from '../../../services/reserva.service';
import { CLASES_MOCK } from '../../../services/mock/datos-mock';
import { HomeMarketplacePage } from './home-marketplace.page';

describe('HomeMarketplacePage', () => {
  let fixture: ComponentFixture<HomeMarketplacePage>;
  const texto = () => (fixture.nativeElement as HTMLElement).textContent ?? '';

  beforeEach(async () => {
    sessionStorage.clear();
    await TestBed.configureTestingModule({
      imports: [HomeMarketplacePage],
      providers: [
        provideRouter([]),
        {
          provide: ClaseService,
          useValue: {
            listar: async () => structuredClone([...CLASES_MOCK]),
            listarEntrenadores: async () => [],
            cupo: async () => ({ id_clase: 1, capacidad_max: 10, reservas: 0, plazas_disponibles: 10 }),
          },
        },
        { provide: ReservaService, useValue: { listarDeCliente: async () => [], crear: async () => ({}) } },
      ],
    }).compileComponents();
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    fixture = TestBed.createComponent(HomeMarketplacePage);
    fixture.detectChanges();
  });

  it('muestra el hero con el buscador', () => {
    expect(texto()).toContain('Reserva tu plaza en GymFlow');
    expect(fixture.nativeElement.querySelector('input[type="search"]')).not.toBeNull();
  });

  it('lista las próximas clases del catálogo real', async () => {
    await new Promise((r) => setTimeout(r, 0));
    fixture.detectChanges();
    expect(texto()).toContain('Próximas clases');
    expect(texto()).toContain(CLASES_MOCK[0].nombre_clase);
  });
});
