/** Descarga un texto como archivo en el navegador (Blob + enlace efímero). */
export function descargarArchivo(nombreArchivo: string, contenido: string, tipo: string): void {
  const blob = new Blob([contenido], { type: `${tipo};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = nombreArchivo;
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();
  URL.revokeObjectURL(url);
}
