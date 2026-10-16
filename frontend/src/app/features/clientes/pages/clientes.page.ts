import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { HlmTableImports } from '@spartan-ng/helm/table';
import { textoDeError } from '../../../core/http/peticion';
import { ClientesApi, ClienteEntrada } from '../../../services/api/recursos.api';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { EstadoBadgeComponent } from '../../../shared/components/estado-badge.component';
import { ToastComponent } from '../../../shared/components/toast.component';
import { EstadoMembresia, Cliente } from '../../../shared/models/cliente.model';

const ESTADOS: readonly EstadoMembresia[] = ['Activo', 'Inactivo', 'Suspendido'];

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

/** Gestión de clientes: listado con filtros, alta, edición y baja (/v1/clientes). */
@Component({
  selector: 'app-clientes',
  imports: [
    ReactiveFormsModule,
    ConfirmDialogComponent,
    EstadoBadgeComponent,
    ToastComponent,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
    HlmTableImports,
  ],
  template: `
    <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
      <h1 class="text-3xl font-semibold">Clientes</h1>
      <button hlmBtn type="button" (click)="nuevo()">Nuevo cliente</button>
    </div>

    <form id="filtros" class="mb-4 flex flex-wrap items-end gap-3" (submit)="buscar($event)">
      <div class="flex flex-col gap-1">
        <label hlmLabel for="q-clientes">Buscar</label>
        <input hlmInput id="q-clientes" type="search" placeholder="Nombre o email" [formControl]="filtroQ" />
      </div>
      <div class="flex flex-col gap-1">
        <label hlmLabel for="estado-clientes">Estado</label>
        <select hlmInput id="estado-clientes" [formControl]="filtroEstado">
          <option value="">Todos</option>
          @for (estado of estados; track estado) {
            <option [value]="estado">{{ estado }}</option>
          }
        </select>
      </div>
      <button hlmBtn type="submit" variant="secondary">Buscar</button>
      <button hlmBtn type="button" variant="ghost" (click)="limpiar()">Limpiar</button>
    </form>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    @if (formulario(); as modo) {
      <section hlmCard class="mb-4 p-4">
        <h2 class="mb-3 text-lg font-semibold">{{ modo === 'crear' ? 'Nuevo cliente' : 'Editar cliente' }}</h2>
        <form id="formulario" [formGroup]="form" class="grid gap-3 sm:grid-cols-2" (submit)="guardar($event)">
          <div class="flex flex-col gap-1">
            <label hlmLabel for="nombre-cliente">Nombre *</label>
            <input hlmInput id="nombre-cliente" formControlName="nombre" />
            @if (mostrarError('nombre')) {
              <p class="text-sm text-destructive">El nombre es obligatorio (máx. 100 caracteres).</p>
            }
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="email-cliente">Email</label>
            <input hlmInput id="email-cliente" type="email" formControlName="email" />
            @if (mostrarError('email')) {
              <p class="text-sm text-destructive">El email no tiene un formato válido (máx. 150).</p>
            }
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="membresia-cliente">Estado de membresía *</label>
            <select hlmInput id="membresia-cliente" formControlName="estado_membresia">
              @for (estado of estados; track estado) {
                <option [value]="estado">{{ estado }}</option>
              }
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="fecha-cliente">Fecha de inscripción</label>
            <input hlmInput id="fecha-cliente" type="date" formControlName="fecha_inscripcion" />
          </div>
          <div class="flex gap-2 sm:col-span-2">
            <button hlmBtn type="submit">{{ modo === 'crear' ? 'Crear' : 'Guardar' }}</button>
            <button hlmBtn type="button" variant="ghost" (click)="cerrarFormulario()">Cancelar</button>
          </div>
        </form>
      </section>
    }

    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando clientes…</p>
    } @else if (items().length === 0) {
      <p class="text-sm text-muted-foreground">No hay clientes que coincidan.</p>
    } @else {
      <div hlmTableContainer>
        <table hlmTable>
          <thead hlmTHead>
            <tr hlmTr>
              <th hlmTh>ID</th>
              <th hlmTh>Nombre</th>
              <th hlmTh>Email</th>
              <th hlmTh>Estado</th>
              <th hlmTh>Inscripción</th>
              <th hlmTh>Acciones</th>
            </tr>
          </thead>
          <tbody hlmTBody>
            @for (fila of items(); track fila.id_cliente) {
              <tr hlmTr>
                <td hlmTd>{{ fila.id_cliente }}</td>
                <td hlmTd>{{ fila.nombre }}</td>
                <td hlmTd>{{ fila.email ?? '—' }}</td>
                <td hlmTd><app-estado-badge [estado]="fila.estado_membresia" /></td>
                <td hlmTd>{{ fila.fecha_inscripcion ?? '—' }}</td>
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
      <p class="mt-2 text-sm text-muted-foreground">{{ items().length }} clientes</p>
    }

    @if (pendiente(); as fila) {
      <app-confirm-dialog
        titulo="Borrar cliente"
        [mensaje]="'¿Dar de baja a ' + fila.nombre + '? Si tiene reservas, pagos o cuenta, la API lo rechazará.'"
        textoCancelar="Volver"
        textoConfirmar="Sí, borrar"
        (cancelar)="pendiente.set(null)"
        (confirmar)="borrar(fila)"
      />
    }
  `,
})
export class ClientesPage {
  private readonly api = inject(ClientesApi);

