from setuptools import setup, find_packages

setup(
    name="monitoring-roll-machine",
    version="1.2.5",
    description="Roll Machine Monitoring System with JSK3588 Protocol Support",
    author="Roll Machine Monitor Team",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.6.0",
        "pyqtgraph>=0.13.3",
        "pyserial>=3.5",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "appdirs>=1.4.4",
        "qrcode>=7.4.2",
        "Pillow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-qt>=4.2.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
            "pyinstaller>=5.0.0",
        ]
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "monitoring-roll-machine=monitoring.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "monitoring": ["*.json", "*.yaml", "*.yml"],
    },
) 