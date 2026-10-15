import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { ApiError } from '../../../core/http/peticion';
import { NetworkError } from '../../../core/auth/auth.errors';
import { ExportApi } from '../../../services/api/recursos.api';
import { esperarCarga } from '../../../testing/esperar';
import { descargarArchivo } from '../../../shared/format/descargar';
import { ExportPage } from './export.page';

vi.mock('../../../shared/format/descargar', () => ({
  descargarArchivo: vi.fn(),
}));

describe('ExportPage', () => {
  let fixture: ComponentFixture<ExportPage>;
  let api: { exportarCsv: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    vi.mocked(descargarArchivo).mockClear();
    api = { exportarCsv: vi.fn(() => Promise.resolve('id_cliente,nombre\n1,Ana\n')) };
    await TestBed.configureTestingModule({
      imports: [ExportPage],
      providers: [provideRouter([]), { provide: ExportApi, useValue: api }],
    }).compileComponents();

    fixture = TestBed.createComponent(ExportPage);
    fixture.detectChanges();
  });

  const elemento = () => fixture.nativeElement as HTMLElement;
  const texto = () => elemento().textContent ?? '';

  function botonTabla(tabla: string): HTMLButtonElement {
    return [...elemento().querySelectorAll('button')].find((b) =>
      b.textContent?.includes(`Descargar ${tabla}`),
    ) as HTMLButtonElement;
  }

  it('ofrece una descarga por cada tabla exportable', () => {
    for (const tabla of ['Clientes', 'Entrenadores', 'Clases', 'Reservas', 'Pagos']) {
      expect(botonTabla(tabla)).toBeTruthy();
    }
  });

  it('descarga el CSV con el nombre de la tabla', async () => {
    botonTabla('Clientes').click();
    await esperarCarga(fixture);

    expect(api.exportarCsv).toHaveBeenCalledWith('clientes');
    expect(descargarArchivo).toHaveBeenCalledWith('clientes.csv', 'id_cliente,nombre\n1,Ana\n', 'text/csv');
    expect(texto()).toContain('Descarga de clientes completada');
  });

  it('muestra el error sin descargar si la API falla', async () => {
    api.exportarCsv.mockRejectedValue(new NetworkError());
    botonTabla('Pagos').click();
    await esperarCarga(fixture);

    expect(descargarArchivo).not.toHaveBeenCalled();
    expect(texto()).toContain('No se pudo conectar con el servidor');
  });

  it('muestra el detalle del error del servidor', async () => {
    api.exportarCsv.mockRejectedValue(new ApiError(503, 'Base de datos no disponible'));
    botonTabla('Clases').click();
    await esperarCarga(fixture);

    expect(texto()).toContain('Base de datos no disponible');
  });
});
