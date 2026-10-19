import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { ApiError } from '../../../core/http/peticion';
import { EntrenadoresApi, EntrenadorEntrada } from '../../../services/api/recursos.api';
import { esperarCarga } from '../../../testing/esperar';
import { limpiarToasts, mensajesDeToast } from '../../../testing/toast';
import { Entrenador } from '../../../shared/models/entrenador.model';
import { EntrenadoresPage } from './entrenadores.page';

const ENTRENADOR: Entrenador = {
  id_entrenador: 1,
  nombre: 'Laura Demo',
  especialidad: 'Yoga',
  telefono: null,
};

describe('EntrenadoresPage', () => {
  let fixture: ComponentFixture<EntrenadoresPage>;
  let api: {
    listar: ReturnType<typeof vi.fn>;
    crearEntrenador: ReturnType<typeof vi.fn>;
    reemplazar: ReturnType<typeof vi.fn>;
    eliminar: ReturnType<typeof vi.fn>;
  };

  beforeEach(async () => {
    sessionStorage.clear();
    limpiarToasts();
    api = {
      listar: vi.fn(() => Promise.resolve([ENTRENADOR])),
      crearEntrenador: vi.fn((datos: EntrenadorEntrada) =>
        Promise.resolve({ id_entrenador: 2, ...datos }),
      ),
      reemplazar: vi.fn((id: number) => Promise.resolve({ ...ENTRENADOR, id_entrenador: id })),
      eliminar: vi.fn(() => Promise.resolve()),
    };
    await TestBed.configureTestingModule({
      imports: [EntrenadoresPage],
      providers: [provideRouter([]), { provide: EntrenadoresApi, useValue: api }],
    }).compileComponents();

    fixture = TestBed.createComponent(EntrenadoresPage);
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

  it('lista los entrenadores con su especialidad', () => {
    expect(texto()).toContain('Laura Demo');
    expect(texto()).toContain('Yoga');
  });

  it('filtra con q en la petición', () => {
    componente()['filtroQ'].setValue('lau');
    enviarFormulario('filtros');
    expect(api.listar).toHaveBeenLastCalledWith({ q: 'lau' });
  });

  it('crea un entrenador normalizando opcionales vacíos a null', async () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Nuevo entrenador')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({ nombre: 'Carlos', especialidad: '', telefono: ' 600 000 000 ' });
    fixture.detectChanges();
    enviarFormulario('formulario');
    await esperarCarga(fixture);

    expect(api.crearEntrenador).toHaveBeenCalledWith({
      nombre: 'Carlos',
      especialidad: null,
      telefono: '600 000 000',
    });
    expect(mensajesDeToast()).toContain('Entrenador creado');
  });

  it('muestra el conflicto si la API rechaza borrar un entrenador con clases', async () => {
    api.eliminar.mockRejectedValue(
      new ApiError(409, 'La operación entra en conflicto con un registro o relación existente'),
    );
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Borrar')!.click();
    await esperarCarga(fixture);
    [...document.querySelectorAll('button')]
      .find((b) => b.textContent?.trim() === 'Sí, borrar')!
      .click();
    await esperarCarga(fixture);

    expect(mensajesDeToast()).toContain('La operación entra en conflicto con un registro o relación existente');
    expect(api.listar).toHaveBeenCalledTimes(1);
  });
});
