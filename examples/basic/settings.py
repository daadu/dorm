from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

INSTALLED_APPS = [
    "blog",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
