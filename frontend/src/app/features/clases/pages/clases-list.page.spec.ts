import { ComponentFixture, TestBed } from '@angular/core/testing';
import { esperarCarga } from '../../../testing/esperar';
import { provideRouter } from '@angular/router';
import { ClaseService } from '../../../services/clase.service';
import { ReservaService } from '../../../services/reserva.service';
import { MockClaseService } from '../../../services/mock/mock-clase.service';
import { MockReservaService } from '../../../services/mock/mock-reserva.service';
import { SessionService } from '../../../core/auth/session.service';
import { USUARIO_ANA } from '../../../core/auth/usuarios-prueba';
import { ClasesListPage } from './clases-list.page';

describe('ClasesListPage', () => {
  let fixture: ComponentFixture<ClasesListPage>;

  beforeEach(async () => {
    sessionStorage.clear();
    await TestBed.configureTestingModule({
      imports: [ClasesListPage],
      providers: [
        provideRouter([]),
        { provide: ClaseService, useClass: MockClaseService },
        { provide: ReservaService, useClass: MockReservaService },
      ],
    }).compileComponents();

    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    fixture = TestBed.createComponent(ClasesListPage);
    fixture.detectChanges();
    await esperarCarga(fixture);
  });

  const texto = () => (fixture.nativeElement as HTMLElement).textContent ?? '';

  it('muestra las plazas libres calculadas desde las reservas', () => {
    expect(texto()).toContain('3 de 12 plazas libres');
    expect(texto()).toContain('1 de 15 plazas libres');
    expect(texto()).toContain('20 de 20 plazas libres');
  });

  it('marca como completa la clase sin plazas y como reservada la de Ana', () => {
    expect(texto()).toContain('Completa');
    expect(texto()).toContain('Ya reservada');
  });

  it('filtra por nombre de clase', () => {
    const input = (fixture.nativeElement as HTMLElement).querySelector('input') as HTMLInputElement;
    input.value = 'zum';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    expect(texto()).toContain('Zumba');
    expect(texto()).not.toContain('Spinning');
  });

  it('reservar una clase con plazas actualiza el cupo', async () => {
    const boton = [...(fixture.nativeElement as HTMLElement).querySelectorAll('button')].find(
      (b) => b.textContent?.trim() === 'Reservar' && b.closest('article')?.textContent?.includes('Zumba'),
    ) as HTMLButtonElement;
    boton.click();
    await esperarCarga(fixture);
    expect(texto()).toContain('Reserva confirmada');
    expect(texto()).toContain('19 de 20 plazas libres');
  });
});
