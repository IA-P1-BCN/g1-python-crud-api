"""Variables de configuración leídas de `.env` (pydantic-settings)."""

import ssl
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes de la aplicación y de la conexión a MySQL."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "app_user"
    mysql_password: str = "app_password"
    mysql_database: str = "gym_db"
    # TLS obligatorio en MySQL gestionados que lo exigen (p. ej. Aiven).
    mysql_ssl: bool = False

    # Orígenes CORS permitidos para el frontend, separados por comas.
    allowed_origins: str = ""

    # Contraseña de administración: obligatoria en el seed, opcional en la API;
    # SecretStr evita que se imprima en logs, trazas o en `repr()`.
    admin_password: SecretStr | None = None
    admin_email: str = "admin@example.com"
    secret_key: SecretStr = Field(min_length=32)
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    @property
    def database_url(self) -> str:
        """URL de conexión SQLAlchemy para MySQL (driver pymysql)."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def cors_origins(self) -> list[str]:
        """Lista de orígenes CORS a partir de `allowed_origins`."""
        return [
            origen.strip()
            for origen in self.allowed_origins.split(",")
            if origen.strip()
        ]

    def sqlalchemy_connect_args(self) -> dict:
        """Argumentos extra para `create_engine` (TLS de MySQL si activo)."""
        if not self.mysql_ssl:
            return {}
        contexto = ssl.create_default_context()
        return {"ssl": contexto}


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración en caché (un único Settings por proceso)."""
    return Settings()
