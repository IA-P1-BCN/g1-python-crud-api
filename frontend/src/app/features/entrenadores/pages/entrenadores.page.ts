import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideInbox } from '@ng-icons/lucide';
import { toast } from '@spartan-ng/brain/sonner';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmEmptyImports } from '@spartan-ng/helm/empty';
import { HlmFieldImports } from '@spartan-ng/helm/field';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { HlmSkeletonImports } from '@spartan-ng/helm/skeleton';
import { HlmTableImports } from '@spartan-ng/helm/table';
import { textoDeError } from '../../../core/http/peticion';
import { EntrenadoresApi, EntrenadorEntrada } from '../../../services/api/recursos.api';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { Entrenador } from '../../../shared/models/entrenador.model';

/** Gestión de entrenadores: CRUD con filtro de texto (/v1/entrenadores). */
@Component({
  selector: 'app-entrenadores',
  imports: [
    ReactiveFormsModule,
    ConfirmDialogComponent,
    NgIcon,
    HlmButtonImports,
    HlmCardImports,
    HlmEmptyImports,
    HlmFieldImports,
    HlmInputImports,
    HlmLabelImports,
    HlmSkeletonImports,
    HlmTableImports,
  ],
  providers: [provideIcons({ lucideInbox })],
  template: `
    <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
      <h1 class="text-3xl font-semibold">Entrenadores</h1>
      <button hlmBtn type="button" (click)="nuevo()">Nuevo entrenador</button>
    </div>

    <form id="filtros" class="mb-4 flex flex-wrap items-end gap-3" (submit)="buscar($event)">
      <div class="flex flex-col gap-1">
        <label hlmLabel for="q-entrenadores">Buscar</label>
        <input hlmInput id="q-entrenadores" type="search" placeholder="Nombre o especialidad" [formControl]="filtroQ" />
      </div>
      <button hlmBtn type="submit" variant="secondary">Buscar</button>
      <button hlmBtn type="button" variant="ghost" (click)="limpiar()">Limpiar</button>
    </form>

    @if (formulario(); as modo) {
      <section hlmCard class="mb-4 p-4">
        <h2 class="mb-3 text-lg font-semibold">{{ modo === 'crear' ? 'Nuevo entrenador' : 'Editar entrenador' }}</h2>
        <form id="formulario" [formGroup]="form" class="grid gap-3 sm:grid-cols-2" (submit)="guardar($event)">
          <div hlmField>
            <label hlmFieldLabel for="nombre-entrenador">Nombre *</label>
            <input hlmInput id="nombre-entrenador" formControlName="nombre" />
            @if (mostrarError('nombre')) {
              <hlm-field-error>El nombre es obligatorio (máx. 100 caracteres).</hlm-field-error>
            }
          </div>
          <div hlmField>
            <label hlmFieldLabel for="especialidad-entrenador">Especialidad</label>
            <input hlmInput id="especialidad-entrenador" formControlName="especialidad" />
            @if (mostrarError('especialidad')) {
              <hlm-field-error>Máximo 100 caracteres.</hlm-field-error>
            }
          </div>
          <div hlmField>
            <label hlmFieldLabel for="telefono-entrenador">Teléfono</label>
            <input hlmInput id="telefono-entrenador" formControlName="telefono" />
            @if (mostrarError('telefono')) {
              <hlm-field-error>Máximo 20 caracteres.</hlm-field-error>
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
      <div hlmTableContainer>
        <table hlmTable>
          <thead hlmTHead>
            <tr hlmTr>
              <th hlmTh>ID</th>
              <th hlmTh>Nombre</th>
              <th hlmTh>Especialidad</th>
              <th hlmTh>Teléfono</th>
              <th hlmTh>Acciones</th>
            </tr>
          </thead>
          <tbody hlmTBody>
            @for (fila of [1, 2, 3]; track fila) {
              <tr hlmTr>
                @for (col of [1, 2, 3, 4, 5]; track col) {
                  <td hlmTd><span hlmSkeleton class="h-4 w-full"></span></td>
                }
              </tr>
            }
          </tbody>
        </table>
      </div>
    } @else if (items().length === 0) {
      <div hlmEmpty>
        <div hlmEmptyHeader>
          <div hlmEmptyMedia variant="icon"><ng-icon name="lucideInbox" /></div>
          <p hlmEmptyTitle>No hay entrenadores que coincidan.</p>
          <p hlmEmptyDescription>Prueba con otros filtros o crea uno nuevo con «Nuevo entrenador».</p>
        </div>
      </div>
    } @else {
      <div hlmTableContainer>
        <table hlmTable>
          <thead hlmTHead>
            <tr hlmTr>
              <th hlmTh>ID</th>
              <th hlmTh>Nombre</th>
              <th hlmTh>Especialidad</th>
              <th hlmTh>Teléfono</th>
              <th hlmTh>Acciones</th>
            </tr>
          </thead>
          <tbody hlmTBody>
            @for (fila of items(); track fila.id_entrenador) {
              <tr hlmTr>
                <td hlmTd>{{ fila.id_entrenador }}</td>
                <td hlmTd>{{ fila.nombre }}</td>
                <td hlmTd>{{ fila.especialidad ?? '—' }}</td>
                <td hlmTd>{{ fila.telefono ?? '—' }}</td>
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
      <p class="mt-2 text-sm text-muted-foreground">{{ items().length }} entrenadores</p>
    }

    @if (pendiente(); as fila) {
      <app-confirm-dialog
        titulo="Borrar entrenador"
        [mensaje]="'¿Dar de baja a ' + fila.nombre + '? Si imparte clases, la API lo rechazará.'"
        textoCancelar="Volver"
        textoConfirmar="Sí, borrar"
        (cancelar)="pendiente.set(null)"
        (confirmar)="borrar(fila)"
      />
    }
  `,
})
export class EntrenadoresPage {
  private readonly api = inject(EntrenadoresApi);

