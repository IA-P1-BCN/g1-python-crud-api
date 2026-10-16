import { ComponentFixture } from '@angular/core/testing';

/** Espera a que terminen las promesas del servicio mock y refresca la vista. */
export async function esperarCarga<T>(fixture: ComponentFixture<T>): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0));
  fixture.detectChanges();
}
