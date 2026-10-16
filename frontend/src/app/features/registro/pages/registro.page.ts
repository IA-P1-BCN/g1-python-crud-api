import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MenuComponent } from '../../../shared/components/menu.component';
import { HlmAlertImports } from '@spartan-ng/helm/alert';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCheckboxImports } from '@spartan-ng/helm/checkbox';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import {
  AuthService,
  EmailDuplicadoError,
  NetworkError,
} from '../../../core/auth/auth.service';

export const MENSAJE_EMAIL_DUPLICADO = 'Ya existe una cuenta con este correo';
export const MENSAJE_RED_REGISTRO = 'No se pudo conectar con el servidor. Inténtalo de nuevo.';
export const MENSAJE_INESPERADO_REGISTRO = 'Ha ocurrido un error inesperado.';
export const MENSAJE_EXITO_REGISTRO = 'Cuenta creada. Ya puedes iniciar sesión';

@Component({
  selector: 'app-registro',
  imports: [ReactiveFormsModule, RouterLink, MenuComponent, HlmAlertImports, HlmButtonImports, HlmCheckboxImports, HlmInputImports, HlmLabelImports],
  templateUrl: './registro.page.html',
})
export class RegistroPage {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

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
      validators: [Validators.required, Validators.minLength(12), Validators.maxLength(128)],
    }),
    crearCliente: new FormControl(false, { nonNullable: true }),
  });

  protected readonly enviando = signal(false);
  protected readonly mostrarPassword = signal(false);
  protected readonly mensajeError = signal<string | null>(null);

  protected async enviar(): Promise<void> {
    if (this.enviando()) {
      return;
    }
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const { nombre, email, password, crearCliente } = this.form.getRawValue();
    this.enviando.set(true);
    this.mensajeError.set(null);

    try {
      await this.auth.register({
        nombre: nombre.trim(),
        email,
        password,
        crear_cliente: crearCliente,
      });
      // Tras registrarse se vuelve al login con el aviso de éxito.
      await this.router.navigateByUrl('/auth/login', { state: { mensaje: MENSAJE_EXITO_REGISTRO } });
    } catch (error) {
      this.mensajeError.set(mensajeParaError(error));
    } finally {
      this.enviando.set(false);
    }
  }
}

function mensajeParaError(error: unknown): string {
  if (error instanceof EmailDuplicadoError) {
    return MENSAJE_EMAIL_DUPLICADO;
  }
  if (error instanceof NetworkError) {
    return MENSAJE_RED_REGISTRO;
  }
  return MENSAJE_INESPERADO_REGISTRO;
}
