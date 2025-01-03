import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import color_style

_STYLE = color_style()


def main():
    project_root = Path(__file__).parent.resolve()
    scripts_path = project_root / "scripts"

    # should FAIL: when calling entrypoint (without explicit `settings_dir`) from the project-root
    error: subprocess.CalledProcessError | None = None
    try:
        subprocess.run(
            [sys.executable, str(scripts_path / "run_without_explict_settings_dir.py")],
            cwd=str(scripts_path),
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        error = e
    assert error, "Should fail when calling dorm.setup(), not from the project root."
    assert b"Ensure settings.py exists in the project root." in error.stderr, f"Error output: {error.stderr}"

    # should PASS: when calling entrypoint (without explicit `settings_dir`) from the project root
    subprocess.run(
        [sys.executable, str(scripts_path / "run_without_explict_settings_dir.py")],
        cwd=str(project_root),
        check=True,
    )

    # should PASS: when calling entrypoint (with explicit `settings_dir`) from within the project or outside the project
    subprocess.run(
        [sys.executable, str(scripts_path / "run_with_explict_settings_dir.py")], cwd=str(project_root), check=True
    )
    with TemporaryDirectory() as tmp_dir:
        subprocess.run(
            [sys.executable, str(scripts_path / "run_with_explict_settings_dir.py")], cwd=str(tmp_dir), check=True
        )


if __name__ == "__main__":
    main()
