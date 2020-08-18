#!/usr/bin/env python

import setuptools

readme = ''
with open('README.rst') as f:
    readme = f.read()
    
setuptools.setup(
    name="Py2DF",
    version="0.0.6",
    author="PgBiel, Skezza",
    description="A tool to convert python scripts to DF code templates.",
    long_description=readme,
    long_description_content_type="text/x-rst",
    install_requires=['nbtlib'],
    include_package_data=True,
    url="https://github.com/Py2DF/Py2DF",
    packages=setuptools.find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
)
