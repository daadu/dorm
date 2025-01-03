from pathlib import Path
import runpy

import sys
from django.core.management import ManagementUtility, BaseCommand, CommandError, color_style
import django

_STYLE = color_style()


def _discover_project_path() -> Path:
    project_path = Path().resolve()
    assert project_path.is_dir(), f"Project path should be a directory: {project_path}"
    return project_path


def setup(*, settings_dir: str | Path | None = None):
    from django.conf import settings

    # IGNORE <- if already configured
    if settings.configured:
        return

    # determine settings.py file
    project_dir = settings_dir or _discover_project_path()
    settings_file = Path(project_dir) / "settings.py"

    if not settings_file.is_file():
        raise RuntimeError(
            _STYLE.ERROR(
                "\n"
                f"Setting file not found at: {settings_file}\n"
                f"Ensure settings.py exists in the project root. If the lookup path is wrong then:\n"
                f"Make sure your entrypoint is called from same directory where `settings.py` is located. Example: `./scripts/main.py` in `<proj-root>` instead of `./main.py` inside `<proj-root>/scripts`\n"
                f"OR\n"
                f"Set `settings_dir` explicitly while calling `dorm.setup(settings_dir=...)`."
            )
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


class DormManagementUtility(ManagementUtility):
    class CantExecuteCommand(BaseCommand):
        def __init__(self, subcommand, stdout=None, stderr=None, no_color=False, force_color=False):
            super().__init__(stdout, stderr, no_color, force_color)
            self.subcommand = subcommand

        def handle(self, *args, **options):
            raise CommandError(f"Can't execute '{self.subcommand}' with dorm.")

    class DormInitCommand(BaseCommand):
        help = "Initialize your project to use dorm."
        requires_system_checks = []

        _DJANGO_VERSION = ".".join(map(str, django.VERSION[:2]))
        _SETTINGS_CONTENT = (
            f'''"""
Django settings for your project.

Generated by 'dorm init', with minimal settings required for just using Django's ORM.

For the full list of settings and their values, see:
- https://docs.djangoproject.com/en/{_DJANGO_VERSION}/topics/settings/
- https://docs.djangoproject.com/en/{_DJANGO_VERSION}/ref/settings/
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

# List of packages (Django apps), defining Django models.
# Each item should be a dotted Python path to package containing `models` as a module or a sub-package.
# https://docs.djangoproject.com/en/{_DJANGO_VERSION}/topics/db/models/
INSTALLED_APPS = [] # TODO: add package here, after adding models 

# Databases
# https://docs.djangoproject.com/en/{_DJANGO_VERSION}/ref/settings/#databases'''
            '''
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}'''
            '\n'
        )

        def handle(self, *args, **options):
            settings_path = _discover_project_path() / "settings.py"
            if settings_path.is_file():
                raise CommandError(
                    f"dorm already initialized with this project (settings.py already exists at {settings_path})."
                )

            # log messages
            self.stdout.write(self.style.WARNING(f"Initializing settings.py file at {settings_path}..."))
            self.stdout.write(self.style.NOTICE(self._SETTINGS_CONTENT))
            # write file content
            settings_path.write_text(self._SETTINGS_CONTENT)
            self.stdout.write(self.style.SUCCESS("--- DONE ---"))

    dorm_commands = {
        "init": DormInitCommand,
    }

    hide_commands = {"startproject", "startapp"}

    def main_help_text(self, commands_only=False):
        main_help_text = super().main_help_text(commands_only)
        # for commands only - simply add/remove command -> sort -> join and return
        if commands_only:
            cmds = set(main_help_text.split("\n"))
            # - add dorm commands
            cmds.union(set(self.dorm_commands.keys()))
            # - remove hide commands
            for hide_cmd in self.hide_commands:
                if hide_cmd in cmds:
                    cmds.remove(hide_cmd)
            return "\n".join(sorted(cmds))

        # make [dorm] commands content
        dorm_content = [_STYLE.NOTICE("[dorm]")]
        for cmd in self.dorm_commands:
            dorm_content.append(f"    {cmd}")
        dorm_content = "\n".join(dorm_content)
        # insert [dorm]
        insert_after = "Available subcommands:\n"
        main_help_text = main_help_text.replace(insert_after, f"{insert_after}\n{dorm_content}\n")
        # remove hide commands
        main_help_text = "\n".join(
            filter(lambda line: all(c not in line for c in self.hide_commands), main_help_text.split("\n"))
        )
        return main_help_text

    def fetch_command(self, subcommand):
        # execute dorm command <- if it is
        if subcommand in self.dorm_commands:
            return self.dorm_commands[subcommand]()
        # fail <- if hide command
        if subcommand in self.hide_commands:
            return self.CantExecuteCommand(subcommand)
        return super().fetch_command(subcommand)


def _cli():
    # figure project_path and subcommand
    project_path = _discover_project_path()
    try:
        subcommand = sys.argv[1]
    except IndexError:
        subcommand = "help"

    def execute_management_command():
        """Run a ManagementUtility."""
        utility = DormManagementUtility(sys.argv)
        utility.execute()

    def hook_before_setup():
        # execute `dorm init` before setup and exit
        if subcommand == "init":
            execute_management_command()
            sys.exit(0)

    def hook_after_setup():
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

    # execute cli
    hook_before_setup()
    setup(settings_dir=project_path)
    ensure_setup()
    hook_after_setup()
    execute_management_command()


if __name__ == "__main__":
    _cli()

__ALL__ = [
    setup,
    ensure_setup,
]
