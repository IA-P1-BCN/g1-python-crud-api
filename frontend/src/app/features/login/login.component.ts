import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService, InvalidCredentialsError, NetworkError, UsuarioAutenticado } from '../../core/auth/auth.service';
import { SessionService } from '../../core/auth/session.service';
import { MenuComponent } from '../../shared/components/menu.component';
import { HlmAlertImports } from '@spartan-ng/helm/alert';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';

export const MENSAJE_CREDENCIALES = 'Correo o contraseña incorrectos';
export const MENSAJE_RED = 'No se pudo conectar con el servidor. Inténtalo de nuevo.';
export const MENSAJE_INESPERADO = 'Ha ocurrido un error inesperado.';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink, MenuComponent, HlmAlertImports, HlmButtonImports, HlmInputImports, HlmLabelImports],
  templateUrl: './login.component.html',
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly session = inject(SessionService);
  private readonly router = inject(Router);
  private readonly ruta = inject(ActivatedRoute);

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

  /** Aviso recibido al llegar desde el registro (state de navegación). */
  protected readonly mensajeInfo = signal<string | null>(
    (history.state as { mensaje?: string } | null)?.mensaje ?? null,
  );
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
      const usuario = await this.auth.login(email, password);
      this.session.iniciar(usuario);
      await this.router.navigateByUrl(this.destino(usuario));
    } catch (error) {
      this.mensajeError.set(mensajeParaError(error));
    } finally {
      this.enviando.set(false);
    }
  }

  /** Vuelve a la ruta pedida si es del portal; si no, al portal (con ficha) o a la home. */
  private destino(usuario: UsuarioAutenticado): string {
    const returnUrl = this.ruta.snapshot.queryParamMap.get('returnUrl');
    if (returnUrl && returnUrl.startsWith('/portal')) {
      return returnUrl;
    }
    return usuario.id_cliente !== null ? '/portal' : '/';
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
