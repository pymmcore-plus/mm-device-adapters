from setuptools import setup
from setuptools.dist import Distribution


class BinaryDistribution(Distribution):
    def has_ext_modules(self) -> bool:
        return True  # Forces a platform-specific wheel


setup(distclass=BinaryDistribution)
