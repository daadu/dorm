import os
import subprocess
from pathlib import Path

# Path to the `examples` directory
examples_dir = Path(__file__).parent.resolve() / ".." / "examples"

# Loop through subdirectories of `examples`
for subdir in os.listdir(examples_dir):
    subdir_path = os.path.join(examples_dir, subdir)
    if os.path.isdir(subdir_path):
        print(f"Running test in {subdir_path}")
        subprocess.run(["dorm", "test"], cwd=subdir_path)
