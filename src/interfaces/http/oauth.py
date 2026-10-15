"""Contrato OAuth2 compartido por Swagger y las dependencias protegidas."""

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login", auto_error=False)
