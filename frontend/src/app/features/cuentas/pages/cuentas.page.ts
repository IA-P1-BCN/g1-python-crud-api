import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HlmBadgeImports } from '@spartan-ng/helm/badge';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { HlmTableImports } from '@spartan-ng/helm/table';
import { textoDeError } from '../../../core/http/peticion';
import { CuentasApi } from '../../../services/api/recursos.api';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { ToastComponent } from '../../../shared/components/toast.component';
import { Cuenta } from '../../../shared/models/cuenta.model';

const ROLES: readonly Cuenta['rol'][] = ['admin', 'staff', 'cliente'];

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

/** Panel de cuentas: listado con filtros, edición PUT y baja (/v1/users, JWT). */
@Component({
  selector: 'app-cuentas',
  imports: [
    ReactiveFormsModule,
    ConfirmDialogComponent,
    ToastComponent,
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
    HlmTableImports,
  ],
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

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    @if (formulario()) {
      <section hlmCard class="mb-4 p-4">
        <h2 class="mb-3 text-lg font-semibold">Editar cuenta</h2>
        <form id="formulario" [formGroup]="form" class="grid gap-3 sm:grid-cols-2" (submit)="guardar($event)">
          <div class="flex flex-col gap-1">
            <label hlmLabel for="nombre-cuenta">Nombre *</label>
            <input hlmInput id="nombre-cuenta" formControlName="nombre" />
            @if (mostrarError('nombre')) {
              <p class="text-sm text-destructive">El nombre es obligatorio (máx. 100 caracteres).</p>
            }
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="email-cuenta">Email *</label>
            <input hlmInput id="email-cuenta" type="email" formControlName="email" />
            @if (mostrarError('email')) {
              <p class="text-sm text-destructive">El email es obligatorio y debe ser válido (máx. 150).</p>
            }
          </div>
          <div class="flex flex-col gap-1 sm:col-span-2">
            <label hlmLabel for="password-cuenta">Contraseña nueva (opcional)</label>
            <input hlmInput id="password-cuenta" type="password" placeholder="Déjala vacía para conservarla" formControlName="password" />
            @if (mostrarError('password')) {
              <p class="text-sm text-destructive">La contraseña debe tener entre 12 y 128 caracteres.</p>
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
      <p class="text-sm text-muted-foreground">Cargando cuentas…</p>
    } @else if (items().length === 0) {
      <p class="text-sm text-muted-foreground">No hay cuentas que coincidan.</p>
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
  protected readonly aviso = signal<Aviso | null>(null);

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
    this.aviso.set(null);
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
    this.aviso.set(null);
    try {
      await this.api.reemplazar(id, {
        nombre: nombre.trim(),
        email: email.trim(),
        ...(password === '' ? {} : { password }),
      });
      this.aviso.set({ mensaje: 'Cuenta actualizada', tipo: 'exito' });
      this.cerrarFormulario();
      await this.cargar();
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    }
  }

  protected async borrar(fila: Cuenta): Promise<void> {
    this.pendiente.set(null);
    this.aviso.set(null);
    try {
      await this.api.eliminar(fila.id);
      this.aviso.set({ mensaje: 'Cuenta eliminada', tipo: 'exito' });
      await this.cargar();
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
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
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    } finally {
      this.cargando.set(false);
    }
  }
}
