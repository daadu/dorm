import os
import subprocess

# Path to the `examples` directory
examples_dir = 'examples'

# Loop through subdirectories of `examples`
for subdir in os.listdir(examples_dir):
    subdir_path = os.path.join(examples_dir, subdir)
    if os.path.isdir(subdir_path):
        print(f"Running test in {subdir_path}")
        subprocess.run(['dorm', 'test'], cwd=subdir_path)
