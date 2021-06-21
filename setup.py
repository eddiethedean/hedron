import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="hedron",
    version="0.0.5",
    description="A python package project for doing analysis on coordinates and clustering them.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/eddiethedean/hedron",
    author="Odos Matthews",
    author_email="odosmatthews@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["hedron"],
    include_package_data=True,
    install_requires=['pandas==1.2.4', 'PyGeodesy==21.6.9', 'py-staticmaps==0.4.0', 'range-key-dict==1.1.0'],
    entry_points={
        "console_scripts": [
            "hedron = hedron.cli:main",
        ]
    },
)