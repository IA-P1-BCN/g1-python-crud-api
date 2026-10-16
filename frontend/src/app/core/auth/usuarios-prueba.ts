import { UsuarioAutenticado } from './auth.service';

/** Usuarios ficticios de desarrollo. Ana tiene ficha de socio; staff no. */
export const USUARIO_ANA: UsuarioAutenticado = {
  id: 1,
  nombre: 'Ana García',
  email: 'cliente@gym.test',
  rol: 'cliente',
  id_cliente: 1,
};

export const USUARIO_STAFF: UsuarioAutenticado = {
  id: 2,
  nombre: 'Laura Staff',
  email: 'staff@gym.test',
  rol: 'staff',
  id_cliente: null,
};
