# Decisiones
- PyJWT y pwdlib según FastAPI oficial; Protocol en dominio y adaptadores en infraestructura.
- Hash ficticio para email inexistente: verifica Argon2 también en ese caso.
- Token 30 minutos fijos, configuración de duración sigue en #67.
- SECRET_KEY sin fallback; tests usan un secreto de prueba explícito, CI también.
- Registro/login sin security requirement. Esquema OAuth2 visible antes de /me (#56).
- Referencias: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ y
  https://pyjwt.readthedocs.io/en/latest/usage.html
