import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { ejecutar, RUTA_API } from '../../core/http/peticion';
import { Clase, CupoClase } from '../../shared/models/clase.model';
import { Cliente } from '../../shared/models/cliente.model';
import { Cuenta, CuentaPut, CuentaSelfPatch } from '../../shared/models/cuenta.model';
import { Entrenador } from '../../shared/models/entrenador.model';
import { Pago, PagoEntrada } from '../../shared/models/pago.model';
import { Reserva } from '../../shared/models/reserva.model';
import { RecursoApi } from './recurso.api';

/** Datos de entrada que aceptan los recursos (espejo de los *Input de la API). */
export interface ClienteEntrada {
  readonly nombre: string;
  readonly email: string | null;
  readonly estado_membresia: Cliente['estado_membresia'];
  readonly fecha_inscripcion: string | null;
}

export interface EntrenadorEntrada {
  readonly nombre: string;
  readonly especialidad: string | null;
  readonly telefono: string | null;
}

export interface ClaseEntrada {
  readonly nombre_clase: string;
  readonly horario: string;
  readonly capacidad_max: number;
  readonly id_entrenador: number;
}

export interface ReservaEntrada {
  readonly id_cliente: number;
  readonly id_clase: number;
  readonly asistio: boolean;
}

@Injectable({ providedIn: 'root' })
export class ClientesApi extends RecursoApi<Cliente, ClienteEntrada> {
  protected readonly ruta = '/clientes';
  crearCliente(datos: ClienteEntrada): Promise<Cliente> {
    return this.crear(datos);
  }
}

@Injectable({ providedIn: 'root' })
export class EntrenadoresApi extends RecursoApi<Entrenador, EntrenadorEntrada> {
  protected readonly ruta = '/entrenadores';
  /** Con email, la API crea también la Cuenta staff en la misma transacción (#134). */
  crearEntrenador(datos: EntrenadorEntrada & { email?: string }): Promise<Entrenador> {
    return this.crear(datos);
  }
}

@Injectable({ providedIn: 'root' })
export class ClasesApi extends RecursoApi<Clase, ClaseEntrada> {
  protected readonly ruta = '/clases';
  cupo(id: number): Promise<CupoClase> {
    return ejecutar(this.http.get<CupoClase>(this.url(`/${id}/cupo`)));
  }

  crearClase(datos: ClaseEntrada): Promise<Clase> {
    return this.crear(datos);
  }
}

@Injectable({ providedIn: 'root' })
export class ReservasApi extends RecursoApi<Reserva, ReservaEntrada> {
  protected readonly ruta = '/reservas';
  crearReserva(datos: ReservaEntrada): Promise<Reserva> {
    return this.crear(datos);
  }
}

@Injectable({ providedIn: 'root' })
export class PagosApi extends RecursoApi<Pago, PagoEntrada> {
  protected readonly ruta = '/pagos';
  crearPago(datos: PagoEntrada): Promise<Pago> {
    return this.crear(datos);
  }
}

/**
 * Cuentas (/v1/users). El alta no está aquí: se hace por /v1/auth/register.
 * Edición parcial (PATCH) y el perfil propio (/me).
 */
@Injectable({ providedIn: 'root' })
export class CuentasApi extends RecursoApi<Cuenta, CuentaPut> {
  protected readonly ruta = '/users';

  /** Perfil de la Cuenta autenticada (requiere token). */
  yo(): Promise<Cuenta> {
    return ejecutar(this.http.get<Cuenta>(this.url('/me')));
  }

  actualizarYo(cambios: CuentaSelfPatch): Promise<Cuenta> {
    return ejecutar(this.http.patch<Cuenta>(this.url('/me'), cambios));
  }

  parchear(id: number, cambios: Partial<CuentaPut>): Promise<Cuenta> {
    return ejecutar(this.http.patch<Cuenta>(this.url(`/${id}`), cambios));
  }
}

/** Tablas exportables a CSV por GET /v1/export/csv?tablas=<tabla>. */
export type TablaExportable = 'clientes' | 'entrenadores' | 'clases' | 'reservas' | 'pagos';

@Injectable({ providedIn: 'root' })
export class ExportApi {
  private readonly http = inject(HttpClient);

  /** Devuelve el CSV (con BOM UTF-8) de la tabla indicada. */
  exportarCsv(tabla: TablaExportable): Promise<string> {
    return ejecutar(
      this.http.get(`${RUTA_API}/export/csv`, {
        params: { tablas: tabla },
        responseType: 'text',
      }),
    );
  }
}
