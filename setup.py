import hdmi

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    from pkgutil import walk_packages


    def _find_packages(path='.', prefix=''):
        yield prefix
        prefix += "."
        for _, name, is_package in walk_packages(path,
                                                 prefix,
                                                 onerror=lambda x: x):
            if is_package:
                yield name


    def find_packages():
        return list(_find_packages(hdmi.__path__, hdmi.__name__))

setup(name='hdmi',
      version=hdmi.__version__,
      install_requires=['myhdl >= 1.0.dev0'],
      description='Implementation of HDMI Source/Sink Modules in MyHDL',
      url='https://github.com/srivatsan-ramesh/HDMI-Source-Sink-Modules',
      author='srivatsan-ramesh',
      author_email='sriramesh4@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
