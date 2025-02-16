from setuptools import setup, find_packages

setup(
    name="claude-sync",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.25.0",
        "pyperclip>=1.8.0"
    ],
    entry_points={
        'console_scripts': [
            'claude-sync=claude_sync.cli.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A file sync utility for Claude AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/claude-sync",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
