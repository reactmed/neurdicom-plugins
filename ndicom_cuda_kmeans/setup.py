from setuptools import setup, find_packages
import os.path as path

setup(
    name='cuda_kmeans',
    version='1.0',
    author='Roman Baigildin',
    author_email='egdeveloper@mail.ru',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Medical images processing :: Processing',
    ],
    url='http://github.com/reactmed/neurdicom-plugins',
    license='MIT',
    keywords='DICOM',
    packages=find_packages(),
    install_requires=[
        'dipy', 'numpy', 'pycuda'
    ],
    dependency_links=[
        "git+git://github.com/pydicom/pydicom"
    ],
    long_description=open(path.join(path.dirname(__file__), 'README.md')).read(),
)
