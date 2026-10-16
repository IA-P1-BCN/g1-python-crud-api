import { TestBed } from '@angular/core/testing';
import { SessionService } from './session.service';
import { USUARIO_ANA } from './usuarios-prueba';

const CLAVE = 'gymflow.sesion';

describe('SessionService', () => {
  beforeEach(() => sessionStorage.clear());

  it('guarda la sesión en sessionStorage al iniciarla', () => {
    const sesion = TestBed.inject(SessionService);
    sesion.iniciar(USUARIO_ANA);
    expect(sesion.autenticado()).toBe(true);
    expect(sesion.idCliente()).toBe(1);
    expect(JSON.parse(sessionStorage.getItem(CLAVE)!)).toEqual(USUARIO_ANA);
  });

  it('restaura la sesión guardada al crear el servicio (recarga)', () => {
    sessionStorage.setItem(CLAVE, JSON.stringify(USUARIO_ANA));
    const sesion = TestBed.inject(SessionService);
    expect(sesion.usuario()?.nombre).toBe('Ana García');
  });

  it('cerrar sesión limpia el estado y el almacenamiento', () => {
    const sesion = TestBed.inject(SessionService);
    sesion.iniciar(USUARIO_ANA);
    sesion.cerrar();
    expect(sesion.autenticado()).toBe(false);
    expect(sessionStorage.getItem(CLAVE)).toBeNull();
  });

  it('ignora datos corruptos en sessionStorage', () => {
    sessionStorage.setItem(CLAVE, '{no-es-json');
    expect(TestBed.inject(SessionService).autenticado()).toBe(false);
  });
});
