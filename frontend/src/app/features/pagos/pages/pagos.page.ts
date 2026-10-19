import { Component, inject, signal } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
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
import { ClientesApi, PagosApi } from '../../../services/api/recursos.api';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog.component';
import { Cliente } from '../../../shared/models/cliente.model';
import { Pago, PagoEntrada } from '../../../shared/models/pago.model';

const METODOS = ['Tarjeta', 'Transferencia', 'Efectivo'] as const;

/** Monto positivo con hasta dos decimales (max_digits=10 en la API). Se admite coma decimal. */
function montoPositivo(control: AbstractControl): ValidationErrors | null {
  const valor = String(control.value ?? '').trim().replace(',', '.');
  if (valor === '' || !/^\d{1,8}(\.\d{1,2})?$/.test(valor) || Number(valor) <= 0) {
    return { monto: true };
  }
  return null;
}

/** Gestión de pagos: CRUD con filtros por cliente y método (/v1/pagos). */
@Component({
  selector: 'app-pagos',
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
      <h1 class="text-3xl font-semibold">Pagos</h1>
      <button hlmBtn type="button" (click)="nuevo()">Nuevo pago</button>
    </div>

    <form id="filtros" class="mb-4 flex flex-wrap items-end gap-3" (submit)="buscar($event)">
      <div class="flex flex-col gap-1">
        <label hlmLabel for="cliente-filtro-pagos">ID de cliente</label>
        <input hlmInput id="cliente-filtro-pagos" type="number" placeholder="Ej.: 1" [formControl]="filtroCliente" />
      </div>
      <div class="flex flex-col gap-1">
        <label hlmLabel for="metodo-filtro-pagos">Método</label>
        <select hlmInput id="metodo-filtro-pagos" [formControl]="filtroMetodo">
          <option value="">Todos</option>
          @for (metodo of metodos; track metodo) {
            <option [value]="metodo">{{ metodo }}</option>
          }
        </select>
      </div>
      <button hlmBtn type="submit" variant="secondary">Buscar</button>
      <button hlmBtn type="button" variant="ghost" (click)="limpiar()">Limpiar</button>
    </form>

    @if (formulario(); as modo) {
      <section hlmCard class="mb-4 p-4">
        <h2 class="mb-3 text-lg font-semibold">{{ modo === 'crear' ? 'Nuevo pago' : 'Editar pago' }}</h2>
        <form id="formulario" [formGroup]="form" class="grid gap-3 sm:grid-cols-2" (submit)="guardar($event)">
          <div hlmField>
            <label hlmFieldLabel for="cliente-pago">Cliente *</label>
            <select hlmInput id="cliente-pago" formControlName="id_cliente">
              <option value="">Elige un cliente</option>
              @for (cliente of clientes(); track cliente.id_cliente) {
                <option [value]="idTexto(cliente.id_cliente)">{{ cliente.nombre }} (#{{ cliente.id_cliente }})</option>
              }
            </select>
            @if (mostrarError('id_cliente')) {
              <hlm-field-error>El cliente es obligatorio.</hlm-field-error>
            } @else if (clientes().length === 0) {
              <p class="text-sm text-muted-foreground">No hay clientes: da de alta alguno primero.</p>
            }
          </div>
          <div hlmField>
            <label hlmFieldLabel for="monto-pago">Monto (€) *</label>
            <input hlmInput id="monto-pago" inputmode="decimal" placeholder="35.00" formControlName="monto" />
            @if (mostrarError('monto')) {
              <hlm-field-error>El monto debe ser mayor que cero y con dos decimales como máximo.</hlm-field-error>
            }
          </div>
          <div hlmField>
            <label hlmFieldLabel for="fecha-pago">Fecha de pago *</label>
            <input hlmInput id="fecha-pago" type="date" formControlName="fecha_pago" />
            @if (mostrarError('fecha_pago')) {
              <hlm-field-error>La fecha es obligatoria.</hlm-field-error>
            }
          </div>
          <div hlmField>
            <label hlmFieldLabel for="metodo-pago">Método</label>
            <select hlmInput id="metodo-pago" formControlName="metodo_pago">
              <option value="">Sin método</option>
              @for (metodo of metodos; track metodo) {
                <option [value]="metodo">{{ metodo }}</option>
              }
            </select>
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
              <th hlmTh>Cliente</th>
              <th hlmTh>Monto</th>
              <th hlmTh>Fecha</th>
              <th hlmTh>Método</th>
              <th hlmTh>Acciones</th>
            </tr>
          </thead>
          <tbody hlmTBody>
            @for (fila of [1, 2, 3]; track fila) {
              <tr hlmTr>
                @for (col of [1, 2, 3, 4, 5, 6]; track col) {
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
          <p hlmEmptyTitle>No hay pagos que coincidan.</p>
          <p hlmEmptyDescription>Prueba con otros filtros o registra un pago nuevo.</p>
        </div>
      </div>
    } @else {
      <div hlmTableContainer>
        <table hlmTable>
          <thead hlmTHead>
            <tr hlmTr>
              <th hlmTh>ID</th>
              <th hlmTh>Cliente</th>
              <th hlmTh>Monto</th>
              <th hlmTh>Fecha</th>
              <th hlmTh>Método</th>
              <th hlmTh>Acciones</th>
            </tr>
          </thead>
          <tbody hlmTBody>
            @for (fila of items(); track fila.id_pago) {
              <tr hlmTr>
                <td hlmTd>{{ fila.id_pago }}</td>
                <td hlmTd>{{ nombreCliente(fila.id_cliente) }}</td>
                <td hlmTd>{{ fila.monto }} €</td>
                <td hlmTd>{{ fila.fecha_pago }}</td>
                <td hlmTd>{{ fila.metodo_pago ?? '—' }}</td>
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
      <p class="mt-2 text-sm text-muted-foreground">{{ items().length }} pagos</p>
    }

    @if (pendiente(); as fila) {
      <app-confirm-dialog
        titulo="Borrar pago"
        [mensaje]="'¿Eliminar el pago #' + fila.id_pago + ' de ' + nombreCliente(fila.id_cliente) + '?'"
        textoCancelar="Volver"
        textoConfirmar="Sí, borrar"
        (cancelar)="pendiente.set(null)"
        (confirmar)="borrar(fila)"
      />
    }
  `,
})
export class PagosPage {
  private readonly api = inject(PagosApi);
  private readonly clientesApi = inject(ClientesApi);

  protected readonly metodos = METODOS;
  protected readonly cargando = signal(true);
  protected readonly items = signal<Pago[]>([]);
  protected readonly clientes = signal<Cliente[]>([]);
  protected readonly formulario = signal<'crear' | 'editar' | null>(null);
  protected readonly editandoId = signal<number | null>(null);
  protected readonly pendiente = signal<Pago | null>(null);

  protected readonly filtroCliente = new FormControl('', { nonNullable: true });
  protected readonly filtroMetodo = new FormControl('', { nonNullable: true });

  protected readonly form = new FormGroup({
    id_cliente: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    monto: new FormControl('', { nonNullable: true, validators: [Validators.required, montoPositivo] }),
    fecha_pago: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    metodo_pago: new FormControl('', { nonNullable: true }),
  });

  constructor() {
    void this.cargar();
  }

  protected nombreCliente(id: number): string {
    const cliente = this.clientes().find((c) => c.id_cliente === id);
    return cliente ? `${cliente.nombre} (#${id})` : `#${id}`;
  }

  protected buscar(evento: Event): void {
    evento.preventDefault();
    void this.cargar();
  }

  protected limpiar(): void {
    this.filtroCliente.setValue('');
    this.filtroMetodo.setValue('');
    void this.cargar();
  }

  protected nuevo(): void {
    this.form.reset({ id_cliente: '', monto: '', fecha_pago: '', metodo_pago: '' });
    this.editandoId.set(null);
    this.formulario.set('crear');
  }

  protected editar(fila: Pago): void {
    this.form.setValue({
      id_cliente: String(fila.id_cliente),
      monto: fila.monto,
      fecha_pago: fila.fecha_pago,
      metodo_pago: fila.metodo_pago ?? '',
    });
    this.editandoId.set(fila.id_pago);
    this.formulario.set('editar');
  }

  protected cerrarFormulario(): void {
    this.formulario.set(null);
    this.editandoId.set(null);
  }

  protected mostrarError(campo: 'id_cliente' | 'monto' | 'fecha_pago'): boolean {
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
    try {
      if (modo === 'crear') {
        await this.api.crearPago(datos);
        toast.success('Pago creado');
      } else {
        const id = this.editandoId();
        if (id === null) {
          return;
        }
        await this.api.reemplazar(id, datos);
        toast.success('Pago actualizado');
      }
      this.cerrarFormulario();
      await this.cargar();
    } catch (error) {
      toast.error(textoDeError(error));
    }
  }

  protected async borrar(fila: Pago): Promise<void> {
    this.pendiente.set(null);
    try {
      await this.api.eliminar(fila.id_pago);
      toast.success('Pago eliminado');
      await this.cargar();
    } catch (error) {
      toast.error(textoDeError(error));
    }
  }

  private datosDelFormulario(): PagoEntrada {
    const { id_cliente, monto, fecha_pago, metodo_pago } = this.form.getRawValue();
    return {
      id_cliente: Number(id_cliente),
      monto: monto.trim().replace(',', '.'),
      fecha_pago,
      metodo_pago: metodo_pago === '' ? null : (metodo_pago as Pago['metodo_pago']),
    };
  }

  private async cargar(): Promise<void> {
    this.cargando.set(true);
    const idCliente = this.filtroCliente.value.trim();
    const metodo = this.filtroMetodo.value;
    try {
      const [pagos, clientes] = await Promise.all([
        this.api.listar({
          ...(idCliente === '' ? {} : { id_cliente: Number(idCliente) }),
          ...(metodo === '' ? {} : { metodo_pago: metodo }),
        }),
        this.clientesApi.listar(),
      ]);
      this.items.set(pagos);
      this.clientes.set(clientes);
    } catch (error) {
      this.items.set([]);
      toast.error(textoDeError(error));
    } finally {
      this.cargando.set(false);
    }
  }
}
