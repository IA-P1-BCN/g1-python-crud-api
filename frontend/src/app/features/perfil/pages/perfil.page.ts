import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HlmBadgeImports } from '@spartan-ng/helm/badge';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { SessionService } from '../../../core/auth/session.service';
import { textoDeError } from '../../../core/http/peticion';
import { CuentasApi } from '../../../services/api/recursos.api';
import { ToastComponent } from '../../../shared/components/toast.component';
import { Cuenta } from '../../../shared/models/cuenta.model';

interface Aviso {
  readonly mensaje: string;
  readonly tipo: 'exito' | 'error';
}

/** Perfil propio: consulta GET /v1/users/me y edición con PATCH. */
@Component({
  selector: 'app-perfil',
  imports: [
    ReactiveFormsModule,
    ToastComponent,
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
  ],
  template: `
    <h1 class="mb-4 text-3xl font-semibold">Mi perfil</h1>

    <app-toast [mensaje]="aviso()?.mensaje ?? null" [tipo]="aviso()?.tipo ?? 'exito'" />

    @if (cargando()) {
      <p class="text-sm text-muted-foreground">Cargando perfil…</p>
    } @else if (cuenta(); as datos) {
      <section hlmCard class="mb-6 max-w-2xl p-4">
        <dl class="grid grid-cols-1 gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
          <div class="flex justify-between gap-4 sm:block">
            <dt class="text-muted-foreground">Nombre</dt>
            <dd class="font-medium sm:mt-0.5">{{ datos.nombre }}</dd>
          </div>
          <div class="flex justify-between gap-4 sm:block">
            <dt class="text-muted-foreground">Email</dt>
            <dd class="font-medium sm:mt-0.5">{{ datos.email }}</dd>
          </div>
          <div class="flex justify-between gap-4 sm:block">
            <dt class="text-muted-foreground">Rol</dt>
            <dd class="sm:mt-0.5">
              <span hlmBadge variant="secondary">{{ datos.rol }}</span>
            </dd>
          </div>
          <div class="flex justify-between gap-4 sm:block">
            <dt class="text-muted-foreground">Estado</dt>
            <dd class="font-medium sm:mt-0.5">{{ datos.activo ? 'Activa' : 'Inactiva' }}</dd>
          </div>
          <div class="flex justify-between gap-4 sm:block">
            <dt class="text-muted-foreground">Ficha de cliente</dt>
            <dd class="font-medium sm:mt-0.5">{{ datos.id_cliente ?? 'Sin vincular' }}</dd>
          </div>
          <div class="flex justify-between gap-4 sm:block">
            <dt class="text-muted-foreground">Creada</dt>
            <dd class="font-medium sm:mt-0.5">{{ datos.fecha_creacion }}</dd>
          </div>
        </dl>
      </section>

      <section hlmCard class="max-w-2xl p-4">
        <h2 class="mb-3 text-lg font-semibold">Editar mis datos</h2>
        <form id="formulario" [formGroup]="form" class="grid gap-3" (submit)="guardar($event)">
          <div class="flex flex-col gap-1">
            <label hlmLabel for="nombre-perfil">Nombre *</label>
            <input hlmInput id="nombre-perfil" formControlName="nombre" />
            @if (mostrarError('nombre')) {
              <p class="text-sm text-destructive">
                El nombre es obligatorio (máx. 100 caracteres).
              </p>
            }
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="email-perfil">Email *</label>
            <input hlmInput id="email-perfil" type="email" formControlName="email" />
            @if (mostrarError('email')) {
              <p class="text-sm text-destructive">
                El email es obligatorio y debe ser válido (máx. 150).
              </p>
            }
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="password-perfil">Contraseña nueva (opcional)</label>
            <input
              hlmInput
              id="password-perfil"
              type="password"
              placeholder="Déjala vacía para conservarla"
              formControlName="password"
            />
            @if (mostrarError('password')) {
              <p class="text-sm text-destructive">
                La contraseña debe tener entre 12 y 128 caracteres.
              </p>
            }
          </div>
          <div class="flex flex-col gap-1">
            <label hlmLabel for="current-password-perfil">Contraseña actual (para cambiarla)</label>
            <input
              hlmInput
              id="current-password-perfil"
              type="password"
              autocomplete="current-password"
              formControlName="current_password"
            />
            @if (mostrarError('current_password')) {
              <p class="text-sm text-destructive">
                Introduce tu contraseña actual (máx. 128 caracteres).
              </p>
            }
          </div>
          <div class="flex gap-2">
            <button hlmBtn type="submit">Guardar cambios</button>
          </div>
        </form>
      </section>
    }
  `,
})
export class PerfilPage {
  private readonly api = inject(CuentasApi);
  private readonly session = inject(SessionService);

  protected readonly cargando = signal(true);
  protected readonly cuenta = signal<Cuenta | null>(null);
  protected readonly aviso = signal<Aviso | null>(null);

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
    current_password: new FormControl('', {
      nonNullable: true,
      validators: [Validators.maxLength(128)],
    }),
  });

  constructor() {
    void this.cargar();
  }

  protected mostrarError(campo: 'nombre' | 'email' | 'password' | 'current_password'): boolean {
    const control = this.form.controls[campo];
    return control.touched && control.invalid;
  }

  protected async guardar(evento: Event): Promise<void> {
    evento.preventDefault();
    this.form.controls.current_password.updateValueAndValidity();
    if (
      this.form.controls.password.value !== '' &&
      this.form.controls.current_password.value === ''
    ) {
      this.form.controls.current_password.setErrors({ required: true });
    }
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const actual = this.cuenta();
    if (actual === null) {
      return;
    }
    const { nombre, email, password, current_password } = this.form.getRawValue();
    this.aviso.set(null);
    try {
      const actualizado = await this.api.actualizarYo({
        nombre: nombre.trim(),
        email: email.trim(),
        ...(password === '' ? {} : { password, current_password }),
      });
      this.aplicar(actualizado);
      this.aviso.set({ mensaje: 'Perfil actualizado', tipo: 'exito' });
      this.form.controls.password.setValue('');
    } catch (error) {
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    }
  }

  private aplicar(actualizado: Cuenta): void {
    this.cuenta.set(actualizado);
    this.form.setValue({
      nombre: actualizado.nombre,
      email: actualizado.email,
      password: '',
      current_password: '',
    });
    const usuario = this.session.usuario();
    if (usuario !== null) {
      this.session.iniciar({ ...usuario, nombre: actualizado.nombre, email: actualizado.email });
    }
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    try {
      const yo = await this.api.yo();
      this.cuenta.set(yo);
      this.form.setValue({
        nombre: yo.nombre,
        email: yo.email,
        password: '',
        current_password: '',
      });
    } catch (error) {
      this.cuenta.set(null);
      this.aviso.set({ mensaje: textoDeError(error), tipo: 'error' });
    } finally {
      this.cargando.set(false);
    }
  }
}
