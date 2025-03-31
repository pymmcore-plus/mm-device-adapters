import sys

from setuptools import setup
from setuptools.command.egg_info import egg_info
from setuptools.dist import Distribution

sys.path.append(".")
from install import install

div, release = install()
version = f"{div}.{release[:4]}.{release[4:6]}.{release[6:8]}"


class BinaryDistribution(Distribution):
    def has_ext_modules(self) -> bool:
        return True  # Forces a platform-specific wheel


setup(version=version, distclass=BinaryDistribution)
