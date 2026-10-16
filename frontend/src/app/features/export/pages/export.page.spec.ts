import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { ApiError } from '../../../core/http/peticion';
import { NetworkError } from '../../../core/auth/auth.errors';
import { ExportApi } from '../../../services/api/recursos.api';
import { esperarCarga } from '../../../testing/esperar';
import { ExportPage } from './export.page';

interface Descarga {
  nombre: string;
  blob: Blob;
}

const URL_ORIGINAL = {
  create: URL.createObjectURL,
  revoke: URL.revokeObjectURL,
};

describe('ExportPage', () => {
  let fixture: ComponentFixture<ExportPage>;
  let api: { exportarCsv: ReturnType<typeof vi.fn> };
  let descargas: Descarga[];
  let ultima: Descarga | undefined;

  beforeEach(async () => {
    descargas = [];
    ultima = undefined;
    // jsdom no implementa URL.createObjectURL: se captura el blob aquí y el
    // nombre en el click del enlace efímero que crea descargarArchivo().
    URL.createObjectURL = vi.fn((blob: Blob) => {
      ultima = { nombre: '', blob };
      descargas.push(ultima);
      return `blob:test/${descargas.length}`;
    });
    URL.revokeObjectURL = vi.fn();
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      if (ultima) {
        ultima.nombre = this.download;
      }
    });

    api = { exportarCsv: vi.fn(() => Promise.resolve('id_cliente,nombre\n1,Ana\n')) };
    await TestBed.configureTestingModule({
      imports: [ExportPage],
      providers: [provideRouter([]), { provide: ExportApi, useValue: api }],
    }).compileComponents();

    fixture = TestBed.createComponent(ExportPage);
    fixture.detectChanges();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    if (URL_ORIGINAL.create) {
      URL.createObjectURL = URL_ORIGINAL.create;
    } else {
      delete (URL as { createObjectURL?: unknown }).createObjectURL;
    }
    if (URL_ORIGINAL.revoke) {
      URL.revokeObjectURL = URL_ORIGINAL.revoke;
    } else {
      delete (URL as { revokeObjectURL?: unknown }).revokeObjectURL;
    }
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
    expect(descargas).toHaveLength(1);
    expect(descargas[0].nombre).toBe('clientes.csv');
    expect(await descargas[0].blob.text()).toBe('id_cliente,nombre\n1,Ana\n');
    expect(descargas[0].blob.type).toContain('text/csv');
    expect(texto()).toContain('Descarga de clientes completada');
  });

  it('muestra el error sin descargar si la API falla', async () => {
    api.exportarCsv.mockRejectedValue(new NetworkError());
    botonTabla('Pagos').click();
    await esperarCarga(fixture);

    expect(descargas).toHaveLength(0);
    expect(texto()).toContain('No se pudo conectar con el servidor');
  });

  it('muestra el detalle del error del servidor', async () => {
    api.exportarCsv.mockRejectedValue(new ApiError(503, 'Base de datos no disponible'));
    botonTabla('Clases').click();
    await esperarCarga(fixture);

    expect(texto()).toContain('Base de datos no disponible');
  });
});
