# Disclaimer

```pyTEM``` was developed for use on the BASF SE TEM laboratory's Talos F200i transmission electron microscope. 
 The authors provide no guarantee that the software will function as intended, either in part or in whole, on any 
 other microscope installation.

```pyTEM``` is available under the MIT license [here](/LICENSE).

# About

```pyTEM``` is a collection of Python modules enabling the *user-friendly* control of, and automated data acquisition 
on, Thermo Fisher Scientific and FEI microscopes from a pure Python environment.

Most ```pyTEM``` modules will require the Thermo Fisher Scientific / FEI scripting interface. While it may depend on 
 your installation, ```pyTEM``` will likely need to be run on a microscope control computer with the prerequisite 
 Thermo Fisher Scientific / FEI scripting interface installed and properly configured.

A list of available modules can be found [below](#modules).

# Modules

### Interface
This is BASF's TEM scripting interface. Bolted directly on top of a COM interface, ```Interface``` is just a Python
 wrapper for the Thermo Fisher Scientific / FEI scripting interface. Therefore, this ```pyTEM``` module requires that 
 the Thermo Fisher Scientific / FEI scripting interface is properly configured on your microscope installation. For 
 detailed information regarding your microscope's scripting capabilities, please refer to the documentation 
 accompanying your microscope or reach out to your microscope supplier.

This is not a complete interface in that it does not provide access to all the functionality of the underlying Thermo
 Fisher Scientific / FEI scripting interface. However, it provides access to all basic microscope functions as well
 as all those required by other ```pyTEM``` modules.

```Interface``` is much more *user-friendly* that the underlying Fisher Scientific / FEI scripting interface. To this 
 end, ```Interface``` functions return only built-in data types or instances of simple forward-facing classes, also 
 ```Interface``` provides many additional functions not directly available in the underlying interface 
 (some examples include ```print_available_magnifications()```, ```set_stage_position()```, and 
 ```print_camera_capabilities()```)

This module is a good starting place for those interested in learning how to control their microscope from a pure 
 Python environment.

##### Quick-start Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Get the current magnification
magnification = my_microscope.get_magnification()

# Shift the image 2 microns to the right, and 3 microns up
u = my_microscope.get_image_shift()
my_microscope.set_image_shift(x=u[0] + 2, y=u[1] + 3)
```

### MicroED
This is BASF's micro-crystal electron diffraction (MicroED) automated imaging script. MicroED allows fast,
 high resolution 3D structure determination of small chemical compounds and biological macromolecules, and ```MicroED``` 
 enables the automated acquisition of the required data series. More on micro-crystal electron diffraction 
 [here](https://en.wikipedia.org/wiki/Microcrystal_electron_diffraction).

```MicroED``` achieves automated image alignment by computing the image deviation during a preparatory tilt 
 sequence and then applying a compensatory image shift during the main acquisition sequence. Automated image alignment 
 is optional. While useful, automated alignment increases both sample exposure and experiment run-time 
 (although usually not significantly).

Since ```MicroED``` utilizes the ```Interface``` module, it requires that the Thermo Fisher Scientific / FEI scripting 
 interface is properly configured on your microscope installation.

##### Quick-start Example

```
from pyTEM.MicroED import MicroED

MicroED().run(verbose=True)
```

# Authorship

```pyTEM``` is developed and maintained by the TEM microscopy laboratory at BASF SE in Ludwigshafen, Germany. The 
 initial development was performed by RISE (Research Internships in Science and Engineering) Interns from North America. 
 More on the RISE program here: https://www.daad.de/rise/en/.

### *[Meagan Jennings](https://github.com/MaeJennings) (Sept - Dec 2021)*

#### Hometown: 
Baltimore, Maryland, USA

#### Contributions:

- Figured out how to interface with and control the microscope from a pure Python environment.
- developed ```TEMPackage```, the predecessor to ```pyTEM```'s ```Interface``` module. View the project as it existed at the time of Meagan's final commit [here](https://github.com/mrl280/pyTEM/tree/a91f30e11cc648c47cd2d977442754d2cda1e31c).
- Developed ```microED_Tilt_Series```, the predecessor to ```pyTEM```'s ```MicroED``` module. View [here](https://gitlab.roqs.basf.net/raa-os-apps/xem/microed-tem-python-script).
- Wrote the original TEM Scripting Guide, which can be found in [docs](/docs).

### *[Michael Luciuk](https://github.com/mrl280) (May - Aug 2022)*

#### Hometown: 
Saskatoon, Saskatchewan, Canada

#### Contributions:

- Refactored the original ```TEMPackage``` and ```microED_Tilt_Series``` into the ```Interface``` and ```MicroED```
 ```pyTEM``` modules we know and love today.

You can view the ```pyTEM``` project as it existed at the time of Michael's final commit [here](https://github.com/mrl280/pyTEM). # TODO: Update after Michael leaves
  
# Installation

Because ```pyTEM``` is often required on microscope control machines which lack internet connectivity, pyTEM is not 
 listed on the Python Package Index (PyPI), nor anywhere else. Rather, we provide a wheel file in [dist](/dist) and 
 [offline install instructions](#offline-install-instructions).

### Offline install instructions
##### On a system with internet access:
1. Download [requirements.txt](./requirements.txt)
2. Download the required dependencies with pip ```pip download -d ./pytem_dependencies -r requirements.txt```
3. Download the ```pyTEM``` wheel file from [dist](/dist).

Transfer ```requirements.txt```, the entire ```pytem_dependencies``` folder you just created, and the ```pyTEM``` wheel file to the offline machine.

##### On the offline system:
1. Install the required dependencies with pip: 
 ```pip install --no-index --find-links ./pytem_dependencies -r requirements.txt```
2. Install ```pyTEM``` itself with pip. Example: ```pip install pyTEM-0.1.0-py3-none-any.whl```


### If you need to build your own custom ```pyTEM``` wheel:
1. Install wheel with ```pip install wheel```, 
2. Download the whole ```pyTEM``` project directory,
3. Navigate to the pyTEM folder, 
4. Run ```setup.py``` with the ```bdist_wheel``` setuptools command. 
 Example: ```python setup.py bdist_wheel```

# Contribution & Contact Info

```pyTEM``` is developed and maintained by the TEM microscopy laboratory at BASF SE in Ludwigshafen, Germany. If you 
 have any questions about the ```pyTEM``` project or would like to contribute, please contact Philipp Müller at
 [philipp.mueller@basf.com](mailto:philipp.mueller@basf.com).

Issues can be reported [here](https://github.com/mrl280/pyTEM/issues)

# serailEM

As further explained [here](https://bio3d.colorado.edu/SerialEM/), SerialEM is a program that can acquire a variety of 
 data from electron microscopes, including tilt series for electron tomography, large image areas for 3-D reconstruction 
 from serial sections, and images for reconstruction of macromolecules by single-particle methods.

As further explained [here](https://sphinx-emdocs.readthedocs.io/en/latest/serialem-note-hidden-goodies.html#example-5-scripting-with-python), it is possible to call serialEM functions from Python scripts. Because SerialEM supports many sophisticated high-level 
 functions, it is likely that, in the future, pyTEM scripts will call serialEM functions to complete high-level 
 operations and tasks.

In order to use pyTEM scripts that invoke serialEM functions, you need to make sure that you have a properly configured 
 serialEM client running on the microscope control computer.
