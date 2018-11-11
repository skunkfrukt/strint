# pylint: disable=missing-docstring
import setuptools
from strint import VERSION

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="strint",
    version=VERSION,
    author="Namida Aneskans",
    author_email="namida@skunkfrukt.se",
    description="A parser for numbers written as strings. Sometimes works.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/skunkfrukt/strint",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
)
