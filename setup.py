from setuptools import setup

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='TEMInterface',
    version='0.1.0',
    description='A Python wrapper for the Thermo Fisher Scientific microscope scripting interface',
    long_description=long_description,
    url='https://github.com/mrl280/tem-scripting-package/',
    author='BASF TEM Laboratory',
    author_email='philipp.mueller @ basf.com',
    license='MIT',
    packages=['TEMInterface', 'uED'],
    python_requires='>=3.6',
    install_requires=['numpy',
                      'pandas',
                      'hyperspy',
                      'scipy',
                      'tifffile',
                      'opencv-python',
                      'comtypes',
                      'matplotlib',
                      ],
)
