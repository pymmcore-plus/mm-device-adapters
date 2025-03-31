import sys

from setuptools import setup
from setuptools.command.egg_info import egg_info
from setuptools.dist import Distribution

sys.path.append(".")
from install import install


class CustomEggInfo(egg_info):
    def run(self):
        div, release = install()
        version = f"{div}.{release[:4]}.{release[4:6]}.{release[6:8]}"
        self.distribution.metadata.version = version
        return super().run()


class BinaryDistribution(Distribution):
    def has_ext_modules(self) -> bool:
        return True  # Forces a platform-specific wheel

    def get_command_class(self, command_name):
        if command_name == "egg_info":
            return CustomEggInfo
        return super().get_command_class(command_name)


setup(distclass=BinaryDistribution)
