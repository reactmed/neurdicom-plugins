from setuptools import setup, find_packages, Extension
from os.path import join, dirname

# extension = Extension('demo', sources=['demo.cpp'])

setup(
    name='c_region_growing',
    version='1.0',
    packages=find_packages(),
    # ext_modules=[extension],
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    include_package_data=True,
    package_data={'': ['extension/build/Darwing/*.dylib']}
)