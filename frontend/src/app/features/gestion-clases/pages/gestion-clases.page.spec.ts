import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { ApiError } from '../../../core/http/peticion';
import { ClasesApi, ClaseEntrada, EntrenadoresApi } from '../../../services/api/recursos.api';
import { esperarCarga } from '../../../testing/esperar';
import { limpiarToasts, mensajesDeToast } from '../../../testing/toast';
import { Clase } from '../../../shared/models/clase.model';
import { Entrenador } from '../../../shared/models/entrenador.model';
import { GestionClasesPage } from './gestion-clases.page';

const CLASE: Clase = {
  id_clase: 1,
  nombre_clase: 'Yoga Demo',
  horario: '2026-11-01T10:00:00',
  capacidad_max: 10,
  id_entrenador: 1,
};

const ENTRENADOR: Entrenador = { id_entrenador: 1, nombre: 'Laura Demo', especialidad: 'Yoga', telefono: null };

describe('GestionClasesPage', () => {
  let fixture: ComponentFixture<GestionClasesPage>;
  let clases: {
    listar: ReturnType<typeof vi.fn>;
    crearClase: ReturnType<typeof vi.fn>;
    reemplazar: ReturnType<typeof vi.fn>;
    eliminar: ReturnType<typeof vi.fn>;
  };
  let entrenadores: { listar: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    sessionStorage.clear();
    limpiarToasts();
    clases = {
      listar: vi.fn(() => Promise.resolve([CLASE])),
      crearClase: vi.fn((datos: ClaseEntrada) => Promise.resolve({ id_clase: 2, ...datos })),
      reemplazar: vi.fn((id: number) => Promise.resolve({ ...CLASE, id_clase: id })),
      eliminar: vi.fn(() => Promise.resolve()),
    };
    entrenadores = { listar: vi.fn(() => Promise.resolve([ENTRENADOR])) };
    await TestBed.configureTestingModule({
      imports: [GestionClasesPage],
      providers: [
        provideRouter([]),
        { provide: ClasesApi, useValue: clases },
        { provide: EntrenadoresApi, useValue: entrenadores },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(GestionClasesPage);
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

  it('lista las clases resolviendo el nombre del entrenador', () => {
    expect(texto()).toContain('Yoga Demo');
    expect(texto()).toContain('Laura Demo');
    expect(texto()).toContain('10:00');
  });

  it('crea una clase enviando el horario UTC sin zona', async () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Nueva clase')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({
      nombre_clase: 'Pilates',
      horario: '2026-11-02T18:30',
      capacidad_max: '12',
      id_entrenador: '1',
    });
    fixture.detectChanges();
    enviarFormulario('formulario');
    await esperarCarga(fixture);

    expect(clases.crearClase).toHaveBeenCalledWith({
      nombre_clase: 'Pilates',
      horario: '2026-11-02T18:30:00',
      capacidad_max: 12,
      id_entrenador: 1,
    });
    expect(mensajesDeToast()).toContain('Clase creada');
  });

  it('no crea nada sin entrenador seleccionado', () => {
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Nueva clase')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({
      nombre_clase: 'Pilates',
      horario: '2026-11-02T18:30',
      capacidad_max: '12',
      id_entrenador: '',
    });
    fixture.detectChanges();
    enviarFormulario('formulario');
    expect(clases.crearClase).not.toHaveBeenCalled();
    expect(texto()).toContain('El entrenador es obligatorio.');
  });

  it('muestra el conflicto de capacidad que devuelve la API al editar', async () => {
    clases.reemplazar.mockRejectedValue(
      new ApiError(409, 'La capacidad no puede ser menor que las reservas'),
    );
    [...elemento().querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Editar')!.click();
    fixture.detectChanges();
    componente()['form'].setValue({
      nombre_clase: 'Yoga Demo',
      horario: '2026-11-01T10:00',
      capacidad_max: '2',
      id_entrenador: '1',
    });
    fixture.detectChanges();
    enviarFormulario('formulario');
    await esperarCarga(fixture);

    expect(mensajesDeToast()).toContain('La capacidad no puede ser menor que las reservas');
  });
});
