La dependencia compone get_current_user: rol y actividad se leen de persistencia
en cada petición. Denegar por rol antes de invocar el controlador, con
ForbiddenError del dominio y el handler HTTP existente. No introducir roles
en JWT ni duplicar su validación. #106 define la autorización del gimnasio.
