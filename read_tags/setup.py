from setuptools import setup, find_packages
import os.path as path
import read_tags

setup(
    name='read_tags',
    version=read_tags.__version__,
    packages=find_packages(),
    install_requires=[
        'pydicom'
    ],
    dependency_links=[
        "git+git://github.com/pydicom/pydicom"
    ],
    long_description=open(path.join(path.dirname(__file__), 'README.txt')).read(),
)
