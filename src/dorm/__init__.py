import os
from pathlib import Path
import runpy

import sys
from django.db import models


def ensure_setup():
    from django.conf import settings

    assert (
        settings.configured
    ), "dorm setup not done, ensure `setup_dorm` is called before using it's features are used."


def setup():
    from django.conf import settings

    # IGNORE <- if already configured
    if settings.configured:
        return

    # determine calling directory
    call_dir = Path().resolve()
    assert call_dir.is_dir(), f"Calling path should be a directory: {call_dir}"

    # determine settings.py file
    settings_file = call_dir / "settings.py"
    assert settings_file.is_file(), f"settings.py file should exists in calling directory: {settings_file}"

    # setup Django with settings file
    def load_settings_from_file(file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Settings file not found: {file_path}")

        # "run" settings.py file
        settings_dict = runpy.run_path(file_path)
        # keep on UPPER case values and return
        settings_dict = {key: value for key, value in settings_dict.items() if key.isupper()}
        return settings_dict

    user_settings = load_settings_from_file(settings_file)
    settings.configure(**user_settings)

    # add calling_dir to PYTHONPATH
    if str(call_dir) not in sys.path:
        sys.path.insert(0, str(call_dir))  # 1st entry for higher priority

    # setup django
    import django

    django.setup()

    # create app.migrations package for all user apps (where models exists) <- only when `dorm makemigrations` called
    if len(sys.argv) > 1 and sys.argv[0].endswith("/dorm") and sys.argv[1] == "makemigrations":
        from django.apps import apps

        for app_config in apps.get_app_configs():
            # Match the full app name (e.g., 'django.contrib.auth')
            if app_config.name in settings.INSTALLED_APPS and app_config.get_models():
                maybe_app_module_path = (call_dir / app_config.name.replace(".", "/")).resolve()
                if maybe_app_module_path.is_dir():
                    (maybe_app_module_path / "migrations").mkdir(exist_ok=True)
                    (maybe_app_module_path / "migrations" / "__init__.py").touch(exist_ok=True)


def _django_manage_py():
    """Copy-pasted from Django generated manage.py."""
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def _cli():
    setup()
    ensure_setup()
    _django_manage_py()


if __name__ == "__main__":
    _cli()

__ALL__ = [
    setup,
    ensure_setup,
    models,
]
