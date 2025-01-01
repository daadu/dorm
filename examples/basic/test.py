import subprocess
from pathlib import Path


def main():
    subprocess.run(["dorm", "test"], cwd=Path(__file__).parent.resolve(), check=True)


if __name__ == "__main__":
    main()
