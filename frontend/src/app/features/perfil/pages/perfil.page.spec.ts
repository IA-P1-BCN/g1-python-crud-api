import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { SessionService } from '../../../core/auth/session.service';
import { USUARIO_ANA } from '../../../core/auth/usuarios-prueba';
import { ApiError } from '../../../core/http/peticion';
import { CuentasApi } from '../../../services/api/recursos.api';
import { esperarCarga } from '../../../testing/esperar';
import { Cuenta } from '../../../shared/models/cuenta.model';
import { PerfilPage } from './perfil.page';

const CUENTA: Cuenta = {
  id: 1,
  nombre: 'Ana García',
  email: 'cliente@gym.test',
  activo: true,
  rol: 'cliente',
  fecha_creacion: '2026-10-01T10:00:00',
  id_cliente: 1,
};

describe('PerfilPage', () => {
  let fixture: ComponentFixture<PerfilPage>;
  let api: { yo: ReturnType<typeof vi.fn>; parchear: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    sessionStorage.clear();
    api = {
      yo: vi.fn(() => Promise.resolve(CUENTA)),
      parchear: vi.fn((id: number, cambios: Partial<Cuenta> & { password?: string }) =>
        Promise.resolve({ ...CUENTA, ...cambios, id }),
      ),
    };
    await TestBed.configureTestingModule({
      imports: [PerfilPage],
      providers: [provideRouter([]), { provide: CuentasApi, useValue: api }],
    }).compileComponents();

    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    fixture = TestBed.createComponent(PerfilPage);
    fixture.detectChanges();
    await esperarCarga(fixture);
  });

  const elemento = () => fixture.nativeElement as HTMLElement;
  const texto = () => elemento().textContent ?? '';
  const componente = () => fixture.componentInstance;

  function enviar(): void {
    elemento().querySelector('#formulario')!.dispatchEvent(new Event('submit'));
    fixture.detectChanges();
  }

  it('muestra los datos de /v1/users/me sin credenciales', () => {
    expect(api.yo).toHaveBeenCalled();
    expect(texto()).toContain('Ana García');
    expect(texto()).toContain('cliente@gym.test');
    expect(texto()).not.toContain('password_hash');
  });

  it('actualiza nombre y email con PATCH y refleja el cambio en la sesión', async () => {
    componente()['form'].setValue({ nombre: 'Ana Editada', email: 'ana.nuevo@example.com', password: '' });
    fixture.detectChanges();
    enviar();
    await esperarCarga(fixture);

    expect(api.parchear).toHaveBeenCalledWith(1, { nombre: 'Ana Editada', email: 'ana.nuevo@example.com' });
    expect(texto()).toContain('Perfil actualizado');
    const sesion = TestBed.inject(SessionService).usuario();
    expect(sesion?.nombre).toBe('Ana Editada');
    expect(sesion?.email).toBe('ana.nuevo@example.com');
  });

  it('envía la contraseña nueva cuando se indica', async () => {
    componente()['form'].setValue({
      nombre: 'Ana García',
      email: 'cliente@gym.test',
      password: 'contraseña-larga-1',
    });
    fixture.detectChanges();
    enviar();
    await esperarCarga(fixture);

    expect(api.parchear).toHaveBeenCalledWith(1, {
      nombre: 'Ana García',
      email: 'cliente@gym.test',
      password: 'contraseña-larga-1',
    });
    expect(componente()['form'].getRawValue().password).toBe('');
  });

  it('muestra el conflicto de email sin tocar la sesión', async () => {
    api.parchear.mockRejectedValue(new ApiError(409, 'Email de Cuenta ya registrado'));
    componente()['form'].setValue({ nombre: 'Ana García', email: 'ocupado@example.com', password: '' });
    fixture.detectChanges();
    enviar();
    await esperarCarga(fixture);

    expect(texto()).toContain('Email de Cuenta ya registrado');
    const sesion = TestBed.inject(SessionService).usuario();
    expect(sesion?.email).toBe('cliente@gym.test');
  });
});
