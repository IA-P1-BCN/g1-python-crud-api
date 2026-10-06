"""Variables de configuración leídas de `.env` (pydantic-settings)."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes de la aplicación y de la conexión a MySQL."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "app_user"
    mysql_password: str = "app_password"
    mysql_database: str = "gym_db"

    # Contraseña de administración. Es opcional porque V1 todavía no la usa;
    # SecretStr evita que se imprima en logs, trazas o en `repr()`.
    admin_password: SecretStr | None = None

    @property
    def database_url(self) -> str:
        """URL de conexión SQLAlchemy para MySQL (driver pymysql)."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración en caché (un único Settings por proceso)."""
    return Settings()
