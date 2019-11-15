# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# from setuptools.command.install import install as _install
# To use a consistent encoding
from codecs import open
from os import path
import sys
import os

# Get the long description from the relevant file
# with open('README.rst', encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name='rpi2mqtt',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.2.0',

    # description='A Jupyter notebook extension to hide code, prompts and outputs.',
    # long_description=long_description,

    # The project's main homepage.
    url='https://github.com/kirbs-/rpi2mqtt',

    # Author details
    author='Chris Kirby',
    author_email='kirbycm@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],

    # What does your project relate to?
    keywords='raspberrypi mqtt GPIO',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    packages={'rpi2mqtt'},

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['dotmap', 'pyyaml', 'paho-mqtt', 'Adafruit_DHT'],

    entry_points={
        'console_scripts': ['rpi2mqtt=rpi2mqtt.event_loop:main']
    }
)
