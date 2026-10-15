import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService, InvalidCredentialsError, NetworkError } from '../../core/auth/auth.service';

export const MENSAJE_CREDENCIALES = 'Correo o contraseña incorrectos';
export const MENSAJE_RED = 'No se pudo conectar con el servidor. Inténtalo de nuevo.';
export const MENSAJE_INESPERADO = 'Ha ocurrido un error inesperado.';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  protected readonly form = new FormGroup({
    email: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.email],
    }),
    password: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required],
    }),
  });

  protected readonly enviando = signal(false);
  protected readonly mensajeError = signal<string | null>(null);

  protected async enviar(): Promise<void> {
    if (this.enviando()) {
      return;
    }
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const { email, password } = this.form.getRawValue();
    this.enviando.set(true);
    this.mensajeError.set(null);

    try {
      await this.auth.login(email, password);
      await this.router.navigateByUrl('/');
    } catch (error) {
      this.mensajeError.set(mensajeParaError(error));
    } finally {
      this.enviando.set(false);
    }
  }
}

function mensajeParaError(error: unknown): string {
  if (error instanceof InvalidCredentialsError) {
    return MENSAJE_CREDENCIALES;
  }
  if (error instanceof NetworkError) {
    return MENSAJE_RED;
  }
  return MENSAJE_INESPERADO;
}
