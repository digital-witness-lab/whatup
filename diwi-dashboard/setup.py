from setuptools import setup, find_packages  # type: ignore

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="diwi-dashboard",
    version="0.0.1",
    author="Micha Gorelick",
    author_email="mynameisfiber@gmail.com",
    url="https://github.com/digital-witness-lab/whatsup/tree/diwi-dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages={"diwi_dashboard": "diwi_dashboard"},
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    extras_require={
        "dev": [
            "pur",
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
            "diwi-dashboard = diwi_dashboard.cli:main",
        ],
    },
)
