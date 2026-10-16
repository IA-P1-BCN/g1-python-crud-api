import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { ApiError } from '../../../core/http/peticion';
import { ClientesApi, ClienteEntrada } from '../../../services/api/recursos.api';
import { esperarCarga } from '../../../testing/esperar';
import { Cliente } from '../../../shared/models/cliente.model';
import { ClientesPage } from './clientes.page';

const CLIENTE: Cliente = {
  id_cliente: 1,
  nombre: 'Ana Demo',
  email: 'ana@example.com',
  estado_membresia: 'Activo',
  fecha_inscripcion: '2026-10-01',
};

describe('ClientesPage', () => {
  let fixture: ComponentFixture<ClientesPage>;
  let api: {
    listar: ReturnType<typeof vi.fn>;
    crearCliente: ReturnType<typeof vi.fn>;
    reemplazar: ReturnType<typeof vi.fn>;
    eliminar: ReturnType<typeof vi.fn>;
  };

  beforeEach(async () => {
    sessionStorage.clear();
    api = {
      listar: vi.fn(() => Promise.resolve([CLIENTE])),
      crearCliente: vi.fn((datos: ClienteEntrada) =>
        Promise.resolve({ id_cliente: 2, ...datos }),
      ),
      reemplazar: vi.fn((id: number) => Promise.resolve({ ...CLIENTE, id_cliente: id })),
      eliminar: vi.fn(() => Promise.resolve()),
    };
    await TestBed.configureTestingModule({
      imports: [ClientesPage],
      providers: [provideRouter([]), { provide: ClientesApi, useValue: api }],
    }).compileComponents();

    fixture = TestBed.createComponent(ClientesPage);
    fixture.detectChanges();
    await esperarCarga(fixture);
  });

  afterEach(() => {
    document.querySelectorAll('.cdk-overlay-container, .cdk-overlay-backdrop').forEach((n) => n.remove());
  });

  const elemento = () => fixture.nativeElement as HTMLElement;
  const texto = () => elemento().textContent ?? '';
  const overlay = () => document.body.textContent ?? '';
  const componente = () => fixture.componentInstance;

  function enviarFormulario(id: 'filtros' | 'formulario'): void {
    elemento().querySelector(`#${id}`)!.dispatchEvent(new Event('submit'));
    fixture.detectChanges();
  }

  it('lista los clientes devueltos por la API', () => {
    expect(texto()).toContain('Ana Demo');
    expect(texto()).toContain('ana@example.com');
    expect(api.listar).toHaveBeenCalledWith({});
  });

  it('envía los filtros de texto y estado a la API', () => {
    componente()['filtroQ'].setValue('ana');
    componente()['filtroEstado'].setValue('Activo');
    enviarFormulario('filtros');
    expect(api.listar).toHaveBeenLastCalledWith({ q: 'ana', estado_membresia: 'Activo' });
  });

  it('crea un cliente con los campos de la API y muestra el éxito', async () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Nuevo cliente')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({
      nombre: '  Bruno Nuevo ',
      email: '',
      estado_membresia: 'Inactivo',
      fecha_inscripcion: '2026-10-15',
    });
    fixture.detectChanges();
    enviarFormulario('formulario');
    await esperarCarga(fixture);

    expect(api.crearCliente).toHaveBeenCalledWith({
      nombre: 'Bruno Nuevo',
      email: null,
      estado_membresia: 'Inactivo',
      fecha_inscripcion: '2026-10-15',
    });
    expect(texto()).toContain('Cliente creado');
  });

  it('no crea nada con un email inválido y marca el campo', () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Nuevo cliente')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({
      nombre: 'Bruno',
      email: 'no-es-email',
      estado_membresia: 'Activo',
      fecha_inscripcion: '',
    });
    fixture.detectChanges();
    enviarFormulario('formulario');
    expect(api.crearCliente).not.toHaveBeenCalled();
    expect(texto()).toContain('El email no tiene un formato válido');
  });

  it('edita con sustitución total (PUT) de todos los campos', async () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Editar')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({
      nombre: 'Ana Editada',
      email: 'ana@example.com',
      estado_membresia: 'Suspendido',
      fecha_inscripcion: '2026-10-01',
    });
    fixture.detectChanges();
    enviarFormulario('formulario');
    await esperarCarga(fixture);

    expect(api.reemplazar).toHaveBeenCalledWith(1, {
      nombre: 'Ana Editada',
      email: 'ana@example.com',
      estado_membresia: 'Suspendido',
      fecha_inscripcion: '2026-10-01',
    });
    expect(texto()).toContain('Cliente actualizado');
  });

  it('muestra el detalle del conflicto si la API rechaza el borrado', async () => {
    api.eliminar.mockRejectedValue(
      new ApiError(409, 'La operación entra en conflicto con un registro o relación existente'),
    );
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Borrar')!.click();
    await esperarCarga(fixture);
    expect(overlay()).toContain('¿Dar de baja a Ana Demo?');

    [...document.querySelectorAll('button')]
      .find((b) => b.textContent?.trim() === 'Sí, borrar')!
      .click();
    await esperarCarga(fixture);

    expect(texto()).toContain('La operación entra en conflicto con un registro o relación existente');
    expect(api.listar).toHaveBeenCalledTimes(1);
  });
});
