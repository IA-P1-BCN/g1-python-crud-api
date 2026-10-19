import { ComponentFixture, TestBed } from '@angular/core/testing';
import { esperarCarga } from '../../../testing/esperar';
import { limpiarToasts, mensajesDeToast } from '../../../testing/toast';
import { provideRouter } from '@angular/router';
import { ClaseService } from '../../../services/clase.service';
import { ReservaService } from '../../../services/reserva.service';
import { MockClaseService } from '../../../services/mock/mock-clase.service';
import { MockReservaService } from '../../../services/mock/mock-reserva.service';
import { SessionService } from '../../../core/auth/session.service';
import { USUARIO_ANA } from '../../../core/auth/usuarios-prueba';
import { MisReservasPage } from './mis-reservas.page';

describe('MisReservasPage', () => {
  let fixture: ComponentFixture<MisReservasPage>;

  beforeEach(async () => {
    sessionStorage.clear();
    limpiarToasts();
    await TestBed.configureTestingModule({
      imports: [MisReservasPage],
      providers: [
        provideRouter([]),
        { provide: ClaseService, useClass: MockClaseService },
        { provide: ReservaService, useClass: MockReservaService },
      ],
    }).compileComponents();

    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    fixture = TestBed.createComponent(MisReservasPage);
    fixture.detectChanges();
    await esperarCarga(fixture);
  });

  const elemento = () => fixture.nativeElement as HTMLElement;
  const texto = () => elemento().textContent ?? '';

  function botonPestana(nombre: string): HTMLButtonElement {
    return [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === nombre) as HTMLButtonElement;
  }

  it('muestra la próxima reserva de Ana en la pestaña Próximas', () => {
    expect(texto()).toContain('Yoga');
    expect(texto()).toContain('Cancelar reserva');
  });

  it('muestra las clases pasadas en la pestaña Pasadas, sin botón de cancelar', () => {
    botonPestana('Pasadas').click();
    fixture.detectChanges();
    expect(texto()).toContain('Pilates');
    expect(texto()).not.toContain('Cancelar reserva');
  });

  it('cancela tras confirmar en el diálogo y muestra el aviso', async () => {
    elemento().querySelector<HTMLButtonElement>('li button')!.click();
    fixture.detectChanges();
    expect(document.body.textContent).toContain('¿Cancelar la reserva de Yoga');

    [...document.querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Sí, cancelar')!.click();
    await esperarCarga(fixture);
    expect(mensajesDeToast()).toContain('Reserva cancelada');
    expect(texto()).toContain('Aún no tienes reservas');
  });
});
