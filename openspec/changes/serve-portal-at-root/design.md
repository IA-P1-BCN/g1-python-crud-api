Construcción multi-stage Node/uv/Python. Copiar únicamente dist/browser a
/app/static. Montar StaticFiles al final, solo cuando exista index.html.
Fallback limitado a rutas de Angular, nunca a /v1 ni archivos ausentes.
Desarrollo sin build continúa sirviendo solo API; Angular usa su proxy habitual.
Render conserva g1-gymflow-api, Aiven, secretos y auto-deploy; no requiere crear
otro servicio. El contenedor Nginx sigue siendo una opción local en Compose.
