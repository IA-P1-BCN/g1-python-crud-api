import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { HlmTableImports } from '@spartan-ng/helm/table';
import { textoDeError } from '../../../core/http/peticion';
import { ClasesApi, ClaseEntrada, EntrenadoresApi } from '../../../services/api/recursos.api';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { ToastComponent } from '../../../shared/components/toast.component';
import { formatearFechaHora } from '../../../shared/format/fecha';
import { Clase } from '../../../shared/models/clase.model';
import { Entrenador } from '../../../shared/models/entrenador.model';

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

/** Gestión de clases: CRUD con entrenador y horario UTC (/v1/clases). */
@Component({
  selector: 'app-gestion-clases',
  imports: [
    ReactiveFormsModule,
    ConfirmDialogComponent,
    ToastComponent,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
    HlmTableImports,
  ],
  template: `
    <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
      <h1 class="text-3xl font-semibold">Gestión de clases</h1>
      <button hlmBtn type="button" (click)="nuevaClase()">Nueva clase</button>
    </div>

    <form id="filtros" class="mb-4 flex flex-wrap items-end gap-3" (submit)="buscar($event)">
      <div class="flex flex-col gap-1">
        <label hlmLabel for="q-clases">Buscar</label>
        <input hlmInput id="q-clases" type="search" placeholder="Nombre de la clase" [formControl]="filtroQ" />
      </div>
      <button hlmBtn type="submit" variant="secondary">Buscar</button>
      <button hlmBtn type="button" variant="ghost" (click)="limpiar()">Limpiar</button>
    </form>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    @if (formulario(); as modo) {
      <section hlmCard class="mb-4 p-4">
        <h2 class="mb-3 text-lg font-semibold">{{ modo === 'crear' ? 'Nueva clase' : 'Editar clase' }}</h2>
        <form id="formulario" [formGroup]="form" class="grid gap-3 sm:grid-cols-2" (submit)="guardar($event)">
          <div class="flex flex-col gap-1">
            <label hlmLabel for="nombre-clase">Nombre *</label>
            <input hlmInput id="nombre-clase" formControlName="nombre_clase" />
            @if (mostrarError('nombre_clase')) {
              <p class="text-sm text-destructive">El nombre es obligatorio (máx. 50 caracteres).</p>
            }
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="horario-clase">Horario (UTC) *</label>
            <input hlmInput id="horario-clase" type="datetime-local" formControlName="horario" />
            @if (mostrarError('horario')) {
              <p class="text-sm text-destructive">El horario es obligatorio.</p>
            }
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="capacidad-clase">Capacidad máxima *</label>
            <input hlmInput id="capacidad-clase" type="number" formControlName="capacidad_max" />
            @if (mostrarError('capacidad_max')) {
              <p class="text-sm text-destructive">La capacidad debe ser un número mayor que cero.</p>
            }
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="entrenador-clase">Entrenador *</label>
            <select hlmInput id="entrenador-clase" formControlName="id_entrenador">
              <option value="">Elige un entrenador</option>
              @for (entrenador of entrenadores(); track entrenador.id_entrenador) {
                <option [value]="idTexto(entrenador.id_entrenador)">{{ entrenador.nombre }}</option>
              }
            </select>
            @if (mostrarError('id_entrenador')) {
              <p class="text-sm text-destructive">El entrenador es obligatorio.</p>
            } @else if (entrenadores().length === 0) {
              <p class="text-sm text-muted-foreground">No hay entrenadores: da de alta alguno primero.</p>
            }
          </div>
          <div class="flex gap-2 sm:col-span-2">
            <button hlmBtn type="submit">{{ modo === 'crear' ? 'Crear' : 'Guardar' }}</button>
            <button hlmBtn type="button" variant="ghost" (click)="cerrarFormulario()">Cancelar</button>
          </div>
        </form>
      </section>
    }

    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando clases…</p>
    } @else if (items().length === 0) {
      <p class="text-sm text-muted-foreground">No hay clases que coincidan.</p>
    } @else {
      <div hlmTableContainer>
        <table hlmTable>
          <thead hlmTHead>
            <tr hlmTr>
              <th hlmTh>ID</th>
              <th hlmTh>Clase</th>
              <th hlmTh>Horario</th>
              <th hlmTh>Capacidad</th>
              <th hlmTh>Entrenador</th>
              <th hlmTh>Acciones</th>
            </tr>
          </thead>
          <tbody hlmTBody>
            @for (fila of items(); track fila.id_clase) {
              <tr hlmTr>
                <td hlmTd>{{ fila.id_clase }}</td>
                <td hlmTd>{{ fila.nombre_clase }}</td>
                <td hlmTd>{{ formatear(fila.horario) }}</td>
                <td hlmTd>{{ fila.capacidad_max }}</td>
                <td hlmTd>{{ nombreEntrenador(fila.id_entrenador) }}</td>
                <td hlmTd>
                  <div class="flex gap-2">
                    <button hlmBtn type="button" size="sm" variant="secondary" (click)="editar(fila)">Editar</button>
                    <button hlmBtn type="button" size="sm" variant="destructive" (click)="pendiente.set(fila)">
                      Borrar
                    </button>
                  </div>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>
      <p class="mt-2 text-sm text-muted-foreground">{{ items().length }} clases</p>
    }

    @if (pendiente(); as fila) {
      <app-confirm-dialog
        titulo="Borrar clase"
        [mensaje]="'¿Dar de baja la clase ' + fila.nombre_clase + '? Si tiene reservas, la API lo rechazará.'"
        textoCancelar="Volver"
        textoConfirmar="Sí, borrar"
        (cancelar)="pendiente.set(null)"
        (confirmar)="borrar(fila)"
      />
    }
  `,
})
export class GestionClasesPage {
  private readonly clases = inject(ClasesApi);
  private readonly entrenadoresApi = inject(EntrenadoresApi);

