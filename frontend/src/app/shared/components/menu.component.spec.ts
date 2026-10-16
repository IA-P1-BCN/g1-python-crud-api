import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { vi } from 'vitest';
import { SessionService } from '../../core/auth/session.service';
import { USUARIO_ANA, USUARIO_STAFF } from '../../core/auth/usuarios-prueba';
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

  it('el rol cliente no ve el grupo de gestión', async () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    await abrir();
    expect(overlay()).not.toContain('Gestión');
    expect(overlay()).not.toContain('Cuentas');
    expect(overlay()).not.toContain('Exportar CSV');
  });

  it('el rol staff ve el grupo de gestión completo', async () => {
    TestBed.inject(SessionService).iniciar(USUARIO_STAFF);
    await abrir();
    expect(overlay()).toContain('Gestión');
    for (const enlace of ['Clientes', 'Entrenadores', 'Clases', 'Pagos', 'Cuentas', 'Exportar CSV']) {
      expect(overlay()).toContain(enlace);
    }
    expect(overlay()).not.toContain('Mi portal');
  });
});
