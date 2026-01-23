# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

license_text = "Custom License (See LICENSE file)"
if os.path.exists("LICENSE"):
    with open("LICENSE", "r", encoding="utf-8") as f:
        license_text = f.read()

setup(
    name="tbcryptography",
    version="0.1.0",
    author="TebeeDeveloper",
    url="https://github.com/TebeeDeveloper/cryptography",

    license="Custom / Proprietary", 
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    package_data={
        'tbcryptography': [
            'bin/*.dll',
            'tbcomplex/*.py',
            'tbstandard/*.py'
        ],
    },
    include_package_data=True,

    python_requires=">=3.14",

    data_files=[('', ['LICENSE'])],
    
    classifiers=[
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",

        "License :: Other/Proprietary License", 
    ],
    
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)