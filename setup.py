"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(

    name="basicblockchains_ecc",  # Required
    version="1.0.1",  # Required
    description="A class for elliptic curve cryptography",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional
    url="https://github.com/BasicBlockchains/ECC",  # Optional
    author="Basic Blockchains",  # Optional
    author_email="basicblockchains@gmail.com",  # Optional
    classifiers=[  # Optional
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Other Audience",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="cryptography, elliptic_curve, ellipticcurve, elliptic_curve_cryptography, secp256k1, crypto",  # Optional
    package_dir={"": "src"},  # Optional
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.10",
    install_requires=["primefac"],  # Optional
    project_urls={  # Optional
        "Bug Reports": "https://github.com/BasicBlockchains/ECC/issues"
    },
)
