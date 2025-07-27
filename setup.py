"""Setup configuration for sysstatus package."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="sysstatus",
    version="0.1.0",
    author="Nasif Raihan",
    author_email="nasif.raihan78@gmail.com",
    description="A production-grade system information display tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nasifraihan/sysstatus",
    project_urls={
        "Bug Tracker": "https://github.com/nasifraihan/sysstatus/issues",
        "Documentation": "https://github.com/nasifraihan/sysstatus#readme",
        "Source Code": "https://github.com/nasifraihan/sysstatus",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sysstatus=sysstatus.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
