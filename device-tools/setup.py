from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="device_tools",
    version="0.0.1",
    author="Micha Gorelick",
    author_email="mynameisfiber@gmail.com",
    url="https://github.com/digital-witness-lab/whatup/device-tools/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=["device_tools"],
    package_dir={"device_tools": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    extras_require={
        "dev": [
            "flake8",
            "black",
            "isort",
            "pyright",
            "bump2version",
        ]
    },
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "device-tools = device_tools.cli:cli",
        ],
    },
)
