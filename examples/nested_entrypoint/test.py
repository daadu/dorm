import subprocess
import sys
from pathlib import Path
from subprocess import SubprocessError
from tempfile import TemporaryDirectory

from django.core.management import color_style

_STYLE = color_style()


def main():
    project_root = Path(__file__).parent.resolve()
    scripts_path = project_root / "scripts"

    # should FAIL: when calling entrypoint (without explicit `settings_dir`) from the project-root
    error = None
    try:
        subprocess.run(
            [sys.executable, str(scripts_path / "run_without_explict_settings_dir.py")],
            cwd=str(scripts_path),
            check=True,
        )
    except SubprocessError as e:
        error = e
    assert isinstance(error, SubprocessError), "Should fail when calling dorm.setup(), not from the project root."
    print(_STYLE.WARNING("^^^ The above error is expected as part of the test."))

    # should PASS: when calling entrypoint (without explicit `settings_dir`) from the project root
    subprocess.run(
        [sys.executable, str(scripts_path / "run_without_explict_settings_dir.py")], cwd=str(project_root), check=True
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
