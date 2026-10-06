"""Clave efímera por ejecución de tests, nunca persistida ni publicada."""

import os
from secrets import token_urlsafe

os.environ.setdefault("SECRET_KEY", token_urlsafe(48))
