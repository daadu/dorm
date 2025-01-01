from pathlib import Path
import runpy

import sys


def _discover_project_path() -> Path:
    project_path = Path().resolve()
    assert project_path.is_dir(), f"Project path should be a directory: {project_path}"
    return project_path


def setup(*, project_path: Path | None = None):
    from django.conf import settings

    # IGNORE <- if already configured
    if settings.configured:
        return

    # determine settings.py file
    project_dir = project_path or _discover_project_path()
    settings_file = project_dir / "settings.py"
    if not settings_file.is_file():
        raise RuntimeError(
            "Ensure that your project is initialized properly.\n"
            f"Execute `dorm` command or manually create `settings.py` file at {settings_file}"
        )

    # setup Django with settings file values
    # - "run" settings.py file
    user_settings = runpy.run_path(str(settings_file))
    # - keep on UPPER case values and return
    user_settings = {key: value for key, value in user_settings.items() if key.isupper()}
    # - add default required settings if not in the project's settings.py
    if "DEFAULT_AUTO_FIELD" not in user_settings:
        user_settings["DEFAULT_AUTO_FIELD"] = "django.db.models.BigAutoField"
    # - configure
    settings.configure(**user_settings)

    # add calling_dir to PYTHONPATH
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))  # 1st entry for higher priority

    # setup django
    import django

    django.setup()


def ensure_setup():
    from django.conf import settings

    assert (
        settings.configured
    ), "dorm setup not done, ensure `setup_dorm` is called before using it's features are used."


def _hook_commands_before_setup(*, project_path: Path, subcommand: str):
    if subcommand == "init":
        settings_path = project_path / "settings.py"
        if settings_path.is_file():
            print(f"dorm already initialized with this project (settings.py already exists at {settings_path}).")
            sys.exit(1)

        settings_content = (
            "from pathlib import Path"
            "\n"
            "\nBASE_DIR = Path(__file__).parent.resolve()"
            "\n"
            "\nINSTALLED_APPS = []"
            "\n"
            "\nDATABASES = {"
            '\n    "default": {'
            '\n        "ENGINE": "django.db.backends.sqlite3",'
            '\n        "NAME": BASE_DIR / "db.sqlite3",'
            '\n    }'
            '\n}'
            '\n'
        )
        print(
            f"settings.py file not found.\n"
            f"Initializing settings.py file at {settings_path}, with following content:\n"
            f"{settings_content}\n\n---"
        )
        settings_path.write_text(settings_content)
        sys.exit(0)


def _hook_commands_after_setup(*, project_path: Path, subcommand: str):
    # create app.migrations package for all user apps (where models exists) <- only when `dorm makemigrations` called
    if subcommand == "makemigrations":
        from django.apps import apps
        from django.conf import settings

        for app_config in apps.get_app_configs():
            # Match the full app name (e.g., 'django.contrib.auth')
            if app_config.name in settings.INSTALLED_APPS and app_config.get_models():
                maybe_app_module_path = (project_path / app_config.name.replace(".", "/")).resolve()
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
    # figure project_path and subcommand
    project_path = _discover_project_path()
    try:
        subcommand = sys.argv[1]
    except IndexError:
        subcommand = "help"

    # execute cli
    _hook_commands_before_setup(project_path=project_path, subcommand=subcommand)
    setup(project_path=project_path)
    ensure_setup()
    _hook_commands_after_setup(project_path=project_path, subcommand=subcommand)
    _django_manage_py()


if __name__ == "__main__":
    _cli()

__ALL__ = [
    setup,
    ensure_setup,
]
