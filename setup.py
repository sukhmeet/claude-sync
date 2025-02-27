# Updated setup.py
from setuptools import setup, find_packages
import os
import shutil

# Ensure the data directory exists
os.makedirs('src/claude_sync/data', exist_ok=True)

# Look for the default syncignore file in multiple potential locations
possible_locations = [
    'src/claude_sync/default_syncignore.txt',  # Updated to match your actual filename
    '.default_syncignore.txt',
    'default_syncignore.txt',
    # Remove 'src/claude_sync/data/.default_syncignore.txt' from the search list
]

# Find the first file that exists
source_file = None
for location in possible_locations:
    if os.path.exists(location):
        source_file = location
        break

# If we found the file, copy it to the data directory
if source_file:
    # Copy the file to the package data directory
    print(f"Copying default syncignore file from {source_file} to src/claude_sync/data/.default_syncignore.txt")
    shutil.copy(source_file, 'src/claude_sync/data/.default_syncignore.txt')
    print(f"Copied default syncignore file from {source_file} to src/claude_sync/data/.default_syncignore.txt")
else:
    # Create a minimal version if we can't find the file
    print("Warning: Could not find default syncignore file. Creating a minimal version.")
    with open('src/claude_sync/data/.default_syncignore.txt', 'w') as f:
        f.write("""# Hidden files and directories
.*
!.gitignore
!.syncignore

# Version Control
.git/
.gitignore

# Build and Dependency Directories
__pycache__/
*.py[cod]

# Environment and Config
.env
.sync_config.json
""")

setup(
    name="claude-sync",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "claude_sync": ["data/.default_syncignore.txt"],
    },
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "pyperclip>=1.8.0",
        "curl_cffi>=0.5.0"  # Adding the missing dependency
    ],
    entry_points={
        'console_scripts': [
            'claude-sync=claude_sync.cli.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A file sync utility for Claude AI",
    long_description=open("README.md").read() if os.path.exists("README.md") else "A file sync utility for Claude AI",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/claude-sync",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)