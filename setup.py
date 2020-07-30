#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

setup(
    name="Py2DF", # Replace with your own username
    version="0.0.2",
    author="PgBiel, Skezza",
    author_email="author@example.com",
    description="A tool to convert python scripts to DF code templates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url="https://github.com/Py2DF/Py2DF",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
