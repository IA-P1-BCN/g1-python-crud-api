import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgIcon } from '@ng-icons/core';
import { toast } from '@spartan-ng/brain/sonner';
import { HlmBadgeImports } from '@spartan-ng/helm/badge';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmFieldImports } from '@spartan-ng/helm/field';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { HlmSkeletonImports } from '@spartan-ng/helm/skeleton';
import { SessionService } from '../../../core/auth/session.service';
import { textoDeError } from '../../../core/http/peticion';
import { CuentasApi } from '../../../services/api/recursos.api';
import { Cuenta } from '../../../shared/models/cuenta.model';

/** Perfil propio: consulta GET /v1/users/me y edición con PATCH. */
@Component({
  selector: 'app-perfil',
  imports: [
    ReactiveFormsModule,
    NgIcon,
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    HlmFieldImports,
    HlmInputImports,
    HlmLabelImports,
    HlmSkeletonImports,
  ],
  template: `
    <h1 class="mb-4 inline-flex items-center gap-2 text-3xl font-semibold"><ng-icon name="lucideUser" class="text-[length:--spacing(6)]" />Mi perfil</h1>

    @if (cargando()) {
      <section hlmCard class="mb-6 max-w-2xl gap-3 p-4">
        <div class="grid grid-cols-1 gap-x-6 gap-y-3 sm:grid-cols-2">
          @for (campo of [1, 2, 3, 4, 5, 6]; track campo) {
            <div class="flex flex-col gap-1">
              <div hlmSkeleton class="h-4 w-24"></div>
              <div hlmSkeleton class="h-4 w-40"></div>
            </div>
          }
        </div>
      </section>
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
          <div hlmField>
            <label hlmFieldLabel for="nombre-perfil">Nombre *</label>
            <input hlmInput id="nombre-perfil" formControlName="nombre" />
            @if (mostrarError('nombre')) {
              <hlm-field-error>El nombre es obligatorio (máx. 100 caracteres).</hlm-field-error>
            }
          </div>
          <div hlmField>
            <label hlmFieldLabel for="email-perfil">Email *</label>
            <input hlmInput id="email-perfil" type="email" formControlName="email" />
            @if (mostrarError('email')) {
              <hlm-field-error>El email es obligatorio y debe ser válido (máx. 150).</hlm-field-error>
            }
          </div>
          <div hlmField>
            <label hlmFieldLabel for="password-perfil">Contraseña nueva (opcional)</label>
            <input
              hlmInput
              id="password-perfil"
              type="password"
              placeholder="Déjala vacía para conservarla"
              formControlName="password"
            />
            @if (mostrarError('password')) {
              <hlm-field-error>La contraseña debe tener entre 12 y 128 caracteres.</hlm-field-error>
            }
          </div>
          <div hlmField>
            <label hlmFieldLabel for="current-password-perfil">Contraseña actual (para cambiarla)</label>
            <input
              hlmInput
              id="current-password-perfil"
              type="password"
              autocomplete="current-password"
              formControlName="current_password"
            />
            @if (mostrarError('current_password')) {
              <hlm-field-error>Introduce tu contraseña actual (máx. 128 caracteres).</hlm-field-error>
            }
          </div>
          <div class="flex gap-2">
            <button hlmBtn class="gap-1.5" type="submit"><ng-icon name="lucideCircleCheck" class="text-[length:--spacing(4)]" />Guardar cambios</button>
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
    try {
      const actualizado = await this.api.actualizarYo({
        nombre: nombre.trim(),
        email: email.trim(),
        ...(password === '' ? {} : { password, current_password }),
      });
      this.aplicar(actualizado);
      toast.success('Perfil actualizado');
      this.form.controls.password.setValue('');
    } catch (error) {
      toast.error(textoDeError(error));
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
      toast.error(textoDeError(error));
    } finally {
      this.cargando.set(false);
    }
  }
}
