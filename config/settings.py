from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "development-only-secret-key"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "routes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = []
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

GEOCODING_BASE_URL = os.getenv("GEOCODING_BASE_URL", "https://nominatim.openstreetmap.org")
ROUTING_BASE_URL = os.getenv("ROUTING_BASE_URL", "https://router.project-osrm.org")
ROUTING_TIMEOUT_SECONDS = float(os.getenv("ROUTING_TIMEOUT_SECONDS", "10"))
ROUTING_USER_AGENT = os.getenv("ROUTING_USER_AGENT", "truckstop-fuel-planner/1.0")
ROUTING_CACHE_TTL_SECONDS = int(os.getenv("ROUTING_CACHE_TTL_SECONDS", "3600"))

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "truckstop-route-cache",
    }
}
