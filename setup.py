"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='pyTEM',
    version='0.1.0',
    description='Control and Automation of Transmission Electron Microscopes',
    long_description=long_description,
    url='https://github.com/mrl280/pyTEM',
    author='BASF TEM Laboratory',
    author_email='philipp.mueller@basf.com',
    keywords=['transmission electron microscopy', 'TEM', 'microscopy', 'electron microscopy',
              'micro-crystal electron diffraction', 'uED'],
    license='MIT',
    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test']),
    python_requires='>=3.8',
    install_requires=['numpy',
                      'pandas',
                      'hyperspy',
                      'scipy',
                      'tifffile',
                      'comtypes',
                      'matplotlib',
                      'setuptools',
                      'mrcfile',
                      'pathlib',
                      'Pillow',
                      ],
    entry_points='''
                [console_scripts]
                align_images=pyTEM_scripts.align_images:script_entry
                bulk_carbon_analysis=pyTEM_scripts.bulk_carbon_analysis:script_entry
                micro_ed=pyTEM.MicroED:script_entry
            ''',
    package_data={'': ['*.ico', '*.npy']},
    include_package_data=True,
)
