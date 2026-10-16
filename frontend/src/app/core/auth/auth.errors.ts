/** Credenciales incorrectas. El mensaje para el usuario lo traduce la pantalla. */
export class InvalidCredentialsError extends Error {
  constructor() {
    super('Credenciales no válidas');
    this.name = 'InvalidCredentialsError';
  }
}

/** Fallo de conexión con el servidor (red caída, timeout o servidor inaccesible). */
export class NetworkError extends Error {
  constructor() {
    super('No se pudo conectar con el servidor');
    this.name = 'NetworkError';
  }
}

/** El correo ya identifica una cuenta (HTTP 409 en la API). */
export class EmailDuplicadoError extends Error {
  constructor() {
    super('Ya existe una cuenta con este correo');
    this.name = 'EmailDuplicadoError';
  }
}
