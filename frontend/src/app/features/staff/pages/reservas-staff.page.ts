import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { textoDeError } from '../../../core/http/peticion';
import { ClaseService } from '../../../services/clase.service';
import { ReservasApi } from '../../../services/api/recursos.api';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { ToastComponent } from '../../../shared/components/toast.component';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmTableImports } from '@spartan-ng/helm/table';
import { formatearFechaHora } from '../../../shared/format/fecha';
import { Clase } from '../../../shared/models/clase.model';
import { Reserva } from '../../../shared/models/reserva.model';

interface Fila {
  readonly reserva: Reserva;
  readonly nombreClase: string;
  readonly horario: string;
}

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

/** Reservas del alcance del staff (las de sus clases): cancela y marca asistencia. */
@Component({
  selector: 'app-reservas-staff',
  imports: [RouterLink, ConfirmDialogComponent, ToastComponent, HlmButtonImports, HlmCardImports, HlmTableImports],
  template: `
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-3xl font-semibold">Reservas de mis clases</h1>
      <a hlmBtn variant="outline" routerLink="/staff">Volver al panel</a>
    </div>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando reservas…</p>
    } @else if (filas().length === 0) {
      <p class="text-sm text-muted-foreground">No hay reservas en tus clases.</p>
    } @else {
      <div hlmTableContainer>
        <table hlmTable>
          <thead hlmTHead>
            <tr hlmTr>
              <th hlmTh>ID</th>
              <th hlmTh>Clase</th>
              <th hlmTh>Horario</th>
              <th hlmTh>Reserva</th>
              <th hlmTh>Asistencia</th>
              <th hlmTh>Acciones</th>
            </tr>
          </thead>
          <tbody hlmTBody>
            @for (fila of filas(); track fila.reserva.id_reserva) {
              <tr hlmTr>
                <td hlmTd>{{ fila.reserva.id_reserva }}</td>
                <td hlmTd>{{ fila.nombreClase }}</td>
                <td hlmTd>{{ formatear(fila.horario) }}</td>
                <td hlmTd>{{ formatear(fila.reserva.fecha_reserva) }}</td>
                <td hlmTd>{{ fila.reserva.asistio ? 'Asistió' : 'Pendiente' }}</td>
                <td hlmTd>
                  <div class="flex gap-2">
                    @if (!fila.reserva.asistio) {
                      <button hlmBtn type="button" size="sm" variant="secondary"
                              (click)="marcarAsistencia(fila)">Marcar asistencia</button>
                    }
                    <button hlmBtn type="button" size="sm" variant="destructive"
                            (click)="pendiente.set(fila)">Cancelar</button>
                  </div>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>
      <p class="mt-2 text-sm text-muted-foreground">{{ filas().length }} reservas</p>
    }

    @if (pendiente(); as fila) {
      <app-confirm-dialog
        titulo="Cancelar reserva"
        [mensaje]="'¿Cancelar la reserva #' + fila.reserva.id_reserva + ' de ' + fila.nombreClase + '? La plaza quedará libre.'"
        textoCancelar="Volver"
        textoConfirmar="Sí, cancelar"
        (cancelar)="pendiente.set(null)"
        (confirmar)="cancelar(fila)"
      />
    }
  `,
})
export class ReservasStaffPage {
  private readonly reservasApi = inject(ReservasApi);
  private readonly clases = inject(ClaseService);

  protected readonly formatear = formatearFechaHora;
  protected readonly cargando = signal(true);
  protected readonly filas = signal<Fila[]>([]);
  protected readonly pendiente = signal<Fila | null>(null);
  protected readonly aviso = signal<Aviso | null>(null);

  constructor() {
    void this.cargar();
  }

  protected async marcarAsistencia(fila: Fila): Promise<void> {
    this.aviso.set(null);
    try {
      await this.reservasApi.reemplazar(fila.reserva.id_reserva, {
        id_cliente: fila.reserva.id_cliente,
        id_clase: fila.reserva.id_clase,
        asistio: true,
      });
      this.aviso.set({ mensaje: 'Asistencia registrada', tipo: 'exito' });
      await this.cargar();
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    }
  }

  protected async cancelar(fila: Fila): Promise<void> {
    this.pendiente.set(null);
    this.aviso.set(null);
    try {
      await this.reservasApi.eliminar(fila.reserva.id_reserva);
      this.aviso.set({ mensaje: 'Reserva cancelada', tipo: 'exito' });
      await this.cargar();
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    }
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    try {
      // El alcance de servidor devuelve solo las reservas de las clases del staff.
      const [reservas, clases] = await Promise.all([this.reservasApi.listar(), this.clases.listar()]);
      const porId = new Map(clases.map((c: Clase) => [c.id_clase, c]));
      this.filas.set(
        reservas
          .map((reserva) => {
            const clase = porId.get(reserva.id_clase);
            return clase
              ? { reserva, nombreClase: clase.nombre_clase, horario: clase.horario }
              : null;
          })
          .filter((x): x is Fila => x !== null)
          .sort((a, b) => b.horario.localeCompare(a.horario)),
      );
      this.aviso.set(null);
    } catch (error) {
      this.filas.set([]);
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    } finally {
      this.cargando.set(false);
    }
  }
}
