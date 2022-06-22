from setuptools import setup

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='pyTEM',
    version='0.1.0',
    description='Automated transmission electron microscopy experiments in pure Python',
    long_description=long_description,
    url='https://github.com/mrl280/tem-scripting-package/',
    author='BASF TEM Laboratory',
    author_email='philipp.mueller@basf.com',
    keywords=['transmission electron microscopy', 'TEM', 'microscopy', 'electron microscopy',
              'micro-crystal electron diffraction', 'uED'],
    license='MIT',
    packages=['pyTEM'],
    python_requires='>=3.6',
    install_requires=['numpy',
                      'pandas',
                      'hyperspy',
                      'scipy',
                      'tifffile',
                      'comtypes',
                      'matplotlib',
                      'setuptools'
                      ],
)
