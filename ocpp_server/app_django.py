"""Bootstraps Django so the OCPP server can use ORM & services."""
import os
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocpp_backend.settings")

# Fallback secret if no .env is loaded
if not os.environ.get("DJANGO_SECRET_KEY"):
    os.environ["DJANGO_SECRET_KEY"] = "dev-secret"

django.setup()
