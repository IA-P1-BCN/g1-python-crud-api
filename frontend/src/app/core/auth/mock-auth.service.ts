import { Injectable } from '@angular/core';
import { AuthService, DatosRegistro, UsuarioAutenticado } from './auth.service';
import { EmailDuplicadoError, InvalidCredentialsError, NetworkError } from './auth.errors';
import { USUARIO_ANA, USUARIO_STAFF } from './usuarios-prueba';

interface UsuarioDePrueba {
  readonly password: string;
  readonly usuario: UsuarioAutenticado;
}

/**
 * Datos ficticios solo para desarrollo, hasta que #55 esté disponible en main.
 * No son credenciales reales ni deben usarse fuera de desarrollo.
 */
const USUARIOS_DE_PRUEBA: Readonly<Record<string, UsuarioDePrueba>> = {
  'cliente@gym.test': { password: 'cliente123', usuario: USUARIO_ANA },
  'staff@gym.test': { password: 'staff123', usuario: USUARIO_STAFF },
};

/** Correo que simula un fallo de conexión, para probar ese estado a mano. */
const CORREO_SIMULA_RED_CAIDA = 'sin-red@gym.test';

/** Retardo artificial para que los estados de carga sean visibles en desarrollo. */
const RETARDO_MS = 400;

/** Longitud de contraseña que exige la API (CuentaRegister). */
const PASSWORD_MIN = 12;
const PASSWORD_MAX = 128;

@Injectable()
export class MockAuthService extends AuthService {
  /** Cuentas en memoria: las de prueba más las creadas durante la sesión. */
  private readonly cuentas = new Map<string, UsuarioDePrueba>(Object.entries(USUARIOS_DE_PRUEBA));
  private siguienteId = 3;
  private siguienteIdCliente = 1000;

  async login(email: string, password: string): Promise<UsuarioAutenticado> {
    await esperar();

    const correo = email.trim().toLowerCase();
    if (correo === CORREO_SIMULA_RED_CAIDA) {
      throw new NetworkError();
    }

    const prueba = this.cuentas.get(correo);
    if (!prueba || prueba.password !== password) {
      throw new InvalidCredentialsError();
    }
    return { ...prueba.usuario };
  }

  async register(datos: DatosRegistro): Promise<void> {
    await esperar();

    const correo = datos.email.trim().toLowerCase();
    if (correo === CORREO_SIMULA_RED_CAIDA) {
      throw new NetworkError();
    }
    if (this.cuentas.has(correo)) {
      throw new EmailDuplicadoError();
    }
    const longitud = datos.password.length;
    if (longitud < PASSWORD_MIN || longitud > PASSWORD_MAX) {
      throw new RangeError(`La contraseña debe tener entre ${PASSWORD_MIN} y ${PASSWORD_MAX} caracteres`);
    }

    this.cuentas.set(correo, {
      password: datos.password,
      usuario: {
        id: this.siguienteId++,
        nombre: datos.nombre,
        email: correo,
        rol: 'cliente',
        // Con crear_cliente la API crea una ficha inactiva; el mock solo asigna su id.
        id_cliente: datos.crear_cliente ? this.siguienteIdCliente++ : null,
      },
    });
  }
}

function esperar(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, RETARDO_MS));
}
