import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { ApiError } from '../../../core/http/peticion';
import { CuentasApi } from '../../../services/api/recursos.api';
import { esperarCarga } from '../../../testing/esperar';
import { Cuenta } from '../../../shared/models/cuenta.model';
import { CuentasPage } from './cuentas.page';

const CUENTA: Cuenta = {
  id: 21,
  nombre: 'Demo GymFlow',
  email: 'demo@example.com',
  activo: true,
  rol: 'cliente',
  fecha_creacion: '2026-10-15T16:53:58',
  id_cliente: 119,
};

describe('CuentasPage', () => {
  let fixture: ComponentFixture<CuentasPage>;
  let api: {
    listar: ReturnType<typeof vi.fn>;
    reemplazar: ReturnType<typeof vi.fn>;
    eliminar: ReturnType<typeof vi.fn>;
  };

  beforeEach(async () => {
    sessionStorage.clear();
    api = {
      listar: vi.fn(() => Promise.resolve([CUENTA])),
      reemplazar: vi.fn((id: number) => Promise.resolve({ ...CUENTA, id, nombre: 'Editada' })),
      eliminar: vi.fn(() => Promise.resolve()),
    };
    await TestBed.configureTestingModule({
      imports: [CuentasPage],
      providers: [provideRouter([]), { provide: CuentasApi, useValue: api }],
    }).compileComponents();

    fixture = TestBed.createComponent(CuentasPage);
    fixture.detectChanges();
    await esperarCarga(fixture);
  });

  afterEach(() => {
    document.querySelectorAll('.cdk-overlay-container, .cdk-overlay-backdrop').forEach((n) => n.remove());
  });

  const elemento = () => fixture.nativeElement as HTMLElement;
  const texto = () => elemento().textContent ?? '';
  const componente = () => fixture.componentInstance;

  function enviarFormulario(id: 'filtros' | 'formulario'): void {
    elemento().querySelector(`#${id}`)!.dispatchEvent(new Event('submit'));
    fixture.detectChanges();
  }

  it('lista las cuentas con rol y estado, sin credenciales', () => {
    expect(texto()).toContain('demo@example.com');
    expect(texto()).toContain('cliente');
    expect(texto()).not.toContain('password');
  });

  it('combina los filtros de texto, rol y activo en la petición', () => {
    componente()['filtroQ'].setValue('demo');
    componente()['filtroRol'].setValue('admin');
    componente()['filtroActivo'].setValue('false');
    enviarFormulario('filtros');
    expect(api.listar).toHaveBeenLastCalledWith({ q: 'demo', rol: 'admin', activo: false });
  });

  it('edita con PUT omitiendo la contraseña si se deja vacía', async () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Editar')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({ nombre: 'Demo Editada', email: 'demo@example.com', password: '' });
    fixture.detectChanges();
    enviarFormulario('formulario');
    await esperarCarga(fixture);

    expect(api.reemplazar).toHaveBeenCalledWith(21, { nombre: 'Demo Editada', email: 'demo@example.com' });
    expect(texto()).toContain('Cuenta actualizada');
  });

  it('incluye la contraseña nueva solo si tiene al menos 12 caracteres', async () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Editar')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({
      nombre: 'Demo GymFlow',
      email: 'demo@example.com',
      password: 'corta',
    });
    fixture.detectChanges();
    enviarFormulario('formulario');
    expect(api.reemplazar).not.toHaveBeenCalled();
    expect(texto()).toContain('entre 12 y 128 caracteres');

    componente()['form'].setValue({
      nombre: 'Demo GymFlow',
      email: 'demo@example.com',
      password: 'contraseña-larga-1',
    });
    fixture.detectChanges();
    enviarFormulario('formulario');
    await esperarCarga(fixture);
    expect(api.reemplazar).toHaveBeenCalledWith(21, {
      nombre: 'Demo GymFlow',
      email: 'demo@example.com',
      password: 'contraseña-larga-1',
    });
  });

  it('muestra el error de sesión inválida si la API responde 401', async () => {
    api.listar.mockRejectedValue(new ApiError(401, 'No se pudieron validar las credenciales'));
    componente()['filtroQ'].setValue('x');
    enviarFormulario('filtros');
    await esperarCarga(fixture);

    expect(texto()).toContain('No se pudieron validar las credenciales');
  });
});
