import subprocess
from pathlib import Path


def _cleanup(*, settings_file: Path):
    settings_file.unlink(missing_ok=True)


def main():
    project_dir = Path(__file__).parent.resolve()
    settings_file = project_dir / "settings.py"
    _cleanup(settings_file=settings_file)

    try:
        # dorm init
        subprocess.run(["dorm", "init"], cwd=project_dir, check=True)

        # assert settings_file created with right content
        assert settings_file.exists(), f"settings.py file should be created, by dorm at {settings_file}"
        # - simple django check command
        subprocess.run(["dorm", "check"], cwd=project_dir, check=True)
        # - ensure dorm setup works
        import dorm

        dorm.setup()
        dorm.ensure_setup()
        # - ensure settings value are correct
        from django.conf import settings

        assert settings.BASE_DIR == project_dir, f"settings.BASE_DIR ({settings.BASE_DIR}) should be {project_dir}"
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": project_dir / "db.sqlite3",
            }
        }
        assert settings.DATABASES == DATABASES, f"settings.DATABASES ({settings.DATABASES}) should be {DATABASES}"
        assert settings.INSTALLED_APPS == [], f"settings.INSTALLED_APPS ({settings.INSTALLED_APPS}) should be {[]}"

    finally:
        _cleanup(settings_file=settings_file)


if __name__ == "__main__":
    main()
