"""Setup configuration for s2doc"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version
version = {}
with open("s2doc/__version__.py") as f:
    exec(f.read(), version)

# Read README
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    long_description = "Convert YAML domain models to Markdown documentation"

setup(
    name="s2doc",
    version=version['__version__'],
    description="Convert YAML domain models to Markdown documentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Igor Music",
    author_email="igor.music@example.com",
    url="https://github.com/FreeSideNomad/s2doc",
    packages=find_packages(exclude=['tests', 'tests.*']),
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
        "graphviz>=0.20",
        "Pillow>=10.0",
        "lxml>=4.9",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        'console_scripts': [
            's2doc=s2doc.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="domain-driven-design ddd yaml markdown documentation domain-stories",
)
