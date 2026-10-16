Conservar nombres y estructura raíz del Blueprint para no mover recursos.
No crear MySQL ni discos en Render. Los secretos sync:false y la CA se conservan.

La imagen Nginx genera default.conf por envsubst. API_UPSTREAM es un origen
sin ruta ni barra final: http://api:8000 local, HTTPS público en Render.
El proxy conserva request_uri y utiliza proxy_host para Host/SNI y bundle CA.
El DNS del contenedor renueva la IP del upstream sin reconstruir la imagen.

API multi-stage no root con entrypoint de migración y seed. Compose fija
PORT=8000 y MYSQL_SSL=false; Render usa PORT=10000.
Un push actualiza servicios existentes, pero crear el frontend exige una
sincronización del Blueprint o alta inicial desde Dashboard.