  protected readonly formatear = formatearFechaHora;
  protected readonly cargando = signal(true);
  protected readonly items = signal<Clase[]>([]);
  protected readonly entrenadores = signal<Entrenador[]>([]);
  protected readonly formulario = signal<'crear' | 'editar' | null>(null);
  protected readonly editandoId = signal<number | null>(null);
  protected readonly pendiente = signal<Clase | null>(null);
  protected readonly aviso = signal<Aviso | null>(null);

  protected readonly filtroQ = new FormControl('', { nonNullable: true });

  protected readonly form = new FormGroup({
    nombre_clase: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.maxLength(50)],
    }),
    horario: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    capacidad_max: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.pattern(/^\d{1,9}$/), Validators.min(1)],
    }),
    id_entrenador: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });

  constructor() {
    void this.cargar();
  }

  protected nombreEntrenador(id: number): string {
    return this.entrenadores().find((e) => e.id_entrenador === id)?.nombre ?? `#${id}`;
  }

  protected buscar(evento: Event): void {
    evento.preventDefault();
    void this.cargar();
  }

  protected limpiar(): void {
    this.filtroQ.setValue('');
    void this.cargar();
  }

  protected nuevaClase(): void {
    this.form.reset({ nombre_clase: '', horario: '', capacidad_max: '', id_entrenador: '' });
    this.editandoId.set(null);
    this.aviso.set(null);
    this.formulario.set('crear');
  }

  protected editar(fila: Clase): void {
    this.form.setValue({
      nombre_clase: fila.nombre_clase,
      horario: fila.horario.slice(0, 16),
      capacidad_max: String(fila.capacidad_max),
      id_entrenador: String(fila.id_entrenador),
    });
    this.editandoId.set(fila.id_clase);
    this.aviso.set(null);
    this.formulario.set('editar');
  }

  protected cerrarFormulario(): void {
    this.formulario.set(null);
    this.editandoId.set(null);
  }

  protected mostrarError(campo: 'nombre_clase' | 'horario' | 'capacidad_max' | 'id_entrenador'): boolean {
    const control = this.form.controls[campo];
    return control.touched && control.invalid;
  }

  protected idTexto(id: number): string {
    return String(id);
  }

  protected async guardar(evento: Event): Promise<void> {
    evento.preventDefault();
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const datos = this.datosDelFormulario();
    const modo = this.formulario();
    this.aviso.set(null);
    try {
      if (modo === 'crear') {
        await this.clases.crearClase(datos);
        this.aviso.set({ mensaje: 'Clase creada', tipo: 'exito' });
      } else {
        const id = this.editandoId();
        if (id === null) {
          return;
        }
        await this.clases.reemplazar(id, datos);
        this.aviso.set({ mensaje: 'Clase actualizada', tipo: 'exito' });
      }
      this.cerrarFormulario();
      await this.cargar();
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    }
  }

  protected async borrar(fila: Clase): Promise<void> {
    this.pendiente.set(null);
    this.aviso.set(null);
    try {
      await this.clases.eliminar(fila.id_clase);
      this.aviso.set({ mensaje: 'Clase eliminada', tipo: 'exito' });
      await this.cargar();
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    }
  }

  private datosDelFormulario(): ClaseEntrada {
    const { nombre_clase, horario, capacidad_max, id_entrenador } = this.form.getRawValue();
    return {
      nombre_clase: nombre_clase.trim(),
      horario: `${horario}:00`,
      capacidad_max: Number(capacidad_max),
      id_entrenador: Number(id_entrenador),
    };
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    const q = this.filtroQ.value.trim();
    try {
      const [clases, entrenadores] = await Promise.all([
        this.clases.listar(q === '' ? {} : { q }),
        this.entrenadoresApi.listar(),
      ]);
      this.items.set(clases);
      this.entrenadores.set(entrenadores);
    } catch (error) {
      this.items.set([]);
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    } finally {
      this.cargando.set(false);
    }
  }
}
