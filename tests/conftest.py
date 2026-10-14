"""Secretos solo de pruebas, explícitos y distintos de la configuración real."""

import os

# Se fija antes de importar main/settings desde los conftest de cada suite.
os.environ["SECRET_KEY"] = "gymflow-test-only-secret-not-for-deployment-2026"
