from setuptools import setup, find_packages

setup(
    name="monitoring-roll-machine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.6.0",
        "pyqtgraph>=0.13.3",
        "pyserial>=3.5",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "appdirs>=1.4.4",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "monitoring-roll-machine=monitoring.__main__:main",
        ],
    },
) 