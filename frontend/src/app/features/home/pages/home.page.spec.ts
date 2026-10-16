import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { ClaseService } from '../../../services/clase.service';
import { ReservaService } from '../../../services/reserva.service';
import { MockClaseService } from '../../../services/mock/mock-clase.service';
import { MockReservaService } from '../../../services/mock/mock-reserva.service';
import { esperarCarga } from '../../../testing/esperar';
import { HomePage } from './home.page';

describe('HomePage', () => {
  let fixture: ComponentFixture<HomePage>;
  const elemento = () => fixture.nativeElement as HTMLElement;

  beforeEach(async () => {
    sessionStorage.clear();
    await TestBed.configureTestingModule({
      imports: [HomePage],
      providers: [
        provideRouter([]),
        { provide: ClaseService, useClass: MockClaseService },
        { provide: ReservaService, useClass: MockReservaService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomePage);
    fixture.detectChanges();
    await esperarCarga(fixture);
  });

  it('muestra las clases a un visitante en solo lectura', () => {
    expect(elemento().textContent).toContain('Yoga');
    expect(elemento().textContent).toContain('Spinning');
    const reservar = [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Reservar');
    expect(reservar).toBeUndefined();
  });

  it('al ver la información de una clase pide iniciar sesión para reservar', () => {
    const boton = [...elemento().querySelectorAll('button')].find((b) =>
      b.textContent?.includes('Ver información'),
    )!;
    boton.click();
    fixture.detectChanges();

    expect(elemento().textContent).toContain('Para reservar');
    expect(elemento().querySelector('a[href^="/login"]')).not.toBeNull();
  });
});