  protected readonly estados = ESTADOS;
  protected readonly cargando = signal(true);
  protected readonly items = signal<Cliente[]>([]);
  protected readonly formulario = signal<'crear' | 'editar' | null>(null);
  protected readonly editandoId = signal<number | null>(null);
  protected readonly pendiente = signal<Cliente | null>(null);
  protected readonly aviso = signal<Aviso | null>(null);

  protected readonly filtroQ = new FormControl('', { nonNullable: true });
  protected readonly filtroEstado = new FormControl('', { nonNullable: true });

  protected readonly form = new FormGroup({
    nombre: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.maxLength(100)],
    }),
    email: new FormControl('', {
      nonNullable: true,
      validators: [Validators.email, Validators.maxLength(150)],
    }),
    estado_membresia: new FormControl<EstadoMembresia>('Activo', {
      nonNullable: true,
      validators: [Validators.required],
    }),
    fecha_inscripcion: new FormControl('', { nonNullable: true }),
  });

  constructor() {
    void this.cargar();
  }

  protected buscar(evento: Event): void {
    evento.preventDefault();
    void this.cargar();
  }

  protected limpiar(): void {
    this.filtroQ.setValue('');
    this.filtroEstado.setValue('');
    void this.cargar();
  }

  protected nuevo(): void {
    this.form.reset({ nombre: '', email: '', estado_membresia: 'Activo', fecha_inscripcion: '' });
    this.editandoId.set(null);
    this.aviso.set(null);
    this.formulario.set('crear');
  }

  protected editar(fila: Cliente): void {
    this.form.setValue({
      nombre: fila.nombre,
      email: fila.email ?? '',
      estado_membresia: fila.estado_membresia,
      fecha_inscripcion: fila.fecha_inscripcion ?? '',
    });
    this.editandoId.set(fila.id_cliente);
    this.aviso.set(null);
    this.formulario.set('editar');
  }

  protected cerrarFormulario(): void {
    this.formulario.set(null);
    this.editandoId.set(null);
  }

  protected mostrarError(campo: 'nombre' | 'email'): boolean {
    const control = this.form.controls[campo];
    return control.touched && control.invalid;
  }

  protected async guardar(evento: Event): Promise<void> {
    evento.preventDefault();
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const datos: ClienteEntrada = this.datosDelFormulario();
    const modo = this.formulario();
    this.aviso.set(null);
    try {
      if (modo === 'crear') {
        await this.api.crearCliente(datos);
        this.aviso.set({ mensaje: 'Cliente creado', tipo: 'exito' });
      } else {
        const id = this.editandoId();
        if (id === null) {
          return;
        }
        await this.api.reemplazar(id, datos);
        this.aviso.set({ mensaje: 'Cliente actualizado', tipo: 'exito' });
      }
      this.cerrarFormulario();
      await this.cargar();
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    }
  }

  protected async borrar(fila: Cliente): Promise<void> {
    this.pendiente.set(null);
    this.aviso.set(null);
    try {
      await this.api.eliminar(fila.id_cliente);
      this.aviso.set({ mensaje: 'Cliente eliminado', tipo: 'exito' });
      await this.cargar();
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    }
  }

  private datosDelFormulario(): ClienteEntrada {
    const { nombre, email, estado_membresia, fecha_inscripcion } = this.form.getRawValue();
    return {
      nombre: nombre.trim(),
      email: email.trim() === '' ? null : email.trim(),
      estado_membresia,
      fecha_inscripcion: fecha_inscripcion === '' ? null : fecha_inscripcion,
    };
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    const q = this.filtroQ.value.trim();
    const estado = this.filtroEstado.value;
    try {
      this.items.set(
        await this.api.listar({
          ...(q === '' ? {} : { q }),
          ...(estado === '' ? {} : { estado_membresia: estado }),
        }),
      );
    } catch (error) {
      this.items.set([]);
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    } finally {
      this.cargando.set(false);
    }
  }
}