  protected readonly cargando = signal(true);
  protected readonly items = signal<Entrenador[]>([]);
  protected readonly formulario = signal<'crear' | 'editar' | null>(null);
  protected readonly editandoId = signal<number | null>(null);
  protected readonly pendiente = signal<Entrenador | null>(null);

  protected readonly filtroQ = new FormControl('', { nonNullable: true });

  protected readonly form = new FormGroup({
    nombre: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.maxLength(100)],
    }),
    especialidad: new FormControl('', { nonNullable: true, validators: [Validators.maxLength(100)] }),
    telefono: new FormControl('', { nonNullable: true, validators: [Validators.maxLength(20)] }),
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
    void this.cargar();
  }

  protected nuevo(): void {
    this.form.reset({ nombre: '', especialidad: '', telefono: '' });
    this.editandoId.set(null);
    this.formulario.set('crear');
  }

  protected editar(fila: Entrenador): void {
    this.form.setValue({
      nombre: fila.nombre,
      especialidad: fila.especialidad ?? '',
      telefono: fila.telefono ?? '',
    });
    this.editandoId.set(fila.id_entrenador);
    this.formulario.set('editar');
  }

  protected cerrarFormulario(): void {
    this.formulario.set(null);
    this.editandoId.set(null);
  }

  protected mostrarError(campo: 'nombre' | 'especialidad' | 'telefono'): boolean {
    const control = this.form.controls[campo];
    return control.touched && control.invalid;
  }

  protected async guardar(evento: Event): Promise<void> {
    evento.preventDefault();
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const datos = this.datosDelFormulario();
    const modo = this.formulario();
    try {
      if (modo === 'crear') {
        await this.api.crearEntrenador(datos);
        toast.success('Entrenador creado');
      } else {
        const id = this.editandoId();
        if (id === null) {
          return;
        }
        await this.api.reemplazar(id, datos);
        toast.success('Entrenador actualizado');
      }
      this.cerrarFormulario();
      await this.cargar();
    } catch (error) {
      toast.error(textoDeError(error));
    }
  }

  protected async borrar(fila: Entrenador): Promise<void> {
    this.pendiente.set(null);
    try {
      await this.api.eliminar(fila.id_entrenador);
      toast.success('Entrenador eliminado');
      await this.cargar();
    } catch (error) {
      toast.error(textoDeError(error));
    }
  }

  private datosDelFormulario(): EntrenadorEntrada {
    const { nombre, especialidad, telefono } = this.form.getRawValue();
    return {
      nombre: nombre.trim(),
      especialidad: especialidad.trim() === '' ? null : especialidad.trim(),
      telefono: telefono.trim() === '' ? null : telefono.trim(),
    };
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    const q = this.filtroQ.value.trim();
    try {
      this.items.set(await this.api.listar(q === '' ? {} : { q }));
    } catch (error) {
      this.items.set([]);
      toast.error(textoDeError(error));
    } finally {
      this.cargando.set(false);
    }
  }
}
