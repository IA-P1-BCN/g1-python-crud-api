import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { SessionService } from '../../core/auth/session.service';
import { USUARIO_ADMIN, USUARIO_ANA, USUARIO_STAFF } from '../../core/auth/usuarios-prueba';
import { AppShellComponent } from './app-shell.component';

describe('AppShellComponent', () => {
  let fixture: ComponentFixture<AppShellComponent>;
  /** Los enlaces de la cabecera de escritorio viven dentro del <header>. */
  const header = () => (fixture.nativeElement as HTMLElement).querySelector('header')?.textContent ?? '';
  /** La barra inferior es el <nav> hermano del <main>. */
  const barraMovil = () =>
    [...((fixture.nativeElement as HTMLElement).querySelectorAll('nav.barra-inferior') ?? [])]
      .map((n) => n.textContent ?? '')
      .join(' ');

  beforeEach(async () => {
    sessionStorage.clear();
    await TestBed.configureTestingModule({
      imports: [AppShellComponent],
      providers: [provideRouter([])],
    }).compileComponents();
    fixture = TestBed.createComponent(AppShellComponent);
    fixture.detectChanges();
  });

  it('sin sesión la cabecera solo muestra el logo', () => {
    expect(header()).toContain('GymFlow');
    expect(header()).not.toContain('Catálogo');
    expect(header()).not.toContain('Dashboard');
  });

  it('el rol cliente ve catálogo y mis reservas, sin enlaces de otros roles', () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    fixture.detectChanges();
    expect(header()).toContain('Catálogo');
    expect(header()).toContain('Mis reservas');
    for (const enlace of ['Mi panel', 'Mis clases', 'Dashboard', 'Clientes', 'Entrenadores', 'Clases']) {
      expect(header()).not.toContain(enlace);
    }
  });

  it('el rol staff ve su panel y sus clases, sin marketplace ni admin', () => {
    TestBed.inject(SessionService).iniciar(USUARIO_STAFF);
    fixture.detectChanges();
    expect(header()).toContain('Mi panel');
    expect(header()).toContain('Mis clases');
    for (const enlace of ['Catálogo', 'Mis reservas', 'Dashboard', 'Clientes', 'Entrenadores']) {
      expect(header()).not.toContain(enlace);
    }
  });

  it('el rol admin ve gestión y no los enlaces de marketplace ni perfil', () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ADMIN);
    fixture.detectChanges();
    for (const enlace of ['Dashboard', 'Clientes', 'Entrenadores', 'Clases']) {
      expect(header()).toContain(enlace);
    }
    for (const enlace of ['Catálogo', 'Mis reservas', 'Mi perfil']) {
      expect(header()).not.toContain(enlace);
    }
  });

  it('la barra inferior móvil replica los enlaces del rol', () => {
    TestBed.inject(SessionService).iniciar(USUARIO_ADMIN);
    fixture.detectChanges();
    expect(barraMovil()).toContain('Panel');
    expect(barraMovil()).toContain('Clientes');
    expect(barraMovil()).not.toContain('Catálogo');
  });

  it('el logo lleva al staff a su panel y al cliente al marketplace', () => {
    const logo = () => (fixture.nativeElement as HTMLElement).querySelector('a.logo') as HTMLAnchorElement;
    TestBed.inject(SessionService).iniciar(USUARIO_STAFF);
    fixture.detectChanges();
    expect(logo().getAttribute('href')).toContain('/staff');
    TestBed.inject(SessionService).cerrar();
    TestBed.inject(SessionService).iniciar(USUARIO_ANA);
    fixture.detectChanges();
    expect(logo().getAttribute('href')).toContain('/marketplace');
  });
});
