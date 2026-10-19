import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { SessionService } from '../../core/auth/session.service';
import { USUARIO_ADMIN, USUARIO_ANA, USUARIO_STAFF } from '../../core/auth/usuarios-prueba';
import { esperarCarga } from '../../testing/esperar';
import { MenuComponent } from './menu.component';

describe('MenuComponent', () => {
  let fixture: ComponentFixture<MenuComponent>;
  const elemento = () => fixture.nativeElement as HTMLElement;
  /** El dropdown de Spartan se renderiza en un overlay fuera del host. */
  const overlay = () => document.body.textContent ?? '';

  beforeEach(async () => {
    sessionStorage.clear();
    await TestBed.configureTestingModule({
      imports: [MenuComponent],
      providers: [provideRouter([])],
    }).compileComponents();
    vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    fixture = TestBed.createComponent(MenuComponent);
    fixture.detectChanges();
  });

  afterEach(() => {
    document.querySelectorAll('.cdk-overlay-container, .cdk-overlay-backdrop').forEach((n) => n.remove());
  });

  async function abrir(): Promise<void> {
    elemento().querySelector<HTMLButtonElement>('button[aria-label="Abrir menú"]')!.click();
    await esperarCarga(fixture);
  }

  it('sin sesión ofrece iniciar sesión y crear cuenta', async () => {
    await abrir();
    expect(overlay()).toContain('Iniciar sesión');
    expect(overlay()).toContain('Crear cuenta');
  });

  it('con sesión muestra el nombre del usuario y permite cerrar sesión', async () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    await abrir();
    expect(overlay()).toContain('Ana García');
    expect(overlay()).not.toContain('Iniciar sesión');

    const salir = [...document.querySelectorAll('[hlmDropdownMenuItem], button')].find(
      (b) => b.textContent?.trim() === 'Cerrar sesión',
    ) as HTMLElement;
    salir.click();
    await esperarCarga(fixture);
    expect(TestBed.inject(SessionService).autenticado()).toBe(false);
  });

  it('con sesión ofrece el perfil propio', async () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    await abrir();
    expect(overlay()).toContain('Mi perfil');
  });

  it('el rol cliente ve el catálogo y no el panel ni la administración', async () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    await abrir();
    expect(overlay()).toContain('Catálogo');
    expect(overlay()).toContain('Mis reservas');
    expect(overlay()).not.toContain('Mi panel');
    expect(overlay()).not.toContain('Dashboard');
    expect(overlay()).not.toContain('Exportar CSV');
  });

  it('el rol staff ve su panel y no las operaciones de administrador', async () => {
    TestBed.inject(SessionService).iniciar(USUARIO_STAFF);
    await abrir();
    expect(overlay()).toContain('Mi panel');
    expect(overlay()).toContain('Mis clases');
    expect(overlay()).toContain('Reservas de mis clases');
    for (const enlace of ['Dashboard', 'Clientes', 'Entrenadores', 'Pagos', 'Cuentas', 'Exportar CSV']) {
      expect(overlay()).not.toContain(enlace);
    }
  });

  it('el rol admin ve un menú exclusivo de administración', async () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ADMIN);
    await abrir();
    expect(overlay()).toContain('Mi perfil');
    for (const enlace of ['Dashboard', 'Clientes', 'Entrenadores', 'Clases', 'Pagos', 'Cuentas', 'Exportar CSV']) {
      expect(overlay()).toContain(enlace);
    }
    for (const enlace of ['Catálogo', 'Mis reservas', 'Mi panel', 'Mis clases', 'Reservas de mis clases']) {
      expect(overlay()).not.toContain(enlace);
    }
  });
});
