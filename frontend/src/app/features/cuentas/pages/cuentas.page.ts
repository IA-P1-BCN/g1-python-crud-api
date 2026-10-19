import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideInbox } from '@ng-icons/lucide';
import { toast } from '@spartan-ng/brain/sonner';
import { HlmBadgeImports } from '@spartan-ng/helm/badge';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmEmptyImports } from '@spartan-ng/helm/empty';
import { HlmFieldImports } from '@spartan-ng/helm/field';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { HlmSkeletonImports } from '@spartan-ng/helm/skeleton';
import { HlmTableImports } from '@spartan-ng/helm/table';
import { textoDeError } from '../../../core/http/peticion';
import { CuentasApi } from '../../../services/api/recursos.api';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { Cuenta } from '../../../shared/models/cuenta.model';

const ROLES: readonly Cuenta['rol'][] = ['admin', 'staff', 'cliente'];

/** Panel de cuentas: listado con filtros, edición PUT y baja (/v1/users, JWT). */
@Component({
  selector: 'app-cuentas',
  imports: [
    ReactiveFormsModule,
    ConfirmDialogComponent,
    NgIcon,
    HlmBadgeImports,
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
      <h1 class="text-3xl font-semibold">Cuentas</h1>
    </div>

    <form id="filtros" class="mb-4 flex flex-wrap items-end gap-3" (submit)="buscar($event)">
      <div class="flex flex-col gap-1">
        <label hlmLabel for="q-cuentas">Buscar</label>
        <input hlmInput id="q-cuentas" type="search" placeholder="Nombre o email" [formControl]="filtroQ" />
      </div>
      <div class="flex flex-col gap-1">
        <label hlmLabel for="rol-cuentas">Rol</label>
        <select hlmInput id="rol-cuentas" [formControl]="filtroRol">
          <option value="">Todos</option>
          @for (rol of roles; track rol) {
            <option [value]="rol">{{ rol }}</option>
          }
        </select>
      </div>
      <div class="flex flex-col gap-1">
        <label hlmLabel for="activo-cuentas">Activo</label>
        <select hlmInput id="activo-cuentas" [formControl]="filtroActivo">
          <option value="">Todos</option>
          <option value="true">Activo</option>
          <option value="false">Inactivo</option>
        </select>
      </div>
      <button hlmBtn type="submit" variant="secondary">Buscar</button>
      <button hlmBtn type="button" variant="ghost" (click)="limpiar()">Limpiar</button>
    </form>

    @if (formulario()) {
      <section hlmCard class="mb-4 p-4">
        <h2 class="mb-3 text-lg font-semibold">Editar cuenta</h2>
        <form id="formulario" [formGroup]="form" class="grid gap-3 sm:grid-cols-2" (submit)="guardar($event)">
          <div hlmField>
            <label hlmFieldLabel for="nombre-cuenta">Nombre *</label>
            <input hlmInput id="nombre-cuenta" formControlName="nombre" />
            @if (mostrarError('nombre')) {
              <hlm-field-error>El nombre es obligatorio (máx. 100 caracteres).</hlm-field-error>
            }
          </div>
          <div hlmField>
            <label hlmFieldLabel for="email-cuenta">Email *</label>
            <input hlmInput id="email-cuenta" type="email" formControlName="email" />
            @if (mostrarError('email')) {
              <hlm-field-error>El email es obligatorio y debe ser válido (máx. 150).</hlm-field-error>
            }
          </div>
          <div hlmField class="sm:col-span-2">
            <label hlmFieldLabel for="password-cuenta">Contraseña nueva (opcional)</label>
            <input hlmInput id="password-cuenta" type="password" placeholder="Déjala vacía para conservarla" formControlName="password" />
            @if (mostrarError('password')) {
              <hlm-field-error>La contraseña debe tener entre 12 y 128 caracteres.</hlm-field-error>
            }
          </div>
          <p class="text-sm text-muted-foreground sm:col-span-2">
            Rol, estado y vínculo con cliente no se editan aquí.
          </p>
          <div class="flex gap-2 sm:col-span-2">
            <button hlmBtn type="submit">Guardar</button>
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
              <th hlmTh>Email</th>
              <th hlmTh>Rol</th>
              <th hlmTh>Activa</th>
              <th hlmTh>Cliente</th>
              <th hlmTh>Creada</th>
              <th hlmTh>Acciones</th>
            </tr>
          </thead>
          <tbody hlmTBody>
            @for (fila of [1, 2, 3]; track fila) {
              <tr hlmTr>
                @for (col of [1, 2, 3, 4, 5, 6, 7, 8]; track col) {
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
          <p hlmEmptyTitle>No hay cuentas que coincidan.</p>
          <p hlmEmptyDescription>Prueba con otros filtros o ajusta la búsqueda.</p>
        </div>
      </div>
    } @else {
      <div hlmTableContainer>
        <table hlmTable>
          <thead hlmTHead>
            <tr hlmTr>
              <th hlmTh>ID</th>
              <th hlmTh>Nombre</th>
              <th hlmTh>Email</th>
              <th hlmTh>Rol</th>
              <th hlmTh>Activa</th>
              <th hlmTh>Cliente</th>
              <th hlmTh>Creada</th>
              <th hlmTh>Acciones</th>
            </tr>
          </thead>
          <tbody hlmTBody>
            @for (fila of items(); track fila.id) {
              <tr hlmTr>
                <td hlmTd>{{ fila.id }}</td>
                <td hlmTd>{{ fila.nombre }}</td>
                <td hlmTd>{{ fila.email }}</td>
                <td hlmTd><span hlmBadge variant="secondary">{{ fila.rol }}</span></td>
                <td hlmTd>{{ fila.activo ? 'Sí' : 'No' }}</td>
                <td hlmTd>{{ fila.id_cliente ?? '—' }}</td>
                <td hlmTd>{{ fila.fecha_creacion }}</td>
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
      <p class="mt-2 text-sm text-muted-foreground">{{ items().length }} cuentas</p>
    }

    @if (pendiente(); as fila) {
      <app-confirm-dialog
        titulo="Borrar cuenta"
        [mensaje]="'¿Dar de baja la cuenta de ' + fila.nombre + '? Se borra de forma permanente; su ficha de cliente y su historial se conservan.'"
        textoCancelar="Volver"
        textoConfirmar="Sí, borrar"
        (cancelar)="pendiente.set(null)"
        (confirmar)="borrar(fila)"
      />
    }
  `,
})
export class CuentasPage {
  private readonly api = inject(CuentasApi);

  protected readonly roles = ROLES;
  protected readonly cargando = signal(true);
  protected readonly items = signal<Cuenta[]>([]);
  protected readonly formulario = signal(false);
  protected readonly editandoId = signal<number | null>(null);
  protected readonly pendiente = signal<Cuenta | null>(null);

  protected readonly filtroQ = new FormControl('', { nonNullable: true });
  protected readonly filtroRol = new FormControl('', { nonNullable: true });
  protected readonly filtroActivo = new FormControl('', { nonNullable: true });

  protected readonly form = new FormGroup({
    nombre: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.maxLength(100)],
    }),
    email: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.email, Validators.maxLength(150)],
    }),
    password: new FormControl('', {
      nonNullable: true,
      validators: [Validators.minLength(12), Validators.maxLength(128)],
    }),
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
    this.filtroRol.setValue('');
    this.filtroActivo.setValue('');
    void this.cargar();
  }

  protected editar(fila: Cuenta): void {
    this.form.setValue({ nombre: fila.nombre, email: fila.email, password: '' });
    this.editandoId.set(fila.id);
    this.formulario.set(true);
  }

  protected cerrarFormulario(): void {
    this.formulario.set(false);
    this.editandoId.set(null);
  }

  protected mostrarError(campo: 'nombre' | 'email' | 'password'): boolean {
    const control = this.form.controls[campo];
    return control.touched && control.invalid;
  }

  protected async guardar(evento: Event): Promise<void> {
    evento.preventDefault();
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const id = this.editandoId();
    if (id === null) {
      return;
    }
    const { nombre, email, password } = this.form.getRawValue();
    try {
      await this.api.reemplazar(id, {
        nombre: nombre.trim(),
        email: email.trim(),
        ...(password === '' ? {} : { password }),
      });
      toast.success('Cuenta actualizada');
      this.cerrarFormulario();
      await this.cargar();
    } catch (error) {
      toast.error(textoDeError(error));
    }
  }

  protected async borrar(fila: Cuenta): Promise<void> {
    this.pendiente.set(null);
    try {
      await this.api.eliminar(fila.id);
      toast.success('Cuenta eliminada');
      await this.cargar();
    } catch (error) {
      toast.error(textoDeError(error));
    }
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    const q = this.filtroQ.value.trim();
    const rol = this.filtroRol.value;
    const activo = this.filtroActivo.value;
    try {
      this.items.set(
        await this.api.listar({
          ...(q === '' ? {} : { q }),
          ...(rol === '' ? {} : { rol }),
          ...(activo === '' ? {} : { activo: activo === 'true' }),
        }),
      );
    } catch (error) {
      this.items.set([]);
      toast.error(textoDeError(error));
    } finally {
      this.cargando.set(false);
    }
  }
}
