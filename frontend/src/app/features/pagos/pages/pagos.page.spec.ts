import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { ApiError } from '../../../core/http/peticion';
import { ClientesApi, PagosApi } from '../../../services/api/recursos.api';
import { esperarCarga } from '../../../testing/esperar';
import { Cliente } from '../../../shared/models/cliente.model';
import { Pago, PagoEntrada } from '../../../shared/models/pago.model';
import { PagosPage } from './pagos.page';

const PAGO: Pago = {
  id_pago: 7,
  id_cliente: 1,
  monto: '35.00',
  fecha_pago: '2026-10-15',
  metodo_pago: 'Tarjeta',
};

const CLIENTE: Cliente = {
  id_cliente: 1,
  nombre: 'Ana Demo',
  email: 'ana@example.com',
  estado_membresia: 'Activo',
  fecha_inscripcion: '2026-10-01',
};

describe('PagosPage', () => {
  let fixture: ComponentFixture<PagosPage>;
  let pagos: {
    listar: ReturnType<typeof vi.fn>;
    crearPago: ReturnType<typeof vi.fn>;
    reemplazar: ReturnType<typeof vi.fn>;
    eliminar: ReturnType<typeof vi.fn>;
  };
  let clientes: { listar: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    sessionStorage.clear();
    pagos = {
      listar: vi.fn(() => Promise.resolve([PAGO])),
      crearPago: vi.fn((datos: PagoEntrada) => Promise.resolve({ id_pago: 8, ...datos })),
      reemplazar: vi.fn((id: number) => Promise.resolve({ ...PAGO, id_pago: id })),
      eliminar: vi.fn(() => Promise.resolve()),
    };
    clientes = { listar: vi.fn(() => Promise.resolve([CLIENTE])) };
    await TestBed.configureTestingModule({
      imports: [PagosPage],
      providers: [
        provideRouter([]),
        { provide: PagosApi, useValue: pagos },
        { provide: ClientesApi, useValue: clientes },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(PagosPage);
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

  it('lista los pagos mostrando el cliente resuelto', () => {
    expect(texto()).toContain('35.00 €');
    expect(texto()).toContain('Ana Demo (#1)');
  });

  it('filtra por cliente y método en la petición', () => {
    componente()['filtroCliente'].setValue('1');
    componente()['filtroMetodo'].setValue('Efectivo');
    enviarFormulario('filtros');
    expect(pagos.listar).toHaveBeenLastCalledWith({ id_cliente: 1, metodo_pago: 'Efectivo' });
  });

  it('bloquea el envío con un monto no positivo', () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Nuevo pago')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({ id_cliente: '1', monto: '0', fecha_pago: '2026-10-15', metodo_pago: '' });
    fixture.detectChanges();
    enviarFormulario('formulario');
    expect(pagos.crearPago).not.toHaveBeenCalled();
    expect(texto()).toContain('El monto debe ser mayor que cero');
  });

  it('crea un pago con id_cliente numérico y monto normalizado', async () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Nuevo pago')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({
      id_cliente: '1',
      monto: '35,5',
      fecha_pago: '2026-10-15',
      metodo_pago: 'Tarjeta',
    });
    fixture.detectChanges();
    const f = componente()['form'] as { status: string; errors: unknown; controls: Record<string, { status: string; errors: unknown }> };
    // eslint-disable-next-line no-console
    console.log('DEBUG status', f.status, 'errors', JSON.stringify(f.errors), JSON.stringify(Object.fromEntries(Object.entries(f.controls).map(([k, v]) => [k, `${v.status}:${JSON.stringify(v.errors)}`]))));
    console.log('DEBUG formulario', componente()['formulario']?.());
    enviarFormulario('formulario');
    await esperarCarga(fixture);

    expect(pagos.crearPago).toHaveBeenCalledWith({
      id_cliente: 1,
      monto: '35.5',
      fecha_pago: '2026-10-15',
      metodo_pago: 'Tarjeta',
    });
    expect(texto()).toContain('Pago creado');
  });

  it('muestra el 404 de la API si el cliente no existe', async () => {
    pagos.crearPago.mockRejectedValue(new ApiError(404, 'Cliente con id 99 no existe'));
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Nuevo pago')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({ id_cliente: '1', monto: '10.00', fecha_pago: '2026-10-15', metodo_pago: '' });
    fixture.detectChanges();
    enviarFormulario('formulario');
    await esperarCarga(fixture);

    expect(texto()).toContain('Cliente con id 99 no existe');
    expect(texto()).toContain('Nuevo pago');
  });
});
