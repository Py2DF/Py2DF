#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name="Py2DF",
    version="0.0.1",
    author="PgBiel, Skezza",
    author_email="author@example.com",
    description="A tool to convert python scripts to DF code templates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['nbtlib>=1.6.3,<2.0'],
    include_package_data=True,
    url="https://github.com/Py2DF/Py2DF",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
